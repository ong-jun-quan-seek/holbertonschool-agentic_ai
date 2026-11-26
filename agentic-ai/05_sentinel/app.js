const searchInput = document.querySelector("#issue-search");
const issueCards = [...document.querySelectorAll(".issue-card")];
const resultCount = document.querySelector("#result-count");
const emptyState = document.querySelector("#empty-state");

searchInput.addEventListener("input", () => {
  const query = searchInput.value.trim().toLowerCase();
  let visibleCount = 0;

  for (const card of issueCards) {
    const matches = card.dataset.search.includes(query);
    card.hidden = !matches;
    if (matches) {
      visibleCount += 1;
    }
  }

  resultCount.textContent = String(visibleCount);
  emptyState.hidden = visibleCount > 0;
});
