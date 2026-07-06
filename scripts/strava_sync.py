#!/usr/bin/env python3
"""Sync recent Strava activities into coach-data/.

Runs in GitHub Actions on a schedule. Mechanical by design: it logs activities
and updates plan session statuses. Coaching judgment (adaptation) stays with
Coach in chat sessions.

Env: STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN
     STRAVA_MOCK_FILE (optional): path to a JSON list of activities, for testing.
Exits 0 with a message when secrets are absent so pre-setup scheduled runs stay green.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(ROOT, "coach-data", "log.jsonl")
PLAN_PATH = os.path.join(ROOT, "coach-data", "plan.json")

RUN_TYPES = {"Run", "TrailRun", "VirtualRun"}
STRENGTH_TYPES = {"WeightTraining", "Workout", "Crossfit"}


def fetch_activities():
    mock = os.environ.get("STRAVA_MOCK_FILE")
    if mock:
        with open(mock) as f:
            return json.load(f)
    cid = os.environ.get("STRAVA_CLIENT_ID")
    secret = os.environ.get("STRAVA_CLIENT_SECRET")
    refresh = os.environ.get("STRAVA_REFRESH_TOKEN")
    if not (cid and secret and refresh):
        print("Strava secrets not configured yet - skipping sync.")
        sys.exit(0)
    body = urllib.parse.urlencode({
        "client_id": cid,
        "client_secret": secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh,
    }).encode()
    req = urllib.request.Request("https://www.strava.com/oauth/token", data=body)
    with urllib.request.urlopen(req, timeout=30) as r:
        token = json.load(r)
    after = int((datetime.now(timezone.utc) - timedelta(days=30)).timestamp())
    url = f"https://www.strava.com/api/v3/athlete/activities?after={after}&per_page=100"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token['access_token']}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def load_log():
    entries = []
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return entries


def pace_str(mins, miles):
    if not miles:
        return None
    sec_per_mi = mins * 60 / miles
    return f"{int(sec_per_mi // 60)}:{int(sec_per_mi % 60):02d}/mi"


def category(sport):
    if sport in RUN_TYPES:
        return "run"
    if sport in STRENGTH_TYPES:
        return "strength"
    return "cross"


def session_category(stype):
    if stype.endswith("_run"):
        return "run"
    if stype == "strength":
        return "strength"
    return "cross"


def main():
    activities = fetch_activities()
    log = load_log()
    seen = {e.get("strava_id") for e in log if e.get("strava_id")}
    with open(PLAN_PATH) as f:
        plan = json.load(f)
    by_date = {}
    for week in plan.get("weeks", []):
        for s in week.get("sessions", []):
            by_date.setdefault(s["date"], []).append(s)

    new_lines, plan_changed = [], False
    for act in sorted(activities, key=lambda a: a.get("start_date_local", "")):
        if act.get("id") in seen:
            continue
        sport = act.get("sport_type") or act.get("type") or "Workout"
        cat = category(sport)
        date = (act.get("start_date_local") or "")[:10]
        miles = round((act.get("distance") or 0) / 1609.34, 2)
        mins = round((act.get("moving_time") or 0) / 60)
        sess = next((s for s in by_date.get(date, [])
                     if session_category(s["type"]) == cat and s.get("status") in ("upcoming", "skipped")), None)
        result = "completed"
        if sess and cat == "run" and sess.get("miles"):
            result = "completed" if miles >= 0.9 * sess["miles"] else "partial"
        entry = {
            "date": date,
            "kind": "workout",
            "session_date": date,
            "type": sess["type"] if sess else ("easy_run" if cat == "run" else ("strength" if cat == "strength" else "cross_train")),
            "result": result,
            "source": "strava",
            "strava_id": act.get("id"),
            "planned": bool(sess),
            "name": act.get("name"),
            "actual": (f"{miles} mi in {mins} min" if cat == "run" else f"{mins} min"),
            "duration_min": mins,
        }
        if cat == "run" and miles:
            entry["miles"] = miles
            entry["avg_pace"] = pace_str(mins, miles)
        if act.get("average_heartrate"):
            entry["avg_hr"] = round(act["average_heartrate"])
        if act.get("max_heartrate"):
            entry["max_hr"] = round(act["max_heartrate"])
        new_lines.append(entry)
        if sess:
            sess["status"] = result
            plan_changed = True

    if not new_lines:
        print("No new activities.")
        return
    with open(LOG_PATH, "a") as f:
        for e in new_lines:
            f.write(json.dumps(e) + "\n")
    if plan_changed:
        with open(PLAN_PATH, "w") as f:
            json.dump(plan, f, indent=2)
    print(f"Logged {len(new_lines)} new activities: " +
          ", ".join(f"{e['date']} {e['type']} ({e['result']})" for e in new_lines))


if __name__ == "__main__":
    main()
