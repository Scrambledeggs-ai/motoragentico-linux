import json
import glob
from datetime import datetime, timezone
from pathlib import Path
from modules.pricing import CLAUDE_PRICING, DEFAULT_CLAUDE_PRICING


CLAUDE_DIR = Path.home() / ".claude"


def _get_model_pricing(model: str) -> dict:
    for key, pricing in CLAUDE_PRICING.items():
        if key in model:
            return pricing
    return DEFAULT_CLAUDE_PRICING


def _calc_cost(usage: dict, pricing: dict) -> float:
    input_t = usage.get("input_tokens", 0)
    output_t = usage.get("output_tokens", 0)
    cache_create = usage.get("cache_creation_input_tokens", 0)
    cache_read = usage.get("cache_read_input_tokens", 0)
    cost = (
        (input_t * pricing["input"] / 1_000_000)
        + (output_t * pricing["output"] / 1_000_000)
        + (cache_create * pricing["cache_creation"] / 1_000_000)
        + (cache_read * pricing["cache_read"] / 1_000_000)
    )
    return cost


def get_all_sessions() -> list[dict]:
    sessions = []
    pattern = str(CLAUDE_DIR / "projects" / "**" / "*.jsonl")
    for filepath in glob.glob(pattern, recursive=True):
        project = Path(filepath).parent.name.replace("-", "/").lstrip("/")
        session_id = Path(filepath).stem
        entries = []
        try:
            with open(filepath, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        except Exception:
            continue

        total_cost = 0.0
        input_tokens = 0
        output_tokens = 0
        cache_tokens = 0
        model = "claude-sonnet-4-6"
        timestamps = []

        for entry in entries:
            if entry.get("type") == "assistant" and "message" in entry:
                msg = entry["message"]
                if "model" in msg:
                    model = msg["model"]
                usage = msg.get("usage", {})
                if usage:
                    pricing = _get_model_pricing(model)
                    total_cost += _calc_cost(usage, pricing)
                    input_tokens += usage.get("input_tokens", 0)
                    output_tokens += usage.get("output_tokens", 0)
                    cache_tokens += usage.get("cache_read_input_tokens", 0)
            ts = entry.get("timestamp")
            if ts:
                try:
                    timestamps.append(datetime.fromisoformat(ts.replace("Z", "+00:00")))
                except Exception:
                    pass

        if not entries:
            continue

        first_ts = min(timestamps) if timestamps else None
        last_ts = max(timestamps) if timestamps else None

        sessions.append({
            "session_id": session_id,
            "project": project,
            "model": model,
            "cost_usd": total_cost,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_tokens": cache_tokens,
            "total_tokens": input_tokens + output_tokens + cache_tokens,
            "messages": len([e for e in entries if e.get("type") in ("human", "assistant")]),
            "first_ts": first_ts,
            "last_ts": last_ts,
        })

    return sorted(sessions, key=lambda s: s["last_ts"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)


def get_summary(days: int = 30) -> dict:
    sessions = get_all_sessions()
    cutoff = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    from datetime import timedelta
    cutoff = cutoff - timedelta(days=days)

    recent = [s for s in sessions if s["last_ts"] and s["last_ts"] >= cutoff]

    total_cost = sum(s["cost_usd"] for s in recent)
    total_tokens = sum(s["total_tokens"] for s in recent)
    total_input = sum(s["input_tokens"] for s in recent)
    total_output = sum(s["output_tokens"] for s in recent)

    by_day: dict[str, float] = {}
    for s in recent:
        if s["last_ts"]:
            day = s["last_ts"].strftime("%Y-%m-%d")
            by_day[day] = by_day.get(day, 0) + s["cost_usd"]

    return {
        "sessions_count": len(recent),
        "total_cost_usd": total_cost,
        "total_tokens": total_tokens,
        "input_tokens": total_input,
        "output_tokens": total_output,
        "cost_by_day": by_day,
        "sessions": recent,
    }
