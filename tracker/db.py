"""SQLite layer for the application tracker.

The DB file lives at the repo root as `tracker.db` and is committed. There's
exactly one user and one machine, so the file IS the dataset.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterator

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "tracker.db"
APPLICATIONS_DIR = REPO_ROOT / "applications"

FOLLOW_UP_DAYS = 7

STATUSES = (
    "draft",
    "applied",
    "screening",
    "interviewing",
    "offer",
    "rejected",
    "withdrawn",
    "ghosted",
)

INTERVIEW_OUTCOMES = (
    "pending",
    "passed",
    "failed",
    "rescheduled",
    "no_show",
)

LOCATION_TYPES = (
    "remote",
    "hybrid",
    "onsite",
    "unknown",
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    slug           TEXT PRIMARY KEY,
    company        TEXT NOT NULL,
    role           TEXT,
    jd_url         TEXT,
    salary_range   TEXT,
    location_type  TEXT,
    status         TEXT NOT NULL DEFAULT 'draft',
    date_applied   DATE,
    notes          TEXT,
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS interview_rounds (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    slug                 TEXT NOT NULL REFERENCES applications(slug) ON DELETE CASCADE,
    stage                TEXT NOT NULL,
    scheduled_at         DATETIME,
    outcome              TEXT DEFAULT 'pending',
    notes                TEXT,
    nudge_silenced_until DATETIME,
    created_at           DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS applications_touch
AFTER UPDATE ON applications
FOR EACH ROW
BEGIN
    UPDATE applications SET updated_at = CURRENT_TIMESTAMP WHERE slug = NEW.slug;
END;
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_schema() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
        _migrate(conn)


def _migrate(conn: sqlite3.Connection) -> None:
    """Idempotent column adds for DBs created before new fields existed."""
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(applications)")}
    if "salary_range" not in cols:
        conn.execute("ALTER TABLE applications ADD COLUMN salary_range TEXT")
    if "location_type" not in cols:
        conn.execute("ALTER TABLE applications ADD COLUMN location_type TEXT")
    round_cols = {r["name"] for r in conn.execute("PRAGMA table_info(interview_rounds)")}
    if "nudge_silenced_until" not in round_cols:
        conn.execute("ALTER TABLE interview_rounds ADD COLUMN nudge_silenced_until DATETIME")


@contextmanager
def txn() -> Iterator[sqlite3.Connection]:
    ensure_schema()
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# --- queries -------------------------------------------------------------

def list_applications(
    status: str | None = None,
    search: str | None = None,
    location_type: str | None = None,
) -> list[sqlite3.Row]:
    sql = "SELECT * FROM applications"
    where: list[str] = []
    params: list[object] = []
    if status:
        where.append("status = ?")
        params.append(status)
    if location_type:
        where.append("location_type = ?")
        params.append(location_type)
    if search:
        where.append("(company LIKE ? OR slug LIKE ? OR role LIKE ?)")
        like = f"%{search}%"
        params.extend([like, like, like])
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY COALESCE(date_applied, created_at) DESC, slug"
    with txn() as conn:
        return list(conn.execute(sql, params))


def get_application(slug: str) -> sqlite3.Row | None:
    with txn() as conn:
        return conn.execute("SELECT * FROM applications WHERE slug = ?", (slug,)).fetchone()


def get_rounds(slug: str) -> list[sqlite3.Row]:
    with txn() as conn:
        return list(conn.execute(
            "SELECT * FROM interview_rounds WHERE slug = ? "
            "ORDER BY COALESCE(scheduled_at, created_at), id",
            (slug,),
        ))


def get_round(round_id: int) -> sqlite3.Row | None:
    with txn() as conn:
        return conn.execute("SELECT * FROM interview_rounds WHERE id = ?", (round_id,)).fetchone()


def status_counts() -> dict[str, int]:
    with txn() as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) AS n FROM applications GROUP BY status"
        ).fetchall()
    return {row["status"]: row["n"] for row in rows}


def last_round(slug: str) -> sqlite3.Row | None:
    with txn() as conn:
        return conn.execute(
            "SELECT * FROM interview_rounds WHERE slug = ? "
            "ORDER BY COALESCE(scheduled_at, created_at) DESC LIMIT 1",
            (slug,),
        ).fetchone()


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    s = value.replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def round_state(row: sqlite3.Row, now: datetime | None = None) -> str:
    """Derive a display state from (scheduled_at, outcome).

    'pending' is split visually into 'scheduled' (future) and 'awaiting'
    (past or undated); other outcomes pass through.
    """
    outcome = (row["outcome"] or "pending") if hasattr(row, "keys") else "pending"
    if outcome != "pending":
        return outcome
    sched = _parse_dt(row["scheduled_at"]) if hasattr(row, "keys") else None
    now = now or datetime.now()
    if sched and sched > now:
        return "scheduled"
    return "awaiting"


def needs_follow_up(slug: str, now: datetime | None = None) -> dict | None:
    """Return follow-up info if the most recent round is unresolved and stale.

    Returns {'round': Row, 'days_since': int, 'since': datetime} or None.
    Triggers when: the latest round's outcome is 'pending', no future-dated
    round exists, and the reference time (scheduled_at or created_at) is at
    least FOLLOW_UP_DAYS ago.
    """
    now = now or datetime.now()
    last = last_round(slug)
    if last is None or last["outcome"] != "pending":
        return None
    sched = _parse_dt(last["scheduled_at"])
    if sched and sched > now:
        return None
    silenced = _parse_dt(last["nudge_silenced_until"]) if "nudge_silenced_until" in last.keys() else None
    if silenced and silenced > now:
        return None
    reference = sched or _parse_dt(last["created_at"])
    if reference is None:
        return None
    delta = now - reference
    if delta < timedelta(days=FOLLOW_UP_DAYS):
        return None
    return {
        "round": last,
        "days_since": delta.days,
        "since": reference,
    }


def rounds_in_range(start: date, end: date) -> list[sqlite3.Row]:
    """Rounds with scheduled_at in [start, end), joined with company name."""
    with txn() as conn:
        return list(conn.execute(
            "SELECT r.*, a.company FROM interview_rounds r "
            "JOIN applications a ON a.slug = r.slug "
            "WHERE r.scheduled_at IS NOT NULL "
            "AND date(r.scheduled_at) >= ? AND date(r.scheduled_at) < ? "
            "ORDER BY r.scheduled_at",
            (start.isoformat(), end.isoformat()),
        ))


def applications_applied_in_range(start: date, end: date) -> list[sqlite3.Row]:
    with txn() as conn:
        return list(conn.execute(
            "SELECT slug, company, date_applied FROM applications "
            "WHERE date_applied IS NOT NULL "
            "AND date_applied >= ? AND date_applied < ? "
            "ORDER BY date_applied",
            (start.isoformat(), end.isoformat()),
        ))


# --- mutations -----------------------------------------------------------

def add_application(
    slug: str,
    company: str,
    role: str | None = None,
    jd_url: str | None = None,
    salary_range: str | None = None,
    location_type: str | None = None,
    status: str = "draft",
    date_applied: str | None = None,
    notes: str | None = None,
) -> None:
    if status not in STATUSES:
        raise ValueError(f"invalid status {status!r}; choose from {STATUSES}")
    if location_type is not None and location_type not in LOCATION_TYPES:
        raise ValueError(f"invalid location_type {location_type!r}; choose from {LOCATION_TYPES}")
    with txn() as conn:
        conn.execute(
            "INSERT INTO applications "
            "(slug, company, role, jd_url, salary_range, location_type, status, date_applied, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (slug, company, role, jd_url, salary_range, location_type,
             status, date_applied, notes),
        )


def update_application(slug: str, **fields: object) -> None:
    if "status" in fields and fields["status"] not in STATUSES:
        raise ValueError(f"invalid status {fields['status']!r}")
    if (
        "location_type" in fields
        and fields["location_type"] is not None
        and fields["location_type"] not in LOCATION_TYPES
    ):
        raise ValueError(f"invalid location_type {fields['location_type']!r}")
    allowed = {
        "company", "role", "jd_url", "salary_range", "location_type",
        "status", "date_applied", "notes",
    }
    fields = {k: v for k, v in fields.items() if k in allowed}
    if not fields:
        return
    sets = ", ".join(f"{k} = ?" for k in fields)
    params = list(fields.values()) + [slug]
    with txn() as conn:
        conn.execute(f"UPDATE applications SET {sets} WHERE slug = ?", params)


def delete_application(slug: str) -> None:
    with txn() as conn:
        conn.execute("DELETE FROM applications WHERE slug = ?", (slug,))


def mark_applied(slug: str) -> bool:
    """Idempotent: flip status draft→applied and stamp date_applied if null.

    Returns True if a change was made.
    """
    with txn() as conn:
        row = conn.execute(
            "SELECT status, date_applied FROM applications WHERE slug = ?", (slug,)
        ).fetchone()
        if row is None:
            return False
        new_status = "applied" if row["status"] == "draft" else row["status"]
        new_date = row["date_applied"] or date.today().isoformat()
        if new_status == row["status"] and new_date == row["date_applied"]:
            return False
        conn.execute(
            "UPDATE applications SET status = ?, date_applied = ? WHERE slug = ?",
            (new_status, new_date, slug),
        )
    return True


def append_note(slug: str, text: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"[{stamp}] {text}"
    with txn() as conn:
        row = conn.execute("SELECT notes FROM applications WHERE slug = ?", (slug,)).fetchone()
        if row is None:
            raise KeyError(slug)
        existing = (row["notes"] or "").rstrip()
        combined = f"{existing}\n{line}".strip() if existing else line
        conn.execute("UPDATE applications SET notes = ? WHERE slug = ?", (combined, slug))


def add_round(
    slug: str,
    stage: str,
    scheduled_at: str | None = None,
    outcome: str | None = None,
    notes: str | None = None,
) -> int:
    if outcome is not None and outcome not in INTERVIEW_OUTCOMES:
        raise ValueError(f"invalid outcome {outcome!r}")
    with txn() as conn:
        cur = conn.execute(
            "INSERT INTO interview_rounds (slug, stage, scheduled_at, outcome, notes) "
            "VALUES (?, ?, ?, ?, ?)",
            (slug, stage, scheduled_at, outcome or "pending", notes),
        )
        round_id = cur.lastrowid
        # Bump the parent's status to interviewing if it's still applied/screening/draft.
        conn.execute(
            "UPDATE applications SET status = 'interviewing' "
            "WHERE slug = ? AND status IN ('draft', 'applied', 'screening')",
            (slug,),
        )
    return int(round_id)


def update_round(
    round_id: int,
    stage: str | None = None,
    scheduled_at: str | None = None,
    outcome: str | None = None,
    notes: str | None = None,
) -> None:
    if outcome is not None and outcome not in INTERVIEW_OUTCOMES:
        raise ValueError(f"invalid outcome {outcome!r}")
    fields: dict[str, object] = {}
    if stage is not None:
        fields["stage"] = stage
    if scheduled_at is not None:
        fields["scheduled_at"] = scheduled_at
    if outcome is not None:
        fields["outcome"] = outcome
    if notes is not None:
        fields["notes"] = notes
    if not fields:
        return
    sets = ", ".join(f"{k} = ?" for k in fields)
    params = list(fields.values()) + [round_id]
    with txn() as conn:
        conn.execute(f"UPDATE interview_rounds SET {sets} WHERE id = ?", params)


def delete_round(round_id: int) -> None:
    with txn() as conn:
        conn.execute("DELETE FROM interview_rounds WHERE id = ?", (round_id,))


FOLLOWUP_DISMISS_SENTINEL = "9999-12-31 00:00:00"


def log_followup(
    round_id: int,
    *,
    note: str | None = None,
    snooze_days: int | None = None,
    dismiss: bool = False,
) -> None:
    """Record a follow-up on a round: silence its nudge, optionally append a note.

    `dismiss=True` parks `nudge_silenced_until` at a sentinel far-future date.
    Otherwise `snooze_days` (default FOLLOW_UP_DAYS) shifts it that far ahead.
    A non-empty `note` is appended to the round's notes with a date stamp.
    """
    if dismiss:
        silenced_until = FOLLOWUP_DISMISS_SENTINEL
    else:
        days = snooze_days if snooze_days is not None else FOLLOW_UP_DAYS
        silenced_until = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    with txn() as conn:
        row = conn.execute(
            "SELECT notes FROM interview_rounds WHERE id = ?", (round_id,)
        ).fetchone()
        if row is None:
            raise KeyError(round_id)
        new_notes = row["notes"]
        if note and note.strip():
            stamp = date.today().isoformat()
            line = f"[{stamp}] {note.strip()}"
            existing = (row["notes"] or "").rstrip()
            new_notes = f"{existing}\n{line}".strip() if existing else line
        conn.execute(
            "UPDATE interview_rounds SET nudge_silenced_until = ?, notes = ? WHERE id = ?",
            (silenced_until, new_notes, round_id),
        )


# --- folder helpers ------------------------------------------------------

def folder_for(slug: str) -> Path:
    return APPLICATIONS_DIR / slug


def folder_assets(slug: str) -> dict[str, bool]:
    folder = folder_for(slug)
    return {
        "resume_md": (folder / "resume.md").exists(),
        "cover_letter_md": (folder / "cover-letter.md").exists(),
        "resume_pdf": (folder / "resume.pdf").exists(),
        "cover_letter_pdf": (folder / "cover-letter.pdf").exists(),
        "jd_md": jd_path(slug).exists(),
    }


def jd_path(slug: str) -> Path:
    return folder_for(slug) / "jd.md"


def read_jd(slug: str) -> str:
    p = jd_path(slug)
    return p.read_text() if p.exists() else ""


def write_jd(slug: str, text: str) -> None:
    folder = folder_for(slug)
    folder.mkdir(parents=True, exist_ok=True)
    jd_path(slug).write_text(text.rstrip() + "\n" if text.strip() else "")
