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
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(ROOT, "coach-data", "log.jsonl")
PLAN_PATH = os.path.join(ROOT, "coach-data", "plan.json")

RUN_TYPES = {"Run", "TrailRun", "VirtualRun"}
STRENGTH_TYPES = {"WeightTraining", "Workout", "Crossfit"}


def normalize(sync_id, sport, start_local, distance_m, moving_s, avg_hr, max_hr, name, source,
              calories=None):
    return {
        "sync_id": sync_id, "sport": sport or "Workout",
        "date": (start_local or "")[:10],
        "start_local": start_local or "",
        "miles": round((distance_m or 0) / 1609.34, 2),
        "mins": round((moving_s or 0) / 60),
        "avg_hr": round(avg_hr) if avg_hr else None,
        "max_hr": round(max_hr) if max_hr else None,
        "kcal": round(calories) if calories else None,
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
                      a.get("name"), "intervals.icu",
                      calories=a.get("icu_active_calories") or a.get("calories")) for a in acts]


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
                      a.get("name"), "strava",
                      calories=a.get("calories") or a.get("kilojoules")) for a in acts]


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


RUN_SESSION_TYPES = ("easy_run", "long_run", "tempo_run", "interval_run")


def _round_q(x):
    return round(x * 4) / 4


def _set_session_miles(s, new_mi):
    """Update a session's miles, keeping detail text and duration in step."""
    old = s.get("miles")
    base = s.get("miles_planned", old)
    if s.get("duration_min") and old:
        s["duration_min"] = round(s["duration_min"] * new_mi / old)
    s["miles"] = new_mi
    detail = re.sub(r"\s*\(auto-adjusted from [^)]*\)", "", s.get("detail", ""))
    m = re.search(r"\d+(?:\.\d+)?\s*mi\b", detail)
    if m:
        detail = detail[:m.start()] + f"{new_mi:g} mi" + detail[m.end():]
    if base is not None and abs(new_mi - base) > 0.01:
        detail = detail.rstrip() + f" (auto-adjusted from {base:g} mi)"
    s["detail"] = detail


def adapt_current_week(plan, entries, today):
    """Volume guard: reconcile the current week's remaining runs with actual miles.

    Mechanical and bounded by design — trims remaining easy runs (then the long
    run, never quality sessions) when the week is tracking >10% over its target,
    and pads easy runs (then the long run) when it's tracking >15% under. The
    week's original volume is anchored in week.miles_target and each adjusted
    session's original mileage in session.miles_planned, so repeated runs are
    idempotent. Structural changes stay with Coach in chat.
    Returns adaptation log entries (possibly empty); mutates plan in place.
    """
    week = None
    for w in plan.get("weeks", []):
        dates = [s["date"] for s in w.get("sessions", [])]
        if dates and min(dates) <= today <= max(dates):
            week = w
            break
    if not week:
        return []
    runs = [s for s in week["sessions"] if s["type"] in RUN_SESSION_TYPES]
    target = week.get("miles_target")
    if target is None:
        target = sum(s.get("miles") or 0 for s in runs)
    if not target:
        return []
    dates = [s["date"] for s in week["sessions"]]
    lo_d, hi_d = min(dates), max(dates)
    actual = sum(e.get("miles") or 0 for e in entries
                 if e.get("kind") == "workout" and e.get("result") in ("completed", "partial")
                 and lo_d <= (e.get("session_date") or e.get("date") or "") <= hi_d)
    remaining = [s for s in runs if s.get("status") == "upcoming" and (s.get("miles") or 0) > 0]
    if not remaining:
        return []
    projected = actual + sum(s["miles"] for s in remaining)
    hi, lo = target * 1.10, target * 0.85
    before = projected
    changes = []
    easies = [s for s in remaining if s["type"] == "easy_run"]
    longs = [s for s in remaining if s["type"] == "long_run"]
    if projected > hi:
        for s in easies + longs:  # trim easy days first, protect the long run longest
            if projected <= hi:
                break
            s.setdefault("miles_planned", s["miles"])
            floor = 2.0 if s["type"] == "easy_run" else max(3.0, _round_q(s["miles_planned"] * 0.7))
            new_mi = max(floor, _round_q(s["miles"] - (projected - hi)))
            if new_mi < s["miles"] - 0.01:
                changes.append(f"{s['day']} {s['type'].replace('_', ' ')} {s['miles']:g}→{new_mi:g} mi")
                projected -= s["miles"] - new_mi
                _set_session_miles(s, new_mi)
        verdict = (f"volume guard: week tracking {before:.1f} mi vs {target:g} planned (cap +10%) — "
                   f"trimmed {', '.join(changes)} to protect the ramp (shin/arch history). "
                   "Extra volume is already banked; nothing is lost.")
    elif projected < lo:
        goal = target * 0.95
        for s in easies + longs:  # pad easy days first; quality sessions stay as written
            if projected >= goal:
                break
            s.setdefault("miles_planned", s["miles"])
            cap = _round_q(s["miles_planned"] * (1.25 if s["type"] == "easy_run" else 1.15))
            new_mi = min(cap, _round_q(s["miles"] + (goal - projected)))
            if new_mi > s["miles"] + 0.01:
                changes.append(f"{s['day']} {s['type'].replace('_', ' ')} {s['miles']:g}→{new_mi:g} mi")
                projected += new_mi - s["miles"]
                _set_session_miles(s, new_mi)
        verdict = (f"volume guard: week tracking {before:.1f} mi vs {target:g} planned (floor −15%) — "
                   f"bumped {', '.join(changes)} to close the gap without spiking any single day.")
    if not changes:
        return []
    week["miles_target"] = target
    return [{"date": today, "kind": "adaptation", "action": verdict,
             "trigger": "activity sync volume reconcile", "source": "auto"}]


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
                     if s["type"] != "rest" and session_category(s["type"]) == cat
                     and s.get("status") in ("upcoming", "skipped")), None)
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
        if act.get("kcal"):
            entry["active_kcal"] = act["kcal"]
        new_lines.append(entry)
        if sess:
            sess["status"] = result
            plan_changed = True

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    adaptations = adapt_current_week(plan, log + new_lines, today)
    if not new_lines and not adaptations:
        print("No new activities; plan already in balance.")
        return
    if new_lines or adaptations:
        with open(LOG_PATH, "a") as f:
            for e in new_lines + adaptations:
                f.write(json.dumps(e) + "\n")
    if plan_changed or adaptations:
        with open(PLAN_PATH, "w") as f:
            json.dump(plan, f, indent=2)
    if new_lines:
        print(f"Logged {len(new_lines)} new activities: " +
              ", ".join(f"{e['date']} {e['type']} ({e['result']})" for e in new_lines))
    for a in adaptations:
        print("Adaptation: " + a["action"])


if __name__ == "__main__":
    main()
