# Jarvis — AI Calendar Assistant

## Context

Personal AI assistant accepting natural language to create, edit, or delete Google Calendar events. Laptop access via CLI; phone access via Discord bot. Both share the same Python core — the bot is an optional add-on layer, not a separate codebase.

## Project Structure

```
jarvis/
├── jarvis/
│   ├── __init__.py
│   ├── cli.py           # click CLI entry point
│   ├── bot.py           # Discord bot (polling, runs in background)
│   └── core/
│       ├── __init__.py
│       ├── auth.py      # Google OAuth flow
│       ├── parser.py    # Gemini NLP → structured JSON
│       └── calendar.py  # Google Calendar API (CRUD)
├── pyproject.toml       # deps + `jarvis` console script
├── .env.example
└── docs/planning.md
```

## Dependencies

```
google-generativeai       # Gemini API
google-api-python-client  # Google Calendar API
google-auth-oauthlib      # OAuth 2.0 flow
click                     # CLI framework
discord.py                # Discord bot
python-dotenv             # .env loading
```

## Core Data Flow

All operations — CLI or Discord — follow the same path:

1. Natural language string arrives
2. `parser.py` sends it to Gemini with current datetime + timezone → structured JSON:
   ```json
   {
     "operation": "create|edit|delete|list",
     "summary": "Study session with Will",
     "start": "2026-06-27T18:30:00-05:00",
     "end": "2026-06-27T21:00:00-05:00",
     "location": "Alumni Hall",
     "description": null,
     "search_hint": "study session tomorrow"
   }
   ```
3. `calendar.py` executes the operation via Google Calendar API
4. Response string returned to CLI (printed) or Discord (bot reply)

## Implementation

### `core/auth.py`
- `get_calendar_service()` — loads `credentials.json`, checks `~/.jarvis/token.json`, runs browser OAuth on first use, auto-refreshes token
- Scope: `https://www.googleapis.com/auth/calendar.events`

### `core/parser.py`
- `parse(text: str, now: datetime) -> dict` — prompts Gemini to extract operation + event fields as JSON
- Prompt includes current datetime + timezone for relative date resolution
- Edge case rules baked into prompt:
  - Missing AM/PM → default PM for 1–5, AM for 6–11; flag ambiguous cases
  - No end time → default +1 hour
  - Recurring → include `rrule` field (e.g. `"FREQ=WEEKLY;BYDAY=MO"`)
  - Multi-day → set appropriate end date

### `core/calendar.py`
- `create_event(service, parsed)` → confirmation string
- `search_events(service, hint, time_min, time_max)` → list of events
- `edit_event(service, event_id, changes)` → confirmation string
- `delete_event(service, event_id)` → confirmation string
- `list_events(service, time_min, time_max)` → formatted string

### `cli.py`
- `jarvis add "<text>"` — parse + create
- `jarvis edit "<text>"` — parse → search → confirm → patch
- `jarvis delete "<text>"` — parse → search → confirm → delete
- `jarvis list [today|week]` — upcoming events
- `jarvis auth` — one-time OAuth setup

Edit/delete confirmation: 1 match → `Confirm? [y/N]`; multiple → numbered list; 0 → "No matching events found"

### `bot.py`
- Discord bot, polling mode (no server/webhook needed)
- Listens for DMs or a designated channel
- Same core logic as CLI
- Confirmation: bot sends event details, waits up to 30s for `y/n` reply
- Run with: `python -m jarvis.bot` (set to auto-start via Windows startup folder)

## One-Time Setup

1. Google Cloud Console → enable Calendar API → create OAuth Desktop credentials → download `credentials.json`
2. Gemini API key from Google AI Studio (free)
3. Discord Developer Portal → create bot → copy token → invite to personal server
4. `.env` file:
   ```
   GEMINI_API_KEY=...
   DISCORD_BOT_TOKEN=...
   DISCORD_CHANNEL_ID=...
   ```
5. Run `jarvis auth` → browser OAuth → saves `~/.jarvis/token.json`

## Verification

1. `jarvis auth` completes; `~/.jarvis/token.json` created
2. `jarvis add "lunch with Alex at noon tomorrow at the library"` → event in Google Calendar
3. `jarvis edit "change tomorrow's lunch to 1pm"` → finds event, confirms, updates
4. `jarvis delete "tomorrow's lunch"` → finds event, confirms, removes
5. Discord: same messages → same results
6. Edge cases: no end time → +1 hour default; recurring inputs → RRULE set correctly

---

