import subprocess
import re
from datetime import datetime, timezone, timedelta


HERMES_BIN = "/home/zenau/.local/bin/hermes"


def _run(args: list[str]) -> str:
    try:
        result = subprocess.run(
            [HERMES_BIN] + args,
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.stdout
    except Exception:
        return ""


def get_insights(days: int = 30) -> dict:
    raw = _run(["insights", "--days", str(days)])
    data = {
        "sessions": 0,
        "messages": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "active_time_hours": 0.0,
        "models": [],
        "activity_by_day": {},
        "peak_hours": [],
        "raw": raw,
    }

    def _extract_int(pattern, text, group=1):
        m = re.search(pattern, text)
        return int(m.group(group).replace(",", "")) if m else 0

    data["sessions"] = _extract_int(r"Sessions:\s+([\d,]+)", raw)
    data["messages"] = _extract_int(r"Messages:\s+([\d,]+)", raw)
    data["input_tokens"] = _extract_int(r"Input tokens:\s+([\d,]+)", raw)
    data["output_tokens"] = _extract_int(r"Output tokens:\s+([\d,]+)", raw)
    data["total_tokens"] = _extract_int(r"Total tokens:\s+([\d,]+)", raw)

    time_m = re.search(r"Active time:\s+~?([\d]+)h\s*([\d]+)m", raw)
    if time_m:
        data["active_time_hours"] = int(time_m.group(1)) + int(time_m.group(2)) / 60

    model_section = re.findall(
        r"([\w.:_-]+(?:latest|instruct|[\d]+b)?)\s+(\d+)\s+([\d,]+)", raw
    )
    for m in model_section:
        name, sessions, tokens = m
        if name not in ("Model", "Sessions", "Tokens"):
            data["models"].append({
                "name": name,
                "sessions": int(sessions),
                "tokens": int(tokens.replace(",", "")),
            })

    day_lines = re.findall(r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+([█\s]*)\s+(\d+)?", raw)
    for line in day_lines:
        day, bars, count = line
        if count:
            data["activity_by_day"][day] = int(count)

    hours_m = re.search(r"Peak hours:\s+(.+)", raw)
    if hours_m:
        data["peak_hours"] = hours_m.group(1).strip()

    return data


def get_stats() -> dict:
    raw = _run(["sessions", "stats"])
    data = {"total_sessions": 0, "total_messages": 0, "db_size": ""}

    m = re.search(r"Total sessions:\s+(\d+)", raw)
    if m:
        data["total_sessions"] = int(m.group(1))

    m = re.search(r"Total messages:\s+(\d+)", raw)
    if m:
        data["total_messages"] = int(m.group(1))

    m = re.search(r"Database size:\s+([\d.]+ \w+)", raw)
    if m:
        data["db_size"] = m.group(1)

    return data


def get_recent_sessions(limit: int = 20) -> list[dict]:
    raw = _run(["sessions", "list"])
    sessions = []
    lines = raw.strip().split("\n")
    for line in lines[2:]:
        if not line.strip() or "─" in line:
            continue
        parts = line.split("  ")
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) >= 3:
            title = parts[0] if parts[0] != "—" else "(sin título)"
            last_active = parts[-2] if len(parts) >= 2 else ""
            session_id = parts[-1] if len(parts) >= 1 else ""
            sessions.append({
                "title": title,
                "last_active": last_active,
                "session_id": session_id,
            })
        if len(sessions) >= limit:
            break
    return sessions
