#!/usr/bin/env python3
"""Scrape a web page and save its title, meta description, headings,
paragraphs and links to JSON or CSV.

Uses only the Python standard library.

Usage:
    python3 scraper.py https://example.com -o example.json
    python3 scraper.py https://example.com -o example.csv --format csv
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
RETRYABLE_STATUS = {429, 500, 502, 503, 504}
MAX_BYTES = 10 * 1024 * 1024

log = logging.getLogger("scraper")


class ScrapeError(Exception):
    """Raised when a page cannot be fetched or parsed."""


class PageParser(HTMLParser):
    """Collect the title, meta description, headings, paragraphs and links."""

    HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
    SKIP = {"script", "style", "noscript", "template"}

    def __init__(self, base_url):
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
        attrs = dict(attrs)
        if tag in self.SKIP:
            self._skip_depth += 1
        elif tag == "meta" and (attrs.get("name") or "").lower() == "description":
            self.description = (attrs.get("content") or "").strip()
        elif tag == "a" and attrs.get("href"):
            self._link_href = urljoin(self.base_url, attrs["href"].strip())
            self._link_text = []
        if tag == "title" or tag in self.HEADINGS or tag == "p":
            self._capture = tag
            self._buffer = []

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self._skip_depth = max(0, self._skip_depth - 1)
        elif tag == "a" and self._link_href:
            href = self._link_href
            if urlparse(href).scheme in ("http", "https") and href not in self._seen_links:
                self._seen_links.add(href)
                self.links.append({"text": _clean(" ".join(self._link_text)), "url": href})
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


def _clean(text):
    return " ".join(text.split())


def fetch(url, timeout=10.0, retries=3, backoff=1.0):
    """Return the decoded HTML of url, retrying transient failures."""
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    for attempt in range(1, retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                content_type = response.headers.get_content_type()
                if content_type not in ("text/html", "application/xhtml+xml"):
                    raise ScrapeError(f"Unsupported content type: {content_type}")
                body = response.read(MAX_BYTES + 1)
                if len(body) > MAX_BYTES:
                    raise ScrapeError(f"Page exceeds {MAX_BYTES} bytes")
                charset = response.headers.get_content_charset() or "utf-8"
                return body.decode(charset, errors="replace")
        except HTTPError as exc:
            if exc.code not in RETRYABLE_STATUS or attempt == retries:
                raise ScrapeError(f"HTTP {exc.code} {exc.reason} for {url}") from exc
            reason = f"HTTP {exc.code}"
        except (URLError, socket.timeout, ConnectionError) as exc:
            if attempt == retries:
                raise ScrapeError(f"Network error for {url}: {exc}") from exc
            reason = str(getattr(exc, "reason", exc))
        delay = backoff * 2 ** (attempt - 1)
        log.warning("Attempt %d/%d failed (%s); retrying in %.1fs",
                    attempt, retries, reason, delay)
        time.sleep(delay)
    raise ScrapeError(f"Failed to fetch {url}")


def scrape(url, **fetch_kwargs):
    html = fetch(url, **fetch_kwargs)
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


def save(data, path, fmt):
    """Write atomically so a failure never leaves a half-written file."""
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            if fmt == "json":
                json.dump(data, handle, indent=2, ensure_ascii=False)
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
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("url", help="Page to scrape (http or https)")
    parser.add_argument("-o", "--output", default="scraped.json", help="Output file path")
    parser.add_argument("-f", "--format", choices=("json", "csv"),
                        help="Output format (default: inferred from extension, else json)")
    parser.add_argument("--timeout", type=float, default=10.0, help="Request timeout in seconds")
    parser.add_argument("--retries", type=int, default=3, help="Attempts for transient errors")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args(argv)
    if urlparse(args.url).scheme not in ("http", "https") or not urlparse(args.url).netloc:
        parser.error(f"Invalid URL: {args.url!r} (must start with http:// or https://)")
    if args.retries < 1:
        parser.error("--retries must be at least 1")
    if not args.format:
        args.format = "csv" if args.output.lower().endswith(".csv") else "json"
    return args


def main(argv=None):
    args = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s: %(message)s")
    try:
        data = scrape(args.url, timeout=args.timeout, retries=args.retries)
        save(data, args.output, args.format)
    except ScrapeError as exc:
        log.error(exc)
        return 1
    except OSError as exc:
        log.error("Could not write %s: %s", args.output, exc)
        return 2
    except KeyboardInterrupt:
        log.error("Interrupted")
        return 130
    log.info("Saved %d headings, %d paragraphs, %d links to %s",
             len(data["headings"]), len(data["paragraphs"]), len(data["links"]), args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
