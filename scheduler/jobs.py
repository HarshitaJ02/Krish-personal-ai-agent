import uuid
from zoneinfo import ZoneInfo

from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from agent.llm import get_llm_response
import config
import re
import json

# Global scheduler instance
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")

async def send_reminder(bot, chat_id: str, message: str):
    """Sends a reminder message to the user."""
    await bot.send_message(chat_id=chat_id, text=f"⏰ Reminder: {message}")

def parse_reminder_datetime(text: str) -> dict[str, str | None] | None:
    """
    Uses LLM to extract datetime from natural language.
    Handles both absolute times ("at 7pm") and relative times ("in 2 minutes").
    Returns ISO format string like "2026-02-25 08:00:00" or None if not found.
    """
    prompt = [{
        "role": "system",
        "content": f"""Extract the reminder datetime from the message and return ONLY a JSON object.
Current time is {datetime.now().strftime("%Y-%m-%d %H:%M")} IST (UTC+5:30).
Convert ALL times to absolute datetime — including relative ones like 'in 2 minutes', 'in 1 hour', 'tomorrow'.
Return ONLY this JSON:
{{"datetime": "YYYY-MM-DD HH:MM:SS", "message": "what to remind about"}}
If no datetime found: {{"datetime": null, "message": null}}"""
    }, {
        "role": "user",
        "content": text
    }]

    try:
        response = get_llm_response(prompt, use_classifier_model=True)
        raw = response.get("content", "").strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        parsed = json.loads(raw)
        return parsed
    except Exception:
        return None

def add_reminder(bot, chat_id: str, message: str, run_date: datetime):
    """Dynamically adds a one-time reminder job to the scheduler."""
    import hashlib
    run_date = run_date.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
    job_id = hashlib.md5(f"{chat_id}_{message}_{run_date.isoformat()}".encode()).hexdigest()

    scheduler.add_job(
        send_reminder,
        trigger="date",
        run_date=run_date,
        args=[bot, chat_id, message],
        id=job_id,
        replace_existing=True
    )
    
    return f"Reminder set for {run_date.strftime('%B %d at %I:%M %p')} IST"