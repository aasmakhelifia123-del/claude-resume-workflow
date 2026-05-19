"""One-shot scan of applications/, populate the tracker DB.

Idempotent: skips slugs that already have a row. Best-effort metadata:
- company        prettified slug
- status         applied if any PDF present in the folder, else draft
- date_applied   null (PDF mtime isn't a reliable proxy for submission date)
- notes          inventory of what's on disk, for quick triage later
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from tracker import db


def prettify(slug: str) -> str:
    parts = slug.replace("_", "-").split("-")
    out = []
    for p in parts:
        if p.lower() in {"ai", "ml", "it", "qa", "trm", "c3"}:
            out.append(p.upper())
        else:
            out.append(p.capitalize())
    return " ".join(out)


def inventory(folder: Path) -> dict[str, bool]:
    return {
        "resume.md": (folder / "resume.md").exists(),
        "cover-letter.md": (folder / "cover-letter.md").exists(),
        "resume.pdf": (folder / "resume.pdf").exists(),
        "cover-letter.pdf": (folder / "cover-letter.pdf").exists(),
    }


def run() -> int:
    db.ensure_schema()
    today = date.today().isoformat()
    created = 0
    skipped = 0
    for folder in sorted(db.APPLICATIONS_DIR.iterdir()):
        if not folder.is_dir():
            continue
        slug = folder.name
        if db.get_application(slug) is not None:
            skipped += 1
            continue
        inv = inventory(folder)
        has_pdf = inv["resume.pdf"] or inv["cover-letter.pdf"]
        status = "applied" if has_pdf else "draft"
        inv_line = ", ".join(f"{k}={'yes' if v else 'no'}" for k, v in inv.items())
        notes = f"Backfilled {today}. Contents: {inv_line}"
        db.add_application(
            slug=slug,
            company=prettify(slug),
            status=status,
            notes=notes,
        )
        print(f"  + {slug:30} status={status}")
        created += 1
    print(f"\nBackfill complete: {created} created, {skipped} skipped (already present).")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
