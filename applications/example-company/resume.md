---
name: Alex Example
contact: Brooklyn, NY · +1 555 555 5555 · alex@example.com
---

<!--
  Fictional example tailored resume. Shows the markdown conventions the
  build expects:

  - YAML frontmatter for the header (name + contact line).
  - `## Section` for top-level sections.
  - `### Title | Company, Location | Dates` for single-role entries
    (exactly two pipes — the build splits on them).
  - `### Company, Location` followed by `**Role** | Dates` paragraphs
    for multi-role entries at one employer.

  This is what a tailored output looks like — pruned from a fuller
  master.md and an angle file in `angles/`.
-->

## Career Summary

Senior full-stack engineer with seven years shipping production web
applications at small SaaS companies. Comfortable owning a feature
end-to-end — data model, API, frontend, rollout — and equally
comfortable investing in the developer experience that makes the next
feature ship faster.

## Relevant Experience

### Senior Software Engineer | Acme Project Tools, Remote | Mar 2020 – Present

- Owned the rebuild of the project-permissions system end-to-end — Postgres
  schema, TypeScript domain model, GraphQL API, and the React UI for the
  org admin pages. Shipped in two phases with no downtime and zero
  permission-leak regressions in the rollout window.
- Led the React → Next.js migration across the marketing site (~80
  routes), including App Router adoption and a phased rollout that
  preserved Core Web Vitals throughout.
- Cut p99 dashboard load from 4.2s to 800ms by moving filter aggregations
  from the client into a materialized Postgres view, behind a feature
  flag with measured rollout.
- Built the internal CI workflow that runs typecheck, lint, and the
  Playwright suite on every PR in under 4 minutes. Earlier the same
  checks ran sequentially in CI and serially in pre-commit; the
  parallelized version became the default and removed about 90% of
  "wait for CI" Slack messages.

### Software Engineer | Beta Health, NYC | Jul 2016 – Feb 2020

- Built the patient-intake form engine on React Hook Form and Zod,
  generating dynamic forms from a JSON config used by 30+ clinics.
- Owned the migration from a single PHP monolith to a Node/TypeScript
  API alongside it, including the strangler pattern, dual-write
  reconciliation, and the eventual decommission.

## Education

**Sample State University, ST** | B.S. Computer Science, 2015

## Additional Skills & Interests

TypeScript, React, Next.js, Node.js, Python, Postgres, GraphQL, AWS,
Docker. Daily Claude Code user for scripting and codebase navigation.
Occasional contributor to a couple of small open source TypeScript
libraries.
