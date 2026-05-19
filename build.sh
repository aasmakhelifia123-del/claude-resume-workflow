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
tmp_typ="$(mktemp -t resume-build).typ"
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

# Post-process "**Title** | Dates" paragraphs into right-aligned rows.
# (delimiter is `~` because the pattern contains both `|` and `/`)
sed -E -i '' 's~^#strong\[([^]]+)\] \| (.+)$~#role-line[\1][\2]~' "$tmp_typ"

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
