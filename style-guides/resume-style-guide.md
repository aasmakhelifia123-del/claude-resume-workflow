# Resume Style Guide

This guide captures voice, framing, and editorial preferences for tailoring
resumes from your master doc. It's prompt context for Claude — not read by
the build — so edit it freely to encode your own preferences.

There's a **`## Personalize`** section at the bottom. Fill that in once and
the rest of the guide does its job across every tailored version.

---

## Who the resume is for

The reader is usually a hiring manager or recruiter spending **30–60
seconds** on first pass. The resume's job is to **get you in the door.**
You can speak to anything once you're in the conversation — so lean toward
the strongest *honest* framing, not the safest one.

---

## Voice and tone

**Aim for:**

- Concrete nouns and verbs. Name the tool, the scale, the outcome.
- Confident without being performative. "Ran," "owned," "built," "scoped"
  — not "leveraged," "spearheaded," "drove transformation."
- Specific detail that earns its place. Numbers, tool names, concrete
  examples. "Cut p99 load from 4.2s to 800ms" beats "improved
  performance." "30+ clinics" beats "many customers."
- Bias toward work that compounds — systems that keep working, tooling
  that speeds up the next person, anything that makes the same problem
  easier to solve next time.

**Avoid:**

- Corporate filler: "ensuring minimal disruption to user productivity,"
  "leveraged synergies," "drove transformation," "spearheaded initiatives."
- Empty intensifiers: "comprehensive," "robust," "seamless," "world-class."
- Stacked nouns without a verb doing work. "Engineer with broad experience
  spanning…" belongs nowhere.
- Buzzword bingo. If the JD asks for a keyword, work it in only where a
  matching bullet already exists; don't bolt it on.

---

## Calibration — important

Most people **downplay their own accomplishments.** When tailoring, lean
toward the confident honest framing, not the timid one.

- If you co-owned something and were a real driver, "led" is often
  defensible.
- If you built something from scratch, "built" beats "contributed to."
- If you administered a tool end-to-end, "owned" beats "supported."
- Round numbers up to the strongest *honest* version ("30+" not 28;
  "~80 routes" not "around 80").

**The line that doesn't move:** don't invent tools, projects, metrics, or
outcomes. Confidence is in framing, not fabrication.

---

## Title conventions

Some companies use titles that don't map cleanly to what hiring managers
elsewhere expect. If your real title is unusual — internal level naming
("Member of Technical Staff III"), industry-specific grades (finance's
AVP/VP, government GS-grades, academic ranks), or a casual title that
undersells the work ("Engineer" for staff-level work) — translate it
into parens after the real title. Do this only for the most senior role
on the resume; the rest can stand on their own.

Example: `**Member of Technical Staff III (Staff Engineer)**` reads as
one title at the previous employer and as something recognizable
everywhere else.

---

## What to include vs. cut when tailoring

**Always in** (regardless of role):

- Career Summary, with the middle sentence adjusted to match the role's
  focus
- Your most-recent or highest-leverage role block, in full
- Education
- Certifications that this audience will recognize

**Cut or downplay depending on the role:**

- Migration / one-time-project bullets if the target already runs the
  thing you migrated to — pivot to ongoing-ownership framing instead.
- Infrastructure or DevX bullets if the role is purely feature-shipping.
- People-management or mentorship bullets if the role is strictly IC and
  small-team.
- Bullets in a tech stack the company doesn't use, unless they
  demonstrate transferable judgment (e.g. a Rails-shop role still values
  a thoughtful Postgres bullet from a Django job).
- Side-of-desk work that diluted the headline accomplishment.

The principle: every bullet should *earn its place* for *this specific
role*. Better short and on-target than long and diluted.

---

## Structural conventions

- **Section order:** Career Summary → Relevant Experience → Certifications
  → Education → Additional Skills & Interests. Adjust the last three to
  match what's actually impressive for your background.
- **Em-dashes:** use sparingly. A few well-placed ones are fine; em-dashes
  as default punctuation make the prose feel mannered. Prefer commas,
  periods, colons, or parentheses; reserve em-dashes for genuine contrast
  or aside. Not multiple per bullet.
- **Length:** one page is the goal, just over is acceptable. Prefer
  cutting whole bullets to making individual bullets weaker.

---

## Bullet patterns that work

Each of these exemplifies the voice:

- **"Owned the rebuild of the project-permissions system end-to-end —
  Postgres schema, TypeScript domain model, GraphQL API, and the React
  UI for the org admin pages. Shipped in two phases with no downtime."**
  Pattern: concrete verb + scope + tech stack across layers + outcome.

- **"Cut p99 dashboard load from 4.2s to 800ms by moving filter
  aggregations from the client into a materialized Postgres view,
  behind a feature flag with measured rollout."**
  Pattern: quantified before/after + the technical choice that made it
  work + the discipline that kept it safe.

- **"Scoped and prototyped a real-time collaboration layer on top of
  Yjs — including the conflict-resolution model and the auth-aware
  presence channel — to inform the team's eventual buy-vs-build
  decision."**
  Pattern: honest verb for work that didn't fully ship + what it
  produced + the "why."

- **"Built the internal CI workflow that runs typecheck, lint, and the
  Playwright suite on every PR in under 4 minutes — replacing a
  sequential pipeline that gated everyone's PRs for 15+ minutes."**
  Pattern: what you built + what it did + the before-state that gives
  the after-state weight.

---

## Tailoring checklist

When producing a tailored version:

1. Read the JD and identify the requirements that matter most. Match
   keywords where you legitimately can.
2. Select bullets from `master.md` that address those requirements.
3. Cut bullets that don't fit the role's focus — even if they're strong.
4. Adjust the Career Summary's middle sentence to reflect what the target
   role actually cares about.
5. Flag anything uncertain before finalizing — honesty calibration
   questions, tool names to double-check, claims that feel borderline.

---

## Personalize

Edit the sections below to encode *your* voice. Once filled in, Claude
will apply them every time it tailors a resume for you.

### Target roles

What kinds of roles are you applying to? IC vs. management track? Any
industries or company sizes you're aiming at or avoiding?

> Example: senior full-stack engineering, IC track, small-to-mid SaaS,
> ideally at companies where the product surface area is the moat.

(Replace with yours.)

### Words you don't sound like

A list of words or phrases that read as *not your voice* — usually
consultant-speak or generic LinkedIn-bio energy. Claude should reach for
plainer alternatives.

> Example: "sharp" / "sharpest", "messy", "cleanly" / "land it cleanly".

(Replace with yours.)

### Always-in bullets

Specific bullets from your master that should be in every tailored version
unless they're actively contradicted by the JD.

> Example: the permissions-system rebuild, the long-tenure framing, the
> open-source contributions line.

(Replace with yours.)

### Calibration notes

Anything specific about how *you* tend to undersell or oversell. If you
have a recurring tic ("I always say 'helped with' when I drove the thing"),
write it down so Claude can correct it.

> Example: I tend to downplay project ownership. If I "co-owned"
> something and was a real driver, "led" is often the right word.

(Replace with yours.)
