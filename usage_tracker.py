import json, os, datetime
from pathlib import Path

USAGE_FILE = Path("docs/data/usage_stats.json")

# Approximate costs for llama-3.1-8b-instant (Groq)
# Input: $0.05 / 1M tokens, Output: $0.08 / 1M tokens (estimated/generic)
# Groq current pricing is roughly $0.05 per 1M tokens for 8B model.
INPUT_COST_PER_1M = 0.05
OUTPUT_COST_PER_1M = 0.08

def record_usage(model, prompt_tokens, completion_tokens):
    """Records usage to a JSON file for the dashboard and CLI."""
    if not USAGE_FILE.parent.exists():
        USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)

    stats = {
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "total_cost": 0.0,
        "last_updated": "",
        "sessions": []
    }

    if USAGE_FILE.exists():
        try:
            stats = json.loads(USAGE_FILE.read_text(encoding="utf-8"))
        except:
            pass

    cost = (prompt_tokens / 1_000_000 * INPUT_COST_PER_1M) + (completion_tokens / 1_000_000 * OUTPUT_COST_PER_1M)
    
    stats["total_prompt_tokens"] += prompt_tokens
    stats["total_completion_tokens"] += completion_tokens
    stats["total_cost"] += cost
    stats["last_updated"] = datetime.datetime.now().isoformat()
    
    # Simple session tracking (today's date)
    today = datetime.date.today().isoformat()
    session = next((s for s in stats.get("sessions", []) if s["date"] == today), None)
    if not session:
        session = {"date": today, "prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0}
        stats.setdefault("sessions", []).append(session)
    
    session["prompt_tokens"] += prompt_tokens
    session["completion_tokens"] += completion_tokens
    session["cost"] += cost

    USAGE_FILE.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    return stats

def get_status_line():
    """Returns a formatted status line for the CLI."""
    if not USAGE_FILE.exists():
        return "Usage: No data"
    try:
        stats = json.loads(USAGE_FILE.read_text(encoding="utf-8"))
        today = datetime.date.today().isoformat()
        session = next((s for s in stats.get("sessions", []) if s["date"] == today), {"prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0})
        
        return (f"📊 Today: {session['prompt_tokens'] + session['completion_tokens']:,} tokens "
                f"(${session['cost']:.4f}) | "
                f"Total: ${stats['total_cost']:.2f}")
    except:
        return "Usage: Error reading stats"
