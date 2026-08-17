# jarvis

A CLI tool for managing Google Calendar using natural language. Commands like `jarvis add "study session at 6pm tomorrow"` are parsed by an LLM into structured data and sent to the Google Calendar API.

## Project structure

```
jarvis/
├── src/
│   └── jarvis/
│       ├── cli.py          # Click commands (add, auth, delete, edit, help, list, test)
│       └── core/
│           ├── auth.py     # Google OAuth flow and service construction
│           ├── calendar.py # Google Calendar API calls
│           └── parser.py   # Gemini prompt and JSON parsing
├── docs/                   # Planning and design notes
├── .env.example
└── pyproject.toml
```

Configuration and secrets live outside the repo, in `~/.jarvis/`:

```
~/.jarvis/
├── .env                # GEMINI_API_KEY
├── credentials.json    # Google OAuth client secret
└── token.json          # written by `jarvis auth`
```

## Setup

**1. Install**

`jarvis` is meant to be a global command: install it once, then run it from any directory with no virtual environment to activate.

First install [uv](https://docs.astral.sh/uv/getting-started/installation/), which builds and manages that global environment:

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then open a new terminal so `uv` is on your PATH, and install jarvis:

```bash
uv tool install --editable path/to/jarvis
```

This builds an isolated environment for jarvis's dependencies and puts a `jarvis` shim on your PATH. `--editable` points the install at your source tree, so code edits take effect immediately — drop it if you'd rather have a frozen snapshot.

If the shell can't find `jarvis` afterwards, run `uv tool update-shell` and open a new terminal.

Code edits apply on their own, but changes to the dependencies in `pyproject.toml` need a rebuild:

```bash
uv tool install --editable --force path/to/jarvis
```

**2. (Optional) Create a virtual environment for development**

Only needed to work on jarvis in isolation — for example to try an unreleased branch without disturbing the global install. Day-to-day use doesn't require it.

```bash
cd path/to/jarvis
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
```

Using `uv` here rather than `python -m venv` and `pip` keeps the development environment resolving the same way as the global one, so the two don't drift onto different dependency versions.

**3. Get a Gemini API key**

Go to [Google AI Studio](https://aistudio.google.com/app/apikey), create a key, then copy `.env.example` to `~/.jarvis/.env` and fill it in:

```bash
mkdir -p ~/.jarvis
cp .env.example ~/.jarvis/.env
# edit ~/.jarvis/.env and set GEMINI_API_KEY=...
```

**4. Get Google Calendar credentials**

In [Google Cloud Console](https://console.cloud.google.com):
- Enable the **Google Calendar API**
- Create an OAuth 2.0 credential (Desktop app)
- Download the JSON and save it as `~/.jarvis/credentials.json`

**5. Authenticate**

```bash
jarvis auth
```

This opens a browser for the OAuth flow and saves a token to `~/.jarvis/token.json`. Only needed once.

## Usage

Run these from anywhere — jarvis reads its configuration from `~/.jarvis/`, never from the current directory.

```bash
jarvis help

jarvis add "team standup every Monday at 9am"
jarvis add "dentist appointment Friday at 3pm for 45 minutes"

jarvis edit "move standup to 10am"
jarvis delete "dentist"

jarvis list          # today's events
jarvis list week     # next 7 days

jarvis test          # smoke test: verify Gemini + Calendar connectivity
```

