# WorkOS — Career Operating System
## Session Context Document
*Use this to continue building in a new Claude session*

---

## What We Are Building

A **personal career operating system** called **WorkOS** — a standalone HTML file that runs in any browser. It is designed for a **Senior Product Designer** working toward promotion. The system automates self-documentation, makes work visible, tracks career progression against 7 promotion vectors, acts as a stateful career coach, and archives everything to a searchable knowledge base.

**Core principles:**
- Local-first — data lives in localStorage, synced via private GitHub Gist
- Human-confirmed — nothing posts or logs without user review and approval
- Evidence-driven — captures proof of growth as it happens
- Cross-device — works on desktop (localhost) and mobile (GitHub Pages)
- AI-augmented — Claude processes meetings, generates coaching, and powers career chat

---

## Current State (Updated April 2026)

**Version:** 3.0.0
**All original stages COMPLETE** plus Meeting Intelligence, Career Chat, MemPalace/Obsidian integration, unified todo system, visibility tracking, and stateful coaching.

**Repo:** [github.com/choumore/workos-app](https://github.com/choumore/workos-app) (public)
**GitHub Pages:** https://choumore.github.io/workos-app/workos.html
**Desktop access:** `http://localhost:8080/workos.html` (served via `python3 -m http.server 8080`)

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      USER'S BROWSER                           │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                    workos.html                        │    │
│  │                                                       │    │
│  │  ┌─────────┐ ┌────┐ ┌───┐ ┌──────┐ ┌─────┐ ┌─────┐ │    │
│  │  │Dashboard│ │Chat│ │Log│ │Briefs│ │Todos│ │Meet.│ │    │
│  │  └────┬────┘ └──┬─┘ └─┬─┘ └──┬───┘ └──┬──┘ └──┬──┘ │    │
│  │  ┌────┐ ┌──────┐                                     │    │
│  │  │Vis.│ │Contr.│  ┌──────┐                           │    │
│  │  └──┬─┘ └──┬───┘  │ ⚙Set │                           │    │
│  │     └──────┴──────┴──┬───┘                            │    │
│  │                      │                                │    │
│  │  ┌───────────────────▼──────────────────────────┐     │    │
│  │  │               localStorage                    │     │    │
│  │  │  entries[] meetings[] todos[] wins[]           │     │    │
│  │  │  weeklyBriefs[] contributions[] vectors[]      │     │    │
│  │  │  chatSessions[] coachingState{} settings{}     │     │    │
│  │  └──────┬──────────────┬────────────┬────────────┘     │    │
│  │         │              │            │                   │    │
│  │  ┌──────▼──────┐ ┌────▼─────┐ ┌────▼──────────┐       │    │
│  │  │ AI Engine   │ │ GitHub   │ │ MemPalace     │       │    │
│  │  │ (Claude API)│ │ Gist Sync│ │ Server :8091  │       │    │
│  │  └──────┬──────┘ └────┬─────┘ └────┬──────────┘       │    │
│  └─────────┼─────────────┼────────────┼──────────────────┘    │
│            │             │            │                        │
└────────────┼─────────────┼────────────┼────────────────────────┘
             │ HTTPS        │ HTTPS      │ HTTP
             ▼              ▼            ▼
    ┌──────────────┐ ┌──────────┐ ┌─────────────────┐
    │ AI Gateway   │ │ GitHub   │ │ Obsidian Vault  │
    │ (OpenAI-     │ │ Gist API │ │ (iCloud Drive)  │
    │  compatible) │ └──────────┘ └─────────────────┘
    └──────────────┘
```

---

## Tabs & Features

### 1. Dashboard (Home Screen)
- **Today's Focus** — Daily triage flow with drag-reorder (Inbox → Today → Tomorrow → Backlog)
- **Weekly Triage** — 3-step Monday flow: inbox review → week review → share plan
- **Vector Dashboard** — Per-vector evidence scores, trend arrows, time-range comparison (week/month/quarter/6mo)
- **Monthly & Quarterly Reflections** — Mandatory reflection prompts on calendar dates
- **Entry Nudges** — Prompts to write entries, generate briefs

### 2. Chat (Career Chat)
- **Multi-turn AI conversations** with full WorkOS state as context
- **Quick Prompts** — Pre-loaded questions ("What should I focus on?", "Generate promotion narrative", etc.)
- **@memory Trigger** — Queries MemPalace semantic search for deep historical context
- **Session History** — 30 archived sessions with resume capability
- **Save Insights** — Extract AI responses as coaching observations

### 3. Log (Daily Journal)
- **Entry Form** — Mood (6 emoji), energy (1-10), work done, reflection
- **Auto-fill** — Completed todos auto-populate work done
- **AI Coaching Notes** — Generated analysis per entry with patterns + action items
- **TL;DR Generation** — Summaries for work done, reflection, coaching
- **Humanize Toggle** — Rewrite AI output in first person
- **History View** — 52-week calendar with mood/energy dots, reverse-chronological entry list

### 4. Briefs
- **Weekly Briefs** — AI-generated patterns, wins detection (keep/dismiss), vector alignment, 1:1 prep
- **Humanize Toggle** — Rewrite in human voice
- **Meeting Prep** — Stakeholder profiles, tone selectors, generated talking points
- **Regenerate** — Re-run brief generation for any week

### 5. Todos (Unified Task System)
- **Buckets:** Inbox → Today → Next Day → This Week → Backlog → Done → Deleted
- **Triage Flow** — Blocking daily/weekly triage with keyboard shortcuts
- **Recurrence** — Daily/weekday/weekly/biweekly/monthly with edit menu
- **Follow-ups** — 3-depth chain (today/tomorrow/3 days/1 week)
- **Subtasks** — Nested todos with independent deadlines
- **Sources** — Meeting, Slack, Manual, Recurring, Subtask, Follow-up, AI Suggestion
- **Slack Integration** — `:workos:` emoji reactions sync as inbox items
- **Search** — Cross-bucket unified search with grouped results

### 6. Meetings (Meeting Intelligence)
- **9 Meeting Types** — 1:1, design review, standup, cross-functional, strategic, brainstorm, user research, hawkins, other
- **Transcript Import** — Drag-drop text, Tactiq paste, Google Calendar integration
- **Auto-Type Detection** — Classification from transcript + stakeholders
- **Insight Extraction** — Type-specific (feedback received, decisions, commitments, opportunities, etc.)
- **Transcript Cleaning** — Claude removes filler words, consolidates speech (chunked for long transcripts, truncation detection with raw fallback)
- **Action Item Extraction** — Auto-converted to todos with dedup
- **Meeting Prep** — Recurring meeting series, stakeholder context, tone profiles
- **Post-Meeting Synthesis** — Reflections + AI consolidation
- **Gist Backup** — Raw transcripts stored in private GitHub Gist (via Zapier from Tactiq)

### 7. Visibility
- **Role Templates** — Designer (WAYWO, Draftboard, Crits, Hawkins) or custom
- **Activity Types** — Custom with vector mapping and staleness thresholds
- **Organic Surfacing** — AI detects visibility opportunities from meetings/journal
- **Draft Generation** — Weekly Top 3, WAYWO, Draftboard, Hawkins posts
- **Reach × Evidence Matrix** — Team/Function/Cross-functional/Organization scope tracking

### 8. Contributions
- **Design system contribution tracking** (Hawkins)
- **Slack paste import** with AI auto-categorization
- **Dashboard** — Category cards, pie chart, activity timeline, filtering
- **Categories:** bug-report, feature-request, design-feedback, component-request, documentation, discussion

### 9. Settings
- **Profile** — Name, role, promotion notes (with AI vector extraction), Insights Discovery profile
- **Feature Toggles** — Meetings, Todos, Visibility, Contributions
- **AI Coaching** — Gateway URL, project ID, API key, model (Sonnet/Opus), usage tracking
- **Slack** — OAuth token, webhook, reactions sync
- **Cloud Sync** — GitHub Gist with auto-push (2s debounce), auto-pull on load
- **Google Calendar** — OAuth Client ID, event fetching
- **MemPalace + Obsidian** — Server URL, vault path, auto-export toggle, test/mine/export buttons
- **Meetings Gist** — Separate gist for Tactiq transcript backup (Zapier integration)
- **Data** — Export/Import JSON, restore from hourly backups

---

## MemPalace + Obsidian Integration (v3.0.0)

**Companion server:** `workos-mempalace-server/server.py` (FastAPI on port 8091)
**Obsidian vault:** `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/WorkOS/`

- **Auto-export** — Entries, meetings (with cleaned transcripts), and briefs as markdown with YAML frontmatter
- **Content hash tracking** — Skips unchanged files on re-export
- **Transcript cleaning** — Claude polishes raw transcripts (filler removal, speech consolidation). Chunked for long transcripts (40K char chunks at speaker boundaries). Falls back to raw if cleaned output < 60% of input (API truncation detection)
- **@memory in Chat** — Semantic search via MemPalace CLI for deep historical context
- **Export formats:** entries/YYYY-MM-DD.md, meetings/YYYY-MM-DD-slug-id.md, briefs/id.md

---

## Meeting Transcript Pipeline

```
Tactiq (Google Meet) → Zapier → GitHub Gist (raw JSON)
                                      │
                    ┌─────────────────▼──────────────────┐
                    │         WorkOS (browser)             │
                    │  Fetch → Process → Extract Insights  │
                    │  Clean transcript → Export to Obsidian│
                    └─────────────────┬──────────────────┘
                                      │
                              MemPalace Server
                                      │
                              Obsidian Vault
                          (iCloud / searchable)
```

- Raw transcripts stored in private Gist (36 meetings as of April 2026)
- Transcripts stripped from localStorage after processing (5MB limit)
- Fetch button restores transcripts from Gist on demand
- Large gist files (>1MB) require individual fetch via `raw_url` (CORS workaround needed from localhost)

---

## 7 Promotion Vectors

1. **Communication** — How you articulate ideas and influence through words
2. **Craft** — Quality of design output and attention to detail
3. **Technical Depth** — Understanding of engineering, systems, constraints
4. **Cross-team Influence** — Impact beyond your immediate team
5. **Strategy** — Connecting work to business outcomes and long-term vision
6. **Leadership** — Mentoring, facilitating, enabling others
7. **Collaboration** — Working effectively across functions and roles

Vectors are extracted from promotion notes, mapped to wins/evidence, scored per time period, and tracked on the Dashboard.

---

## Data Model (localStorage)

```js
state = {
  settings: {
    name, role, baseUrl, projectId, apiKey, model,
    slackWebhook, slackToken, promotionNotes,
    insightsProfile, insightsProfileRaw,
    ghToken, ghGistId,              // cloud sync (never synced)
    googleClientId,                 // calendar OAuth
    meetingsGistId,                 // Tactiq transcript backup gist
    mempalaceServerUrl,             // default: http://localhost:8091
    obsidianVaultPath,              // absolute path to vault
    obsidianExportEnabled,          // auto-export toggle
    features: { contributions, visibility, meetings, todos }
  },
  entries: [{ id, date, dayOfWeek, workDone, reflection, mood, energy,
              planTomorrow, aiReflection, tldr, isMonday, isFriday, weeklyRetro }],
  wins: [{ id, date, sourceWeek, sourceBriefId, description, impact, vectors[], status }],
  weeklyBriefs: [{ id, weekOf, patterns, vectorCheckIn, winsDetected[], oneOnOnePrep,
                   humanizedSections{} }],
  meetings: [{ id, date, title, participants, type, transcript, summary,
               actionItems, notes, insights{}, feedback, link, duration }],
  meetingPreps: [{ id, meetingTitle, preps[], syntheses[] }],
  todos: [{ id, text, priority, source, sourceId, sourceTitle, parentId,
            scheduledFor, triagedAt, recurrence, starred, done, deleted }],
  contributions: [{ id, date, channel, text, category, component, status, slackLink }],
  visibilityActivities: [{ id, date, type, description, vectors[], audience }],
  vectors: {},                      // computed vector scores
  coachingState: { activeObservations[], resolvedObservations[] },
  monthlyReflections: {},           // keyed by YYYY-MM
  quarterlyReflections: {},         // keyed by YYYY-QN
  chatSessions: [],                 // max 30, with message history
  apiUsageLog: [],                  // token counts, costs per feature
  intentions: {},                   // legacy, keyed by Monday date
  dayPriorities: {},
  customVisibilityTypes: [],
  pendingVisibility: [],
  slackSyncedTs: [],
  triageProgress: {},
  deletedMeetingIds: []
}
```

---

## Cloud Sync

- **Primary:** Private GitHub Gist stores full app state (tokens excluded via whitelist)
- **Auto-push** on every save (2-second debounce)
- **Auto-pull** on page load
- **Merge safety:** Latest-wins by ID/key — never straight overwrites (critical: cloud sync merges, doesn't replace)
- **Meetings Gist:** Separate gist for raw Tactiq transcripts (Zapier pushes, WorkOS pulls)
- **Backup:** 3-layer system — hourly deep backups, pre-sync snapshots, rolling localStorage backup

---

## Version History

| Version | Date | Highlights |
|---------|------|-----------|
| 3.0.0 | 2026-04-08 | MemPalace + Obsidian integration, transcript cleaning, @memory chat, auto-export |
| 2.6.0 | 2026-04-07 | Unified todo input, triage shortcuts, 3-layer backup, sync merge safety |
| 2.5.0 | 2026-03-30 | Career Chat tab, Humanize AI, Slack emoji-to-todo, API Usage Tracker |
| 2.4.0 | 2026-03-26 | Card-based weekly triage, dynamic font sizing, weekly plan HTML |
| 2.3.0 | 2026-03-23 | Reschedule dropdown, todo search, subtask deadlines, Deleted tab |
| 2.2.0 | 2026-03-20 | Visibility Phase 4, open loops from todos |
| 2.1.0 | 2026-03-17 | Recurring todos, inline editing, star items, mobile triage |
| 2.0.0 | 2026-03-14 | Unified todo system, daily focus triage, Monday triage flow |
| 1.0.0 | 2026-03-01 | Initial release: journal, coaching, briefs, wins, contributions, sync |

---

## User Profile

- **Role:** Senior Product Designer at Netflix (Content Business Products XD)
- **Primary devices:** Mac (desktop, localhost), iPhone (GitHub Pages)
- **Primary tools:** Chrome, Slack, Figma, Terminal (Claude Code), Cursor
- **GitHub:** choumore
- **Technical level:** Non-code / low-code (builds with AI assistance)
- **AI text preference:** All AI-drafted text must use first person voice

---

## How to Continue in a New Session

The code (`workos.html`) is the source of truth. Claude memory files track preferences and roadmap status. To continue building:

1. Open Claude Code in the WorkOS directory
2. Describe what you want to build or change
3. Claude reads the code, memory, and this context file as needed

No separate build spec needed — the app is the spec.

---

*Document updated: April 2026 | System version: 3.0.0*
