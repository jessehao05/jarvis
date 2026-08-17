import json
import os
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(Path.home() / ".jarvis" / ".env")

_SYSTEM_PROMPT = """\
You are a calendar assistant. Extract structured event data from natural language and return ONLY valid JSON — no explanation, no markdown, no code fences.

Current datetime: {now}
Timezone: {tz}

Return this schema:
{{
  "operation": "create" | "edit" | "delete" | "list",
  "summary": string | null,
  "start": ISO 8601 datetime string with offset | null,
  "end": ISO 8601 datetime string with offset | null,
  "location": string | null,
  "description": string | null,
  "search_hint": string | null,
  "changes": object | null,
  "rrule": string | null,
  "clarification_needed": string | null
}}

Rules:
- "operation" is always required.
- For "create": fill summary, start, end (if given), location, description, rrule.
- For "edit": fill search_hint (what to find), changes (what to update, same field names).
- For "delete": fill search_hint only.
- For "list": leave most fields null; use search_hint for time range description if given (e.g. "today", "this week").
- Resolve relative dates ("tomorrow", "next Tuesday", "in 2 hours") using the current datetime above.
- Missing end time: set end = start + 1 hour.
- Missing AM/PM: hours 1-5 → PM, hours 6-11 → AM, 12 → PM, unless context implies otherwise. If truly ambiguous, set clarification_needed with a question and leave start/end null.
- Recurring events: set rrule as an RFC 5545 RRULE string (e.g. "FREQ=WEEKLY;BYDAY=MO,WE,FR").
- Multi-day events: set start to the first day, end to the last day (use date-only ISO format if no times given).
- Events spanning midnight: end datetime will be the next calendar day — that is fine.
- search_hint should be a short human-readable description of the event to search for (used to query the calendar).
"""


def parse(text: str, now: datetime) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not set. Add it to your .env file.")

    client = genai.Client(api_key=api_key)

    tz_name = now.strftime("%Z") or "UTC"
    prompt = _SYSTEM_PROMPT.format(now=now.isoformat(), tz=tz_name)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{prompt}\n\nUser input: {text}",
        config=types.GenerateContentConfig(temperature=0),
    )

    raw = response.text.strip()
    # Strip accidental markdown code fences if the model adds them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)
