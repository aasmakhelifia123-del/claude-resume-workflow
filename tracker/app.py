"""Flask app for the tracker."""

from __future__ import annotations

import calendar as _calendar
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, url_for

from . import db

app = Flask(__name__)


SORTABLE_COLUMNS = {
    "company": lambda r: (r.get("company") or "").lower(),
    "role": lambda r: (r.get("role") or "").lower(),
    "status": lambda r: r.get("status") or "",
    "date_applied": lambda r: r.get("date_applied") or "",
    "last_activity": lambda r: r.get("_last_activity") or "",
    "follow_up": lambda r: r["follow_up"]["days_since"] if r.get("follow_up") else -1,
}

STATE_LABELS = {
    "scheduled": "Scheduled",
    "awaiting": "Awaiting result",
    "passed": "Passed",
    "failed": "Failed",
    "rescheduled": "Rescheduled",
    "no_show": "No-show",
}


@app.template_filter("state_label")
def _state_label(state: str) -> str:
    return STATE_LABELS.get(state, state)


@app.template_filter("round_state")
def _round_state_filter(row):
    return db.round_state(row)


# --- routes --------------------------------------------------------------

@app.route("/")
def index():
    status_filter = request.args.get("status") or None
    search = request.args.get("q") or None
    location = request.args.get("location") or None
    follow_up_only = request.args.get("follow_up") == "1"
    sort = request.args.get("sort") or "date_applied"
    direction = request.args.get("dir") or ("asc" if sort in {"company", "role"} else "desc")
    if sort not in SORTABLE_COLUMNS:
        sort = "date_applied"
        direction = "desc"

    rows = db.list_applications(status=status_filter, search=search, location_type=location)
    enriched = []
    for row in rows:
        last = db.last_round(row["slug"])
        follow_up = db.needs_follow_up(row["slug"])
        last_activity = row["updated_at"] or row["created_at"] or ""
        if last and last["scheduled_at"] and last["scheduled_at"] > last_activity:
            last_activity = last["scheduled_at"]
        enriched.append({
            **dict(row),
            "last_round": last,
            "last_round_state": db.round_state(last) if last else None,
            "follow_up": follow_up,
            "_last_activity": last_activity,
        })

    if follow_up_only:
        enriched = [r for r in enriched if r.get("follow_up")]

    key_fn = SORTABLE_COLUMNS[sort]
    enriched.sort(key=key_fn, reverse=(direction == "desc"))

    follow_ups = [r for r in enriched if r.get("follow_up")]
    counts = db.status_counts()
    return render_template(
        "index.html",
        rows=enriched,
        counts=counts,
        statuses=db.STATUSES,
        location_types=db.LOCATION_TYPES,
        status_filter=status_filter,
        location_filter=location,
        search=search or "",
        sort=sort,
        direction=direction,
        follow_up_only=follow_up_only,
        follow_ups=follow_ups,
        total=sum(counts.values()),
    )


@app.route("/app/<slug>")
def detail(slug: str):
    row = db.get_application(slug)
    if row is None:
        abort(404)
    rounds = db.get_rounds(slug)
    assets = db.folder_assets(slug)
    jd_text = db.read_jd(slug)
    follow_up = db.needs_follow_up(slug)
    return render_template(
        "detail.html",
        row=row,
        rounds=rounds,
        assets=assets,
        jd_text=jd_text,
        statuses=db.STATUSES,
        outcomes=db.INTERVIEW_OUTCOMES,
        location_types=db.LOCATION_TYPES,
        folder=f"applications/{slug}",
        follow_up=follow_up,
    )


@app.route("/app/<slug>/edit", methods=["POST"])
def edit(slug: str):
    if db.get_application(slug) is None:
        abort(404)
    form = request.form
    db.update_application(
        slug,
        company=form.get("company") or "",
        role=form.get("role") or None,
        jd_url=form.get("jd_url") or None,
        salary_range=form.get("salary_range") or None,
        location_type=form.get("location_type") or None,
        status=form.get("status") or "draft",
        date_applied=form.get("date_applied") or None,
        notes=form.get("notes") or None,
    )
    return redirect(url_for("detail", slug=slug))


@app.route("/app/<slug>/jd", methods=["POST"])
def edit_jd(slug: str):
    if db.get_application(slug) is None:
        abort(404)
    db.write_jd(slug, request.form.get("jd_text", ""))
    return redirect(url_for("detail", slug=slug))


