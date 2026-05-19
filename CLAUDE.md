# Resume tailoring workflow — instructions for Claude

This repo is a personal resume-tailoring system: a markdown master resume,
a set of pre-tailored "angles" for different role types, voice and style
guides, a story bank, a Typst PDF pipeline, and a local SQLite tracker.

When opened in this repo, you're being asked to do one of two things:

1. **First-run setup** — the user is new to this repo and `master.md`
   still has its template scaffolding. Help them turn their existing
   resume into a proper master, then generate angles and (optionally) a
   story bank. See [First-run setup](#first-run-setup) below.

2. **Tailor a resume for a specific job** — the user has filled in their
   master and has pasted a JD. Read the JD, pick the closest angle,
   cross-reference master, prune, rewrite per the style guides, write
   the file, register the application in the tracker, and **stop for
   review before building the PDF**. See
   [Tailoring workflow](#tailoring-workflow) below.

## The pieces

- [master.md](master.md) — the kitchen-sink master resume. Always the
  ground truth for facts (titles, dates, accomplishments). Everything
  else is a filtered view of this.
- [angles/](angles/) — pre-tailored angle templates that live as starting
  points for different *kinds* of roles. Each is a trimmed/reframed
  version of master, opinionated for a particular pitch. Any `angles/*.md`
  is a valid starting point. See [angles/README.md](angles/README.md).
- [style-guides/](style-guides/) — voice, framing, and tailoring rules.
  **Always read these before producing any tailored resume or letter.**
  - `resume-style-guide.md` / `tailoring-prompt.md` — resume process & rules
  - `cover-letter-style-guide.md` / `cover-letter-prompt.md` — cover letter rules
  - `story-bank.md` — concrete situation → action → outcome stories.
    Primary source for cover-letter paragraph 2. Also useful for resumes
    when a bullet would land harder told as a story.
- [template/resume.typ](template/resume.typ) — Typst styling for the
  PDF. Don't touch this unless asked.
- [applications/](applications/) — one folder per company. The tailored
  resume for a given application lives at
  `applications/<company-slug>/resume.md`. Cover letter at
  `cover-letter.md` alongside. JD body at `jd.md`.
- [build.sh](build.sh) — `./build.sh path/to/resume.md` → PDF next to it.
  Also calls `python3 tracker.py mark-applied <slug>` after a successful
  build of a file under `applications/<slug>/`.
- [tracker.py](tracker.py) + [tracker/](tracker/) — local SQLite-backed
  application tracker. CLI + Flask UI. See
  [README-tracker.md](README-tracker.md).

## First-run setup

Trigger: `master.md` still contains its template scaffolding
(placeholder name, empty sections), or the user says something like
"help me set up this repo" / "help me set up my resume."

Walk the user through these steps. Pause for input where indicated.

1. **Collect their existing resume.** Ask them to paste their current
   resume as text, share a PDF, or describe their career in detail if
   they don't have one yet. Don't write anything until you have enough
   material.
2. **Confirm their name, contact line, and target role types.** The
   contact line goes in the YAML header of `master.md` and every angle
   file. Target role types determine which angle files you'll generate.
3. **Fill in `master.md`.** Migrate every role, every accomplishment,
   every credential into the structure the existing template already
   has. This is the *kitchen-sink* doc — include everything they might
   ever want to mention, even things they're not currently emphasizing.
   Group bullets into thematic subsections per role.
4. **Personalize the style guides.** Open
   `style-guides/resume-style-guide.md` and
   `style-guides/cover-letter-style-guide.md`. Each has a `## Personalize`
   section near the bottom. Ask the user the questions in those sections
   and fill in their answers.
5. **Generate angle files.** Based on the role types the user identified,
   create 3–4 files under `angles/` (e.g. `fullstack.md`,
   `staff-eng.md`, `frontend.md`). Each one is a pruned and reframed
   view of master, leading with what the target hiring manager for
   *that* role-type cares about. The repo ships with a worked
   [`fullstack-example.md`](angles/fullstack-example.md) — use it as a
   structural reference, then delete or replace it once the user's
   real angles are in place.
6. **(Optional) Bootstrap the story bank.** Ask whether they want to
   build out [`style-guides/story-bank.md`](style-guides/story-bank.md)
   now or later. If now, walk them through 3–4 headline stories
   (situation → action → outcome → when to use) and 4–6 shorter detail
   stories. If later, leave the file as-is and they can run a follow-up
   session.
7. **Hand off.** Tell them they're set up and explain how to start a
   real application: open a Claude Code session, paste a JD, say
   "tailor for this."

## Tailoring workflow

Trigger: the user has pasted a JD or pointed at one, and `master.md` is
populated.

1. **Decide the angle.** Pick the `angles/*.md` whose framing best
   matches the role. If none fit, start from `master.md`. State your
   pick and why, in one line.
2. **Cross-reference master.** Scan `master.md` for accomplishments the
   chosen angle skipped that are specifically relevant to this JD. Pull
   them in. Don't pad with generic items.
3. **Prune.** Drop anything in the angle that this JD doesn't care
   about. Better short and on-target than long and diluted.
4. **Rewrite per the style guides.** Apply the rules in
   `style-guides/tailoring-prompt.md` and `resume-style-guide.md`. Pull
   anecdotes and framings from `story-bank.md` when a bullet would land
   harder told as a story.
5. **Write the file.** Put it at `applications/<company-slug>/resume.md`.
   Create the folder if needed. Use lowercase kebab-case for the slug.
6. **Save the JD.** Write the verbatim JD body (strip recruiter intros,
   "we're hiring!" preamble, and sign-offs) to
   `applications/<company-slug>/jd.md`. If the JD was given as a URL
   only, drop the URL in there with a one-line note.
7. **Register the application in the tracker.** Run:
   ```
   python3 tracker.py add <slug> --company "X" --role "Y" \
       --jd-url <url> --salary "$150–180k" --location-type remote
   ```
   Pull `--role`, `--salary` (if stated), `--location-type`
   (`remote | hybrid | onsite | unknown`), and `--jd-url` straight from
   the JD. If a row already exists, use `update` instead of `add`. If
   the JD doesn't state salary, omit the flag — don't guess.
8. **Stop and hand off for review.** Tell the user the draft is ready
   and point them at the file path. Do **not** run `./build.sh` yet.
   Wait for the user to approve the build or come back with edits. The
   user often wants to read and tweak the markdown before committing to
   a PDF.
9. **Build (only after approval).** Once given the green light, run
   `./build.sh applications/<company-slug>/resume.md` and confirm the
   PDF was produced. Flag if it ran over 2 pages.

## Cover letters

Cover letters work the same way as resumes: tailored draft at
`applications/<company-slug>/cover-letter.md`, follow
`style-guides/cover-letter-prompt.md` and `cover-letter-style-guide.md`.
Same review checkpoint before building — write the markdown, stop, wait
for approval, then build with `./build.sh`.

## Tracker — keep it in sync

The repo has a SQLite tracker (`tracker.db`) for application state. When
the user mentions an event that changes status — "I got an interview at
Acme next Tuesday", "Beta rejected me", "Gamma sent an offer" — update
the tracker via the CLI. Don't just acknowledge verbally.

Common commands:

```
python3 tracker.py add <slug> --company "X" --role "Y" --jd-url <url> \
        --salary "$150–180k" --location-type remote
python3 tracker.py update <slug> --salary "$160–190k" --role "Senior Engineer"
python3 tracker.py status <slug> <new-status>
python3 tracker.py interview <slug> --stage "Recruiter screen" --date 2026-05-22T10:00
python3 tracker.py interview-update <round_id> --outcome passed --notes "..."
python3 tracker.py note <slug> "freeform note"          # appends
python3 tracker.py followup <slug> --note "emailed recruiter" --snooze 7
python3 tracker.py jd <slug> --file applications/<slug>/jd.md
python3 tracker.py list
python3 tracker.py show <slug>
```

Statuses: `draft | applied | screening | interviewing | offer | rejected | withdrawn | ghosted`.
Round outcomes: `pending | passed | failed | rescheduled | no_show`.
Location types: `remote | hybrid | onsite | unknown`.

Field-population rules:

- **Role / salary / location_type:** pull from the JD. If a JD mention is
  ambiguous ("flexible work environment" — is that remote or hybrid?),
  use `unknown` rather than guessing.
- **JD file:** any time the user pastes a fresh JD or updated JD for an
  application, rewrite `applications/<slug>/jd.md`. Don't append —
  replace.
- **Manual fallback:** if the user adds an application by hand (just
  makes a folder and starts editing resume.md), `build.sh` will
  lazy-create the row with `status=applied` and no other fields. The
  detail page in the web UI has form inputs for everything; they can
  fill them in there.

Don't touch `tracker.db` directly with raw SQL or by editing the file —
always go through `tracker.py`.

## Markdown conventions the template expects

```markdown
---
name: Your Name
contact: City, ST · +1 555 555 5555 · you@example.com
---

## Section heading

### Company, Location          (multi-role: company as level-3 heading)

**Role 1** | Dates 1            (each role on its own paragraph;
                                 build.sh right-aligns the dates)
**Role 2** | Dates 2

### Title | Org, Location | Dates   (single-role alternative: 3-part pipe)

- Bullet point
- Another bullet
```

The `**Role** | Dates` paragraph pattern is a real convention the build
relies on — preserve the literal `|` separator and the bold on the title
side. Don't substitute em-dashes or commas for the pipe.

## What not to do

- **Don't edit `master.md` based on a JD.** Master is the long-term
  store of truth; tailored resumes live in `applications/`.
- **Don't invent accomplishments.** If it's not in master or the story
  bank, ask before adding it.
- **Don't change `template/resume.typ`** as part of tailoring work.
  Visual iteration is a separate conversation.
- **Don't push past 2 pages** without naming the tradeoff. Three pages
  is a signal to cut, not to ship.
