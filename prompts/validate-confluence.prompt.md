# Validate Confluence Page

Review a Confluence documentation page from the `confluence_docs/pages/` directory from two perspectives: a junior developer onboarding onto Nexus, and a senior developer checking for accuracy and completeness.

## Process

### 1. Read the page

Read the specified file from `confluence_docs/pages/`. If no file is specified, ask which page to review.

### 2. Junior Developer Review

Read the page as if you're a new developer joining the Nexus team. Flag:

- **Jargon without explanation** — terms that assume prior context (e.g. "Kong gateway", "Phoenix tracing", "ground truth") without defining them or linking to a definition
- **Missing prerequisites** — what do I need installed/configured/access to before following this?
- **Gaps in instructions** — steps that skip over non-obvious actions ("configure the settings" — which settings? where?)
- **Assumed knowledge** — references to internal systems, repos, or processes without context
- **Broken flow** — does the page read top-to-bottom or does it jump around?
- **Missing examples** — concepts explained abstractly that need a concrete example

Output as a numbered list of issues, each with:
- **Line/section** — where the issue is
- **Problem** — what's confusing
- **Suggestion** — how to fix it

### 3. Senior Developer Review

Read the page as an experienced Nexus developer. Flag:

- **Inaccuracies** — does this match the actual codebase? Cross-reference with the code.
- **Stale information** — references to files, settings, or patterns that no longer exist
- **Missing context** — important caveats, edge cases, or gotchas that aren't mentioned
- **Incomplete coverage** — significant aspects of the topic that aren't documented
- **Contradictions** — does this page contradict other Confluence pages or `.github/copilot-instructions.md`?
- **Security concerns** — secrets, endpoints, or internal URLs that shouldn't be in docs

For each issue found, cross-reference against the actual codebase to confirm.

### 4. Summary

Produce a final summary:

```markdown
## Page: [filename]

### Overall Assessment
[Good / Needs Work / Needs Rewrite] — one sentence why.

### Junior Dev Issues (onboarding friction)
1. [issue]
2. [issue]

### Senior Dev Issues (accuracy & completeness)
1. [issue]
2. [issue]

### Quick Wins
- [Small fixes that would immediately improve the page]

### Recommended Actions
- [ ] [Specific action items, ordered by impact]
```

## Tips

- Compare instructions in the doc against actual file paths and code in the repo
- Check if referenced Django management commands actually exist
- Verify any settings names against `viiv/settings.py`
- Check if linked pages in `confluence_manifest.json` still exist
