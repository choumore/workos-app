# Generate Feed

After completing a daily debrief, generate the structured feed file that WorkOS will import.

## What to do

1. Collect all debrief output — work summary, decisions, follow-ups, Slack/email highlights
2. Format into the standard stride-feed markdown structure
3. Write to `stride-feed/YYYY-MM-DD.md` in the vault (use today's date)

## Output format

Write this exact structure to the vault:

```markdown
---
date: YYYY-MM-DD
type: stride-feed
---

## Work Summary
- [bullet list of work done, derived from debrief]

## Decisions Made
- [bullet list of decisions, if any]

## Follow-ups
- [ ] [actionable follow-up items — these become WorkOS todos]

## Slack Highlights
- #channel: summary of notable thread

## Email Highlights
- From Name: subject/summary
```

## Rules

- Follow-ups MUST use `- [ ]` checkbox format — WorkOS parses these as todos
- Keep follow-ups actionable and specific (not "think about X" but "draft X by Wednesday")
- Only include sections that have content — skip empty sections entirely
- Work Summary should be concise bullets, not paragraphs
- If the debrief had no Slack/email highlights, omit those sections
- Date in frontmatter must match the filename date
