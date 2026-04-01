/*
AI assistance note:
This file was scaffolded with the help of OpenAI Codex and then reviewed
and adjusted by the student for the final project submission.
*/

const issueForm = document.querySelector("#issue-form");
const issueList = document.querySelector("#issue-list");
const issueSummary = document.querySelector("#issue-summary");
const formMessage = document.querySelector("#form-message");
const filterButtons = document.querySelectorAll(".filter-button");

let currentFilter = "open";

async function fetchIssues(filter = "open") {
  issueSummary.textContent = "Loading issues...";

  const response = await fetch(`/api/issues?status=${encodeURIComponent(filter)}`);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Could not load issues.");
  }

  renderIssues(data.issues, filter);
}

function renderIssues(issues, filter) {
  currentFilter = filter;

  if (issues.length === 0) {
    issueSummary.textContent = `No ${filter} issues right now.`;
    issueList.innerHTML = `
      <article class="empty-state">
        <h3>Nothing to show</h3>
        <p>Try another filter, or submit the first issue for this list.</p>
      </article>
    `;
    return;
  }

  const openCount = issues.filter((issue) => issue.status === "open").length;
  issueSummary.textContent = `${issues.length} issue(s) shown, ${openCount} still open.`;

  issueList.innerHTML = issues
    .map(
      (issue) => `
        <article class="issue-card">
          <div class="issue-card-header">
            <div>
              <span class="status-pill ${issue.status}">${issue.status}</span>
              <h3>${escapeHtml(issue.title)}</h3>
            </div>
            ${issue.status === "open"
              ? `<button class="secondary-button" data-action="resolve" data-id="${issue.id}">Mark Resolved</button>`
              : ""}
          </div>
          <p class="meta-line">${escapeHtml(issue.category)} · ${escapeHtml(issue.location)}</p>
          <p>${escapeHtml(issue.details)}</p>
          <p class="meta-line">Created: ${formatDate(issue.created_at)}</p>
        </article>
      `
    )
    .join("");
}

async function submitIssue(event) {
  event.preventDefault();
  formMessage.textContent = "Submitting issue...";

  const formData = new FormData(issueForm);
  const payload = Object.fromEntries(formData.entries());

  const response = await fetch("/api/issues", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Could not submit the issue.");
  }

  issueForm.reset();
  formMessage.textContent = "Issue submitted successfully.";
  await fetchIssues(currentFilter);
}

async function resolveIssue(issueId) {
  const response = await fetch(`/api/issues/${issueId}/resolve`, {
    method: "POST",
  });
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Could not update the issue.");
  }

  await fetchIssues(currentFilter);
}

function setActiveFilter(button) {
  filterButtons.forEach((filterButton) => {
    filterButton.classList.toggle("active", filterButton === button);
  });
}

function formatDate(timestamp) {
  return new Date(timestamp).toLocaleString();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

issueForm.addEventListener("submit", async (event) => {
  try {
    await submitIssue(event);
  } catch (error) {
    formMessage.textContent = error.message;
  }
});

filterButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    try {
      setActiveFilter(button);
      await fetchIssues(button.dataset.filter);
    } catch (error) {
      issueSummary.textContent = error.message;
    }
  });
});

issueList.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }

  if (target.dataset.action !== "resolve") {
    return;
  }

  try {
    await resolveIssue(target.dataset.id);
  } catch (error) {
    issueSummary.textContent = error.message;
  }
});

fetchIssues(currentFilter).catch((error) => {
  issueSummary.textContent = error.message;
});
