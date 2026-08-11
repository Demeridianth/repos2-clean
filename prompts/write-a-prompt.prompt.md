# Write a Prompt File

Create a new `.prompt.md` file for the `.github/prompts/` directory in this repo.

## Process

1. **Gather requirements** — ask me:
   - What task or workflow does this prompt cover?
   - What specific use cases should it handle?
   - Any reference materials or existing patterns to follow?

2. **Draft the prompt** — create a `.prompt.md` file with:
   - A clear `# Title`
   - A one-line description of what it does
   - Step-by-step workflow
   - Output format/template if applicable
   - Nexus-specific context where relevant

3. **Review with me** — present the draft and ask:
   - Does this cover your use cases?
   - Anything missing or unclear?
   - Should any section be more/less detailed?

## Prompt file guidelines

### Structure

```markdown
# Prompt Title

One-line description of what this prompt does.

## Process / Workflow

Step-by-step instructions.

## Output format

Template or example of expected output.

## Rules / Constraints

Guardrails and project-specific notes.
```

### Rules

- **Keep it under 100 lines** — if longer, split into a process with referenced files
- **Be specific about triggers** — when should someone use this prompt?
- **Include Nexus context** — reference Django apps, evals, LLM patterns where relevant
- **Use imperative mood** — "Explore the codebase" not "You should explore the codebase"
- **Include concrete examples** — show don't tell
- **No time-sensitive info** — prompts should stay valid across sprints

### Naming

- Use `kebab-case.prompt.md`
- Name should describe the action: `triage-issue`, `write-eval`, `review-pr`
- Save to `.github/prompts/`

After creating, remind me to test it in Copilot Chat by typing `#<prompt-name>` (for example, `#write-a-prompt`), omitting the `.prompt.md` suffix.
