# Angles

An **angle** is a pre-tailored, opinionated version of your master resume
aimed at a specific *kind* of role. When a new job description comes in,
the first decision in the tailoring workflow is **which angle fits best**
— Claude starts from that file, cross-references the master for anything
the angle missed, prunes what doesn't fit the JD, and writes the result
to `applications/<company-slug>/resume.md`.

Angles save you from re-deciding the same framing questions every time.
A platform-engineering JD and an IT-operations JD ask for very different
versions of the same career — different ordering, different emphasis,
sometimes different summary entirely. An angle bakes that decision in
once.

## Suggested workflow

You **don't have to write these by hand**. Once you've filled in
`master.md` (see the first-run guide in the project root README), open
Claude Code in this directory and say something like:

> Read my `master.md` and the style guides. Generate 3–4 angle files in
> `angles/` covering the kinds of roles I'm targeting: `[role type 1]`,
> `[role type 2]`, `[role type 3]`. Each one should be a pruned and
> reordered view of master that leads with the framing those hiring
> managers care about.

Claude will draft them. Read each, tweak in your voice, and you're set.

## File naming

Use lowercase, kebab-case, descriptive of the role *family* — not a
specific company. Good examples:

- `platform-infra.md`
- `frontend.md`
- `staff-eng.md`
- `data-platform.md`
- `it-ops.md`

Anything ending in `.md` inside `angles/` is treated as a valid starting
point by the tailoring workflow described in [`../CLAUDE.md`](../CLAUDE.md).

## File structure

Each angle is just a markdown file with the same conventions the build
expects (see the root [README](../README.md) for the markdown layout).
[`fullstack-example.md`](fullstack-example.md) in this directory is a
worked example you can use as a structural reference — then delete or
replace it with your own.
