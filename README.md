# jarvis

A CLI tool for managing Google Calendar using natural language. Commands like `jarvis add "study session at 6pm tomorrow"` are parsed by an LLM into structured data and sent to the Google Calendar API.

## Project structure

```
jarvis/
├── src/
│   └── jarvis/
│       ├── cli.py          # Click commands (add, edit, delete, list, test)
│       └── core/
│           ├── auth.py     # Google OAuth flow and service construction
│           ├── calendar.py # Google Calendar API calls
│           └── parser.py   # Gemini prompt and JSON parsing
├── .env.example
├── credentials.json    # (not committed) Google OAuth client secret
└── pyproject.toml
```

## Setup

**1. Install**

```bash
cd path/to/jarvis
pip install -e .
```

**2. (Optional) Create a virtual environment for development**

This step can be skipped if you only wish to run this project, not make any changes (development).

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

**3. Get a Gemini API key**

Go to [Google AI Studio](https://aistudio.google.com/app/apikey), create a key, then copy `.env.example` to `.env` and fill it in:

```bash
cp .env.example .env
# edit .env and set GEMINI_API_KEY=...
```

**4. Get Google Calendar credentials**

In [Google Cloud Console](https://console.cloud.google.com):
- Enable the **Google Calendar API**
- Create an OAuth 2.0 credential (Desktop app)
- Download the JSON and save it as `credentials.json` in the project root

**5. Authenticate**

```bash
jarvis auth
```

This opens a browser for the OAuth flow and saves a token to `~/.jarvis/token.json`. Only needed once.

## Usage

```bash
jarvis add "team standup every Monday at 9am"
jarvis add "dentist appointment Friday at 3pm for 45 minutes"

jarvis edit "move standup to 10am"
jarvis delete "dentist"

jarvis list          # today's events
jarvis list week     # next 7 days

jarvis test          # smoke test: verify Gemini + Calendar connectivity
```

