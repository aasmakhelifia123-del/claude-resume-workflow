---
name: Alex Example
contact: Brooklyn, NY · +1 555 555 5555 · alex@example.com
---

<!--
  Worked example angle file. The fictional persona "Alex Example" is a
  senior full-stack engineer with ~7 years at small SaaS companies.

  This file is meant to show what an angle looks like once it's filled in
  — a pruned and reordered view of your master, leading with the framing
  that matters for one kind of role.

  Delete or replace this file once you have your own angles in place.
  See angles/README.md and the project root README for guidance on
  generating angles from your own master.md.
-->

## Career Summary

Senior full-stack engineer with seven years shipping production web
applications at small SaaS companies. Comfortable owning a feature
end-to-end — data model, API, frontend, rollout — and equally comfortable
investing in the developer experience that makes the next feature ship
faster.

## Relevant Experience

### Senior Software Engineer | Acme Project Tools, Remote | Mar 2020 – Present

#### Product engineering

- Owned the rebuild of the project-permissions system end-to-end —
  Postgres schema, TypeScript domain model, GraphQL API, and the React
  UI for the org admin pages. Shipped in two phases with no downtime.
- Designed and shipped the in-app notifications system from scratch,
  including the Postgres-backed event queue, the WebSocket fan-out, and
  the React inbox UI. Used by 70% of active accounts within three weeks
  of GA.
- Led the React → Next.js migration across the marketing site (~80
  routes), including App Router adoption and a phased rollout that
  preserved Core Web Vitals throughout.
- Partnered with design on the dashboard redesign — turned a static
  Figma flow into a working prototype in two days that became the basis
  for the final shipped product.

#### Performance & data

- Cut p99 dashboard load from 4.2s to 800ms by moving filter aggregations
  from the client into a materialized Postgres view, behind a feature
  flag with measured rollout.
- Owned the move from REST to GraphQL for the internal API, including
  the schema design, the gradual migration of clients, and the eventual
  REST decommission.
- Designed the analytics event pipeline (Snowplow → Postgres → dbt) that
  product uses for feature-adoption reporting.

#### Developer experience

- Built the internal CI workflow that runs typecheck, lint, and the
  Playwright suite on every PR in under 4 minutes. Earlier the same
  checks ran sequentially in CI and serially in pre-commit; the
  parallelized version became the default and removed about 90% of
  "wait for CI" Slack messages.
- Wrote the test-data factory layer used by every integration test in
  the repo. New tests can stand up a fully-populated workspace in two
  lines instead of forty.
- Mentored two junior engineers through their first year, including
  code-review norms, pair-programming hours, and a small internal
  reading group on production debugging.

### Software Engineer | Beta Health, NYC | Jul 2016 – Feb 2020

- Built the patient-intake form engine on React Hook Form and Zod,
  generating dynamic forms from a JSON config used by 30+ clinics.
- Owned the migration from a single PHP monolith to a Node/TypeScript
  API alongside it, including the strangler pattern, dual-write
  reconciliation, and the eventual decommission of the legacy stack.
- Built the on-call playbook and the dashboards behind it; ran the
  internal training that brought every engineer on the team through
  their first on-call rotation.

## Education

**Sample State University, ST** | B.S. Computer Science, 2015

## Additional Skills & Interests

TypeScript, React, Next.js, Node.js, Python, Postgres, GraphQL, AWS,
Docker, Playwright. Daily Claude Code user for scripting and codebase
navigation. Occasional contributor to a couple of small open source
TypeScript libraries.
