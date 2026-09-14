#!/usr/bin/env bash
# Render a markdown resume to PDF via pandoc + typst.
#
#   ./build.sh path/to/resume.md  →  path/to/resume.pdf
#
# Styling lives in template/resume.typ. The build does a small post-process
# step that converts paragraphs of the form "**Title** | Dates" into a
# right-aligned two-column row via the #role-line() helper in the template.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$REPO/template/resume.typ"

if [[ $# -ne 1 ]]; then
  echo "usage: $0 path/to/resume.md" >&2
  exit 64
fi

input="$1"

if [[ ! -f "$input" ]]; then
  echo "error: input file not found: $input" >&2
  exit 66
fi

missing=()
for cmd in pandoc typst; do
  command -v "$cmd" >/dev/null 2>&1 || missing+=("$cmd")
done
if (( ${#missing[@]} > 0 )); then
  echo "error: missing required tool(s): ${missing[*]}" >&2
  echo "       install with: brew install pandoc typst" >&2
  exit 69
fi

if [[ ! -f "$TEMPLATE" ]]; then
  echo "error: template not found at $TEMPLATE" >&2
  exit 70
fi

output="${input%.md}.pdf"
tmp_typ="$(mktemp -t resumeXXXXXX)"
trap 'rm -f "$tmp_typ"' EXIT

# Cover letters get looser paragraph spacing — the template branches on `letter`.
pandoc_extra=()
case "$(basename "$input")" in
  cover-letter*.md|*-cover-letter.md)
    pandoc_extra+=(--metadata=letter:true)
    ;;
esac

pandoc "$input" \
  --from=markdown \
  --template="$TEMPLATE" \
  --wrap=none \
  --to=typst \
  ${pandoc_extra[@]+"${pandoc_extra[@]}"} \
  --output="$tmp_typ"

# Post-process pandoc's raw Typst output before Typst ever parses it:
#   1. "**Title** | Dates" paragraphs -> #role-line[Title][Dates]
#   2. strip the auto-generated pandoc label right after any level-3
#      heading that contains a pipe (meaningless once rule 3/4 turns that
#      heading into a plain function call) -- <...> allows any characters,
#      including umlauts, since pandoc keeps them in its auto-slugs
#   3. "Title | Org, Location | Dates" headings -> #entry-heading-3[...]
#      (must run before rule 4 -- a 3-part heading also matches rule 4's
#      pattern, but greedily at the wrong pipe)
#   4. "Title | Dates" headings -> #entry-heading[Title][Dates]
# All four rules avoid a Typst-side content-to-string() round trip that
# silently drops spaces adjacent to em-dashes/parens in heading titles
# (see GitHub issue #1) -- entry-heading/entry-heading-3 take rich content
# directly instead of reconstructing it from a flattened string.
#
# -i.bak (not -i '') for portability: GNU sed's -i takes only an optional
# *joined* suffix, so a separate '' argument gets misparsed as the sed
# script itself on GNU sed -- both GNU and BSD/macOS sed accept a joined
# non-empty suffix like -i.bak unambiguously.
sed -E -i.bak \
  -e 's~^#strong\[([^]]+)\] \| (.+)$~#role-line[\1][\2]~' \
  -e '/^=== .+ \| .+$/{N;s~\n<[^>]*>$~~}' \
  -e 's~^=== (.+) \| (.+) \| (.+)$~#entry-heading-3[\1][\2][\3]~' \
  -e 's~^=== (.+) \| (.+)$~#entry-heading[\1][\2]~' \
  "$tmp_typ"
rm -f "$tmp_typ.bak"

typst compile "$tmp_typ" "$output"

echo "wrote $output"

# If the input lives under applications/<slug>/, tell the tracker the
# application has been built — it'll flip draft → applied and stamp today's
# date (idempotent; no-op on subsequent builds).
if [[ "$input" == applications/*/resume.md || "$input" == applications/*/cover-letter.md \
   || "$input" == "$REPO"/applications/*/resume.md || "$input" == "$REPO"/applications/*/cover-letter.md ]]; then
  slug="$(basename "$(dirname "$input")")"
  if command -v python3 >/dev/null 2>&1; then
    python3 "$REPO/tracker.py" mark-applied "$slug" || \
      echo "warn: tracker.py mark-applied failed (continuing)" >&2
  fi
fi