@app.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        slug = (request.form.get("slug") or "").strip()
        company = (request.form.get("company") or "").strip()
        if not slug or not company:
            abort(400)
        db.add_application(
            slug=slug,
            company=company,
            role=request.form.get("role") or None,
            jd_url=request.form.get("jd_url") or None,
            salary_range=request.form.get("salary_range") or None,
            location_type=request.form.get("location_type") or None,
            status=request.form.get("status") or "draft",
            date_applied=request.form.get("date_applied") or None,
            notes=request.form.get("notes") or None,
        )
        return redirect(url_for("detail", slug=slug))
    return render_template("new.html", statuses=db.STATUSES, location_types=db.LOCATION_TYPES)


@app.route("/app/<slug>/delete", methods=["POST"])
def delete(slug: str):
    db.delete_application(slug)
    return redirect(url_for("index"))


@app.route("/app/<slug>/rounds/new", methods=["POST"])
def round_new(slug: str):
    if db.get_application(slug) is None:
        abort(404)
    form = request.form
    db.add_round(
        slug=slug,
        stage=form.get("stage") or "Round",
        scheduled_at=form.get("scheduled_at") or None,
        outcome=form.get("outcome") or None,
        notes=form.get("notes") or None,
    )
    return redirect(url_for("detail", slug=slug))


@app.route("/rounds/<int:round_id>/edit", methods=["POST"])
def round_edit(round_id: int):
    row = db.get_round(round_id)
    if row is None:
        abort(404)
    form = request.form
    db.update_round(
        round_id=round_id,
        stage=form.get("stage") or None,
        scheduled_at=form.get("scheduled_at") or None,
        outcome=form.get("outcome") or None,
        notes=form.get("notes") or "",
    )
    return redirect(url_for("detail", slug=row["slug"]))


@app.route("/rounds/<int:round_id>/delete", methods=["POST"])
def round_delete(round_id: int):
    row = db.get_round(round_id)
    if row is None:
        abort(404)
    slug = row["slug"]
    db.delete_round(round_id)
    return redirect(url_for("detail", slug=slug))


@app.route("/rounds/<int:round_id>/log-followup", methods=["POST"])
def round_log_followup(round_id: int):
    row = db.get_round(round_id)
    if row is None:
        abort(404)
    form = request.form
    snooze = (form.get("snooze") or "7").strip()
    dismiss = snooze == "dismiss"
    snooze_days: int | None = None
    if not dismiss:
        try:
            snooze_days = int(snooze)
        except ValueError:
            snooze_days = db.FOLLOW_UP_DAYS
    db.log_followup(
        round_id,
        note=(form.get("note") or None),
        snooze_days=snooze_days,
        dismiss=dismiss,
    )
    return redirect(url_for("detail", slug=row["slug"]))


@app.route("/calendar")
def calendar_view():
    today = date.today()
    month_param = request.args.get("month") or today.strftime("%Y-%m")
    try:
        year, month = (int(p) for p in month_param.split("-", 1))
        first = date(year, month, 1)
    except (ValueError, TypeError):
        first = today.replace(day=1)
        year, month = first.year, first.month

    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)
    next_first = date(next_year, next_month, 1)
    prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)

    rounds = db.rounds_in_range(first, next_first)
    applied = db.applications_applied_in_range(first, next_first)

    by_day: dict[int, dict[str, list]] = {}
    for r in rounds:
        d = datetime.strptime(r["scheduled_at"].replace("T", " ")[:10], "%Y-%m-%d").day
        cell = by_day.setdefault(d, {"rounds": [], "applied": []})
        cell["rounds"].append({
            "id": r["id"],
            "slug": r["slug"],
            "company": r["company"],
            "stage": r["stage"],
            "state": db.round_state(r),
            "time": r["scheduled_at"][11:16] if len(r["scheduled_at"]) >= 16 else "",
        })
    for a in applied:
        d = datetime.strptime(a["date_applied"], "%Y-%m-%d").day
        cell = by_day.setdefault(d, {"rounds": [], "applied": []})
        cell["applied"].append({"slug": a["slug"], "company": a["company"]})

    cal = _calendar.Calendar(firstweekday=0)  # Monday
    weeks = cal.monthdatescalendar(year, month)

    return render_template(
        "calendar.html",
        weeks=weeks,
        month_first=first,
        month_label=first.strftime("%B %Y"),
        by_day=by_day,
        today=today,
        prev_month=f"{prev_year:04d}-{prev_month:02d}",
        next_month=f"{next_year:04d}-{next_month:02d}",
    )


@app.route("/app/<slug>/open-folder", methods=["POST"])
def open_folder(slug: str):
    folder = db.folder_for(slug)
    if folder.is_dir():
        subprocess.Popen(["open", str(folder)])
    return redirect(url_for("detail", slug=slug))


# --- entrypoint ----------------------------------------------------------

def run_dev(host: str = "127.0.0.1", port: int = 5050) -> None:
    db.ensure_schema()
    print(f"tracker UI → http://{host}:{port}", file=sys.stderr)
    app.run(host=host, port=port, debug=False)
