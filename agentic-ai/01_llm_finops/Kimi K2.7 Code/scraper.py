#!/usr/bin/env python3
"""Scrape a web page and save its structured text data to a JSON or CSV file.

This script uses only the Python standard library. It fetches a page with a
polite User-Agent, extracts the title, meta description, headings, paragraphs
and links, and writes them to disk with basic retry logic and comprehensive
error handling.

Usage:
    python3 scraper.py https://example.com
    python3 scraper.py https://example.com -o data.json
    python3 scraper.py https://example.com -o data.csv --format csv
"""

import argparse
import csv
import json
import logging
import os
import socket
import sys
import tempfile
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

USER_AGENT = "Mozilla/5.0 (compatible; SimpleScraper/1.0)"
MAX_BYTES = 10 * 1024 * 1024  # 10 MiB
RETRYABLE_STATUS = {429, 500, 502, 503, 504}
DEFAULT_TIMEOUT = 10.0
DEFAULT_RETRIES = 3

log = logging.getLogger("scraper")


class ScrapeError(Exception):
    """Raised when a page cannot be fetched or parsed successfully."""


class PageParser(HTMLParser):
    """Parse HTML and collect title, description, headings, paragraphs, links."""

    HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
    SKIP = {"script", "style", "noscript", "template"}

    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.title = ""
        self.description = ""
        self.headings = []
        self.paragraphs = []
        self.links = []
        self._seen_links = set()
        self._capture = None
        self._buffer = []
        self._skip_depth = 0
        self._link_href = None
        self._link_text = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip_depth += 1
            return

        attributes = dict(attrs)

        if tag == "meta" and attributes.get("name", "").lower() == "description":
            self.description = (attributes.get("content") or "").strip()

        if tag == "a" and attributes.get("href"):
            self._link_href = urljoin(self.base_url, attributes["href"].strip())
            self._link_text = []

        if tag == "title" or tag in self.HEADINGS or tag == "p":
            self._capture = tag
            self._buffer = []

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self._skip_depth = max(0, self._skip_depth - 1)
            return

        if tag == "a" and self._link_href:
            href = self._link_href
            parsed = urlparse(href)
            if parsed.scheme in ("http", "https") and href not in self._seen_links:
                self._seen_links.add(href)
                self.links.append(
                    {"text": _clean(" ".join(self._link_text)), "url": href}
                )
            self._link_href = None

        if tag == self._capture:
            text = _clean(" ".join(self._buffer))
            if text:
                if tag == "title":
                    self.title = text
                elif tag == "p":
                    self.paragraphs.append(text)
                else:
                    self.headings.append({"level": tag, "text": text})
            self._capture = None

    def handle_data(self, data):
        if self._skip_depth:
            return
        if self._capture:
            self._buffer.append(data)
        if self._link_href:
            self._link_text.append(data)

    def error(self, message):
        # html.parser calls this for some malformed input; turn it into an exception.
        raise ScrapeError(f"HTML parse error: {message}")


def _clean(text: str) -> str:
    """Collapse whitespace in text."""
    return " ".join(text.split())


