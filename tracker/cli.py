"""CLI for the tracker. Invoked via the `tracker.py` shim at the repo root.

This is the joint interface used by build.sh, by Claude sessions, and by
the human. The Flask web app is just a viewing/editing convenience over
the same underlying database.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from . import db

_UPDATABLE_FIELDS = (
    "company", "role", "jd_url", "salary_range", "location_type",
    "status", "date_applied", "notes",
)


def _print_table(rows: list, columns: list[tuple[str, str]]) -> None:
    """Render rows as a fixed-width ASCII table to stdout.

    columns is a list of (key, header) tuples.
    """
    if not rows:
        print("(no rows)")
        return
    keys = [k for k, _ in columns]
    headers = [h for _, h in columns]
    widths = [len(h) for h in headers]
    cells: list[list[str]] = []
    for row in rows:
        line = []
        for i, key in enumerate(keys):
            val = "" if row[key] is None else str(row[key])
            line.append(val)
            widths[i] = max(widths[i], len(val))
        cells.append(line)
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*("-" * w for w in widths)))
    for line in cells:
        print(fmt.format(*line))


# --- commands ------------------------------------------------------------

def cmd_serve(args: argparse.Namespace) -> int:
    from . import app as flask_app
    flask_app.run_dev(host=args.host, port=args.port)
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    rows = db.list_applications(status=args.status, search=args.search)
    enriched = []
    for row in rows:
        last = db.last_round(row["slug"])
        d = dict(row)
        d["last_round"] = (
            f"{last['stage']} ({last['outcome']})" if last else ""
        )
        enriched.append(d)
    _print_table(
        enriched,
        [
            ("slug", "slug"),
            ("company", "company"),
            ("role", "role"),
            ("salary_range", "salary"),
            ("location_type", "loc"),
            ("status", "status"),
            ("date_applied", "applied"),
            ("last_round", "last round"),
        ],
    )
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    row = db.get_application(args.slug)
    if row is None:
        print(f"no such application: {args.slug}", file=sys.stderr)
        return 1
    for k in row.keys():
        print(f"{k:>14}: {row[k]}")
    rounds = db.get_rounds(args.slug)
    if rounds:
        print("\ninterview rounds:")
        _print_table(
            rounds,
            [
                ("id", "id"),
                ("stage", "stage"),
                ("scheduled_at", "scheduled"),
                ("outcome", "outcome"),
                ("notes", "notes"),
            ],
        )
    assets = db.folder_assets(args.slug)
    print(f"\nfolder: applications/{args.slug}/")
    for k, v in assets.items():
        print(f"  {k}: {'yes' if v else 'no'}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    db.add_application(
        slug=args.slug,
        company=args.company,
        role=args.role,
        jd_url=args.jd_url,
        salary_range=args.salary_range,
        location_type=args.location_type,
        status=args.status,
        date_applied=args.date_applied,
        notes=args.notes,
    )
    print(f"added {args.slug}")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    if db.get_application(args.slug) is None:
        print(f"no such application: {args.slug}", file=sys.stderr)
        return 1
    fields = {k: getattr(args, k) for k in _UPDATABLE_FIELDS if getattr(args, k) is not None}
    if not fields:
        print("nothing to update — pass at least one --field value", file=sys.stderr)
        return 2
    db.update_application(args.slug, **fields)
    print(f"{args.slug}: updated {', '.join(fields)}")
    return 0


def cmd_jd(args: argparse.Namespace) -> int:
    if db.get_application(args.slug) is None:
        print(f"no such application: {args.slug}", file=sys.stderr)
        return 1
    if args.file:
        text = Path(args.file).read_text()
    elif args.text is not None:
        text = args.text
    else:
        if sys.stdin.isatty():
            print("paste the JD, then Ctrl-D:", file=sys.stderr)
        text = sys.stdin.read()
    if not text.strip():
        print("empty JD; nothing written", file=sys.stderr)
        return 2
    db.write_jd(args.slug, text)
    print(f"{args.slug}: wrote {db.jd_path(args.slug).relative_to(db.REPO_ROOT)}")
    return 0


def cmd_mark_applied(args: argparse.Namespace) -> int:
    # Lazy-create the row if the folder exists but the DB doesn't know about it
    # yet (covers the case where someone made the folder by hand and ran build.sh
    # before backfilling).
    if db.get_application(args.slug) is None:
        folder = db.folder_for(args.slug)
        if not folder.is_dir():
            print(f"no such application or folder: {args.slug}", file=sys.stderr)
            return 1
        company = args.slug.replace("-", " ").title()
        db.add_application(
            slug=args.slug,
            company=company,
            status="applied",
            date_applied=date.today().isoformat(),
        )
        print(f"created {args.slug} (status=applied, date_applied=today)")
        return 0
    changed = db.mark_applied(args.slug)
    if changed:
        print(f"{args.slug}: marked applied")
    else:
        print(f"{args.slug}: already past draft, no change")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    if db.get_application(args.slug) is None:
        print(f"no such application: {args.slug}", file=sys.stderr)
        return 1
    db.update_application(args.slug, status=args.new_status)
    print(f"{args.slug}: status → {args.new_status}")
    return 0


def cmd_interview(args: argparse.Namespace) -> int:
    if db.get_application(args.slug) is None:
        print(f"no such application: {args.slug}", file=sys.stderr)
        return 1
    rid = db.add_round(
        slug=args.slug,
        stage=args.stage,
        scheduled_at=args.date,
        outcome=args.outcome,
        notes=args.notes,
    )
    print(f"{args.slug}: added round #{rid} — {args.stage}")
    return 0


def cmd_interview_update(args: argparse.Namespace) -> int:
    if db.get_round(args.round_id) is None:
        print(f"no such round: {args.round_id}", file=sys.stderr)
        return 1
    db.update_round(
        round_id=args.round_id,
        stage=args.stage,
        scheduled_at=args.date,
        outcome=args.outcome,
        notes=args.notes,
    )
    print(f"updated round #{args.round_id}")
    return 0


def cmd_note(args: argparse.Namespace) -> int:
    if db.get_application(args.slug) is None:
        print(f"no such application: {args.slug}", file=sys.stderr)
        return 1
    db.append_note(args.slug, args.text)
    print(f"{args.slug}: note appended")
    return 0


def cmd_followup(args: argparse.Namespace) -> int:
    if db.get_application(args.slug) is None:
        print(f"no such application: {args.slug}", file=sys.stderr)
        return 1
    last = db.last_round(args.slug)
    if last is None:
        print(f"{args.slug}: no interview rounds — nothing to follow up on", file=sys.stderr)
        return 1
    if last["outcome"] != "pending":
        print(
            f"{args.slug}: latest round ({last['stage']}) is {last['outcome']}, not pending",
            file=sys.stderr,
        )
        return 1
    db.log_followup(
        last["id"],
        note=args.note,
        snooze_days=args.snooze,
        dismiss=args.dismiss,
    )
    if args.dismiss:
        print(f"{args.slug}: follow-up nudge dismissed on round #{last['id']}")
    else:
        days = args.snooze if args.snooze is not None else db.FOLLOW_UP_DAYS
        print(f"{args.slug}: follow-up logged on round #{last['id']} (snoozed {days}d)")
    return 0


def cmd_backfill(_: argparse.Namespace) -> int:
    from scripts.backfill import run as backfill_run
    return backfill_run()


# --- parser --------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tracker", description="Job application tracker")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("serve", help="run the local web UI")
    sp.add_argument("--host", default="127.0.0.1")
    sp.add_argument("--port", type=int, default=5050)
    sp.set_defaults(func=cmd_serve)

    sp = sub.add_parser("list", help="list applications as a table")
    sp.add_argument("--status", choices=db.STATUSES)
    sp.add_argument("--search", help="substring match on company/slug/role")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("show", help="dump one application + its rounds")
    sp.add_argument("slug")
    sp.set_defaults(func=cmd_show)

    sp = sub.add_parser("add", help="create a new application row")
    sp.add_argument("slug")
    sp.add_argument("--company", required=True)
    sp.add_argument("--role")
    sp.add_argument("--jd-url", dest="jd_url")
    sp.add_argument("--salary", "--salary-range", dest="salary_range")
    sp.add_argument("--location-type", dest="location_type", choices=db.LOCATION_TYPES)
    sp.add_argument("--status", choices=db.STATUSES, default="draft")
    sp.add_argument("--date-applied", dest="date_applied")
    sp.add_argument("--notes")
    sp.set_defaults(func=cmd_add)

    sp = sub.add_parser("update", help="update one or more fields on an existing row")
    sp.add_argument("slug")
    sp.add_argument("--company")
    sp.add_argument("--role")
    sp.add_argument("--jd-url", dest="jd_url")
    sp.add_argument("--salary", "--salary-range", dest="salary_range")
    sp.add_argument("--location-type", dest="location_type", choices=db.LOCATION_TYPES)
    sp.add_argument("--status", choices=db.STATUSES)
    sp.add_argument("--date-applied", dest="date_applied")
    sp.add_argument("--notes", help="REPLACES the notes field; use `note` to append")
    sp.set_defaults(func=cmd_update)

    sp = sub.add_parser("jd", help="save the JD text to applications/<slug>/jd.md")
    sp.add_argument("slug")
    sp.add_argument("--file", help="read JD from this file path")
    sp.add_argument("--text", help="JD text as a single arg (rarely used; prefer stdin)")
    sp.set_defaults(func=cmd_jd)

    sp = sub.add_parser("mark-applied", help="flip a draft row to applied")
    sp.add_argument("slug")
    sp.set_defaults(func=cmd_mark_applied)

    sp = sub.add_parser("status", help="change application status")
    sp.add_argument("slug")
    sp.add_argument("new_status", choices=db.STATUSES)
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("interview", help="record a new interview round")
    sp.add_argument("slug")
    sp.add_argument("--stage", required=True)
    sp.add_argument("--date", help="ISO datetime, e.g. 2026-05-22T10:00")
    sp.add_argument("--outcome", choices=db.INTERVIEW_OUTCOMES)
    sp.add_argument("--notes")
    sp.set_defaults(func=cmd_interview)

    sp = sub.add_parser("interview-update", help="update an existing round")
    sp.add_argument("round_id", type=int)
    sp.add_argument("--stage")
    sp.add_argument("--date")
    sp.add_argument("--outcome", choices=db.INTERVIEW_OUTCOMES)
    sp.add_argument("--notes")
    sp.set_defaults(func=cmd_interview_update)

    sp = sub.add_parser("note", help="append a timestamped line to notes")
    sp.add_argument("slug")
    sp.add_argument("text")
    sp.set_defaults(func=cmd_note)

    sp = sub.add_parser("followup", help="log a follow-up on the latest pending round")
    sp.add_argument("slug")
    sp.add_argument("--note", help="optional text appended to the round's notes")
    snooze_group = sp.add_mutually_exclusive_group()
    snooze_group.add_argument("--snooze", type=int, metavar="DAYS",
                              help=f"silence the nudge for N days (default {db.FOLLOW_UP_DAYS})")
    snooze_group.add_argument("--dismiss", action="store_true",
                              help="silence the nudge until something else changes")
    sp.set_defaults(func=cmd_followup)

    sp = sub.add_parser("backfill", help="scan applications/, populate DB")
    sp.set_defaults(func=cmd_backfill)

    return p


def main(argv: list[str] | None = None) -> int:
    db.ensure_schema()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
