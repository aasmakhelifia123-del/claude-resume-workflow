# Application tracker

A local SQLite-backed tracker for job applications in this repo. CLI + Flask web UI, both reading the same `tracker.db` at the repo root.

## Install

Only dependency is Flask. Pick one:

```bash
# Easiest: pipx for an isolated install
pipx install flask

# Or pip in a venv
python3 -m venv .venv && source .venv/bin/activate
pip install flask

# Or globally with pip --user
pip install --user flask
```

(Python's stdlib `sqlite3` handles the DB; no other deps.)

## First run

```bash
python3 tracker.py backfill         # scan applications/, create rows for the 22 existing folders
python3 tracker.py list             # confirm everything's there
python3 tracker.py serve            # → http://127.0.0.1:5050
```

## CLI

```
tracker.py serve [--port 5050]
tracker.py list [--status STATUS] [--search TEXT]
tracker.py show <slug>
tracker.py add <slug> --company "X" [--role Y --jd-url URL --salary "$150–180k" --location-type remote --status applied --date-applied 2026-05-17]
tracker.py update <slug> [--role Y --salary "..." --location-type hybrid --jd-url URL --status applied ...]
tracker.py jd <slug> [--file path.md | --text "..."]   # writes applications/<slug>/jd.md (stdin if no flag)
tracker.py mark-applied <slug>                          # used by build.sh
tracker.py status <slug> <new-status>
tracker.py interview <slug> --stage "Recruiter screen" [--date 2026-05-22T10:00] [--outcome pending] [--notes "..."]
tracker.py interview-update <round_id> [--stage S] [--date D] [--outcome O] [--notes N]
tracker.py note <slug> "appended note line"
tracker.py followup <slug> [--note "emailed recruiter"] [--snooze 7 | --dismiss]
tracker.py backfill
```

Statuses: `draft | applied | screening | interviewing | offer | rejected | withdrawn | ghosted`
Round outcomes: `pending | passed | failed | rescheduled | no_show`
Location types: `remote | hybrid | onsite | unknown`

## How it ties into `build.sh`

After `./build.sh applications/<slug>/resume.md` finishes, build.sh calls `python3 tracker.py mark-applied <slug>` which flips the row from `draft` → `applied` and stamps today's date (idempotent — subsequent builds are no-ops). If the row doesn't exist yet, it's lazily created with `status=applied`.

## How Claude updates it

The `CLAUDE.md` workflow tells Claude sessions to run the matching CLI command when you mention an interview, rejection, offer, etc. So in conversation:

> "Eve scheduled a recruiter screen for next Tuesday at 2pm"

Claude runs `python3 tracker.py interview eve --stage "Recruiter screen" --date 2026-05-26T14:00`.

## Data model

Two tables in `tracker.db` (committed to git — single-user repo, the data is the value):

- `applications` — one row per `applications/<slug>/` folder. Fields: slug, company, role, jd_url, salary_range, location_type, status, date_applied, notes.
- `interview_rounds` — many per application. Fields: stage, scheduled_at, outcome, notes, nudge_silenced_until.

When a round sits at `outcome=pending` for 7+ days, the detail page shows a "Time to follow up" callout. Logging a follow-up (web form or `tracker.py followup`) sets `nudge_silenced_until` — snoozes the nudge for N days, or dismisses it permanently — and optionally appends a dated note to the round.

The full JD lives on disk at `applications/<slug>/jd.md`, not in the DB — same shape as `resume.md` / `cover-letter.md`. The detail page renders it inline.

Source channel, recruiter contacts, etc. live in the free-form `notes` field.

## Backups

`tracker.db` is committed, so git history IS the backup. To dump as text:

```bash
sqlite3 tracker.db .dump > tracker.sql
```

## What's intentionally not in here

- No auth (localhost only, single user).
- No calendar/email integration (revisit later).
- No CSV import/export (`sqlite3` does this if ever needed).
- Source channel, recruiter contacts, salary — these live in the free-form notes field, not as structured columns.