def fetch(url: str, timeout: float, retries: int, backoff: float) -> str:
    """Fetch the page at ``url`` and return its decoded HTML.

    Retries transient HTTP errors (429, 5xx) and network-level errors with
    exponential backoff. Raises ``ScrapeError`` for fatal problems.
    """
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        },
    )

    last_reason = None
    for attempt in range(1, retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                content_type = response.headers.get_content_type()
                if content_type not in ("text/html", "application/xhtml+xml"):
                    raise ScrapeError(
                        f"Unsupported content type for {url}: {content_type}"
                    )

                body = response.read(MAX_BYTES + 1)
                if len(body) > MAX_BYTES:
                    raise ScrapeError(
                        f"Response body for {url} exceeds {MAX_BYTES} bytes"
                    )

                charset = response.headers.get_content_charset() or "utf-8"
                return body.decode(charset, errors="replace")

        except HTTPError as exc:
            if exc.code not in RETRYABLE_STATUS or attempt == retries:
                raise ScrapeError(f"HTTP {exc.code} {exc.reason} for {url}") from exc
            last_reason = f"HTTP {exc.code}"

        except (URLError, socket.timeout, ConnectionError, TimeoutError) as exc:
            if attempt == retries:
                reason = getattr(exc, "reason", exc)
                raise ScrapeError(f"Network error for {url}: {reason}") from exc
            last_reason = str(getattr(exc, "reason", exc))

        delay = backoff * 2 ** (attempt - 1)
        log.warning(
            "Attempt %d/%d failed (%s); retrying in %.1fs",
            attempt,
            retries,
            last_reason,
            delay,
        )
        time.sleep(delay)

    raise ScrapeError(f"Failed to fetch {url} after {retries} attempts")


def scrape(url: str, timeout: float = DEFAULT_TIMEOUT, retries: int = DEFAULT_RETRIES):
    """Scrape ``url`` and return a structured dictionary of extracted data."""
    html = fetch(url, timeout=timeout, retries=retries, backoff=1.0)
    parser = PageParser(url)

    try:
        parser.feed(html)
        parser.close()
    except Exception as exc:
        raise ScrapeError(f"Failed to parse HTML from {url}: {exc}") from exc

    return {
        "url": url,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "title": parser.title,
        "description": parser.description,
        "headings": parser.headings,
        "paragraphs": parser.paragraphs,
        "links": parser.links,
    }


def save(data: dict, path: str, fmt: str):
    """Write ``data`` to ``path`` atomically in the requested format.

    Uses a temporary file + ``os.replace`` so a crash never leaves a
    half-written output file.
    """
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            if fmt == "json":
                json.dump(data, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
            else:
                writer = csv.writer(handle)
                writer.writerow(["type", "level", "text", "url"])
                writer.writerow(["title", "", data["title"], data["url"]])
                writer.writerow(["description", "", data["description"], ""])
                for heading in data["headings"]:
                    writer.writerow(["heading", heading["level"], heading["text"], ""])
                for paragraph in data["paragraphs"]:
                    writer.writerow(["paragraph", "", paragraph, ""])
                for link in data["links"]:
                    writer.writerow(["link", "", link["text"], link["url"]])
        os.replace(tmp_path, path)
    except BaseException:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n  python3 scraper.py https://example.com -o out.json",
    )
    parser.add_argument("url", help="URL to scrape (must start with http:// or https://)")
    parser.add_argument(
        "-o", "--output", default="scraped.json", help="Output file path (default: scraped.json)"
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=("json", "csv"),
        help="Output format (default: inferred from output extension, else json)",
    )
    parser.add_argument(
        "--timeout", type=float, default=DEFAULT_TIMEOUT, help="Request timeout in seconds"
    )
    parser.add_argument(
        "--retries", type=int, default=DEFAULT_RETRIES, help="Number of retries for transient errors"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args(argv)

    parsed_url = urlparse(args.url)
    if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
        parser.error(f"Invalid URL: {args.url!r} (must start with http:// or https://)")

    if args.timeout <= 0:
        parser.error("--timeout must be greater than 0")
    if args.retries < 0:
        parser.error("--retries must be non-negative")

    if not args.format:
        args.format = "csv" if args.output.lower().endswith(".csv") else "json"

    return args


def main(argv=None):
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        data = scrape(args.url, timeout=args.timeout, retries=args.retries)
        save(data, args.output, args.format)
    except ScrapeError as exc:
        log.error(exc)
        return 1
    except OSError as exc:
        log.error("Could not write to %s: %s", args.output, exc)
        return 2
    except KeyboardInterrupt:
        log.error("Interrupted by user")
        return 130

    log.info(
        "Saved %d heading(s), %d paragraph(s), %d link(s) to %s",
        len(data["headings"]),
        len(data["paragraphs"]),
        len(data["links"]),
        args.output,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
