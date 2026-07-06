#!/usr/bin/env python3
"""Sync recent activities into coach-data/ from intervals.icu (preferred) or Strava.

Runs in GitHub Actions on a schedule. Mechanical by design: it logs activities
and updates plan session statuses. Coaching judgment (adaptation) stays with
Coach in chat sessions.

Sources, tried in order:
  intervals.icu — INTERVALS_ATHLETE_ID + INTERVALS_API_KEY (free; syncs from Garmin)
  Strava        — STRAVA_CLIENT_ID + STRAVA_CLIENT_SECRET + STRAVA_REFRESH_TOKEN
  SYNC_MOCK_FILE (testing) — path to a JSON list of normalized activities.

Exits 0 with a message when no source is configured, so pre-setup runs stay green.
"""
import base64
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


def normalize(sync_id, sport, start_local, distance_m, moving_s, avg_hr, max_hr, name, source):
    return {
        "sync_id": sync_id, "sport": sport or "Workout",
        "date": (start_local or "")[:10],
        "start_local": start_local or "",
        "miles": round((distance_m or 0) / 1609.34, 2),
        "mins": round((moving_s or 0) / 60),
        "avg_hr": round(avg_hr) if avg_hr else None,
        "max_hr": round(max_hr) if max_hr else None,
        "name": name, "source": source,
    }


UA = "coach-activity-sync/1.0 (github.com/cdunn444/Coach)"


def fetch_intervals(athlete_id, api_key):
    athlete_id = athlete_id.strip()
    oldest = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00")
    url = f"https://intervals.icu/api/v1/athlete/{urllib.parse.quote(athlete_id)}/activities?oldest={oldest}"
    auth = base64.b64encode(f"API_KEY:{api_key.strip()}".encode()).decode()
    req = urllib.request.Request(url, headers={"Authorization": f"Basic {auth}", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            acts = json.load(r)
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode()[:300]
        except Exception:
            pass
        print(f"intervals.icu returned HTTP {e.code} for athlete '{athlete_id}'. {body}")
        if e.code in (401, 403):
            print("Check the INTERVALS_ATHLETE_ID (exactly as shown in Developer Settings, "
                  "e.g. 'i123456') and INTERVALS_API_KEY secrets.")
        sys.exit(1)
    return [normalize(f"icu-{a.get('id')}", a.get("type"), a.get("start_date_local"),
                      a.get("distance"), a.get("moving_time"),
                      a.get("average_heartrate"), a.get("max_heartrate"),
                      a.get("name"), "intervals.icu") for a in acts]


def fetch_strava(cid, secret, refresh):
    body = urllib.parse.urlencode({
        "client_id": cid, "client_secret": secret,
        "grant_type": "refresh_token", "refresh_token": refresh,
    }).encode()
    req = urllib.request.Request("https://www.strava.com/oauth/token", data=body,
                                 headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        token = json.load(r)
    after = int((datetime.now(timezone.utc) - timedelta(days=30)).timestamp())
    url = f"https://www.strava.com/api/v3/athlete/activities?after={after}&per_page=100"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token['access_token']}", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        acts = json.load(r)
    return [normalize(f"strava-{a.get('id')}", a.get("sport_type") or a.get("type"),
                      a.get("start_date_local"), a.get("distance"), a.get("moving_time"),
                      a.get("average_heartrate"), a.get("max_heartrate"),
                      a.get("name"), "strava") for a in acts]


def fetch_activities():
    mock = os.environ.get("SYNC_MOCK_FILE")
    if mock:
        with open(mock) as f:
            return [normalize(**a) for a in json.load(f)]
    icu_id, icu_key = os.environ.get("INTERVALS_ATHLETE_ID"), os.environ.get("INTERVALS_API_KEY")
    if icu_id and icu_key:
        return fetch_intervals(icu_id, icu_key)
    cid, sec, ref = (os.environ.get(k) for k in
                     ("STRAVA_CLIENT_ID", "STRAVA_CLIENT_SECRET", "STRAVA_REFRESH_TOKEN"))
    if cid and sec and ref:
        return fetch_strava(cid, sec, ref)
    print("No sync source configured yet - skipping.")
    sys.exit(0)


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
    seen = {e.get("sync_id") for e in log if e.get("sync_id")}
    with open(PLAN_PATH) as f:
        plan = json.load(f)
    by_date = {}
    for week in plan.get("weeks", []):
        for s in week.get("sessions", []):
            by_date.setdefault(s["date"], []).append(s)

    new_lines, plan_changed = [], False
    for act in sorted(activities, key=lambda a: a["start_local"]):
        if act["sync_id"] in seen:
            continue
        cat = category(act["sport"])
        sess = next((s for s in by_date.get(act["date"], [])
                     if session_category(s["type"]) == cat and s.get("status") in ("upcoming", "skipped")), None)
        result = "completed"
        if sess and cat == "run" and sess.get("miles"):
            result = "completed" if act["miles"] >= 0.9 * sess["miles"] else "partial"
        entry = {
            "date": act["date"],
            "kind": "workout",
            "session_date": act["date"],
            "type": sess["type"] if sess else ("easy_run" if cat == "run" else ("strength" if cat == "strength" else "cross_train")),
            "result": result,
            "source": act["source"],
            "sync_id": act["sync_id"],
            "planned": bool(sess),
            "name": act["name"],
            "actual": (f"{act['miles']} mi in {act['mins']} min" if cat == "run" else f"{act['mins']} min"),
            "duration_min": act["mins"],
        }
        if cat == "run" and act["miles"]:
            entry["miles"] = act["miles"]
            entry["avg_pace"] = pace_str(act["mins"], act["miles"])
        if act["avg_hr"]:
            entry["avg_hr"] = act["avg_hr"]
        if act["max_hr"]:
            entry["max_hr"] = act["max_hr"]
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
