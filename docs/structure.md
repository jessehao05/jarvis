## File scope/responsibility

- main cli entrypoint: cli.py
    - imports from jarvis.core.__
- core logic: core/
    - google authentication for google calendar api: auth.py
    - google calendar api actions (add, delete, edit): calendar.py
    - nlp to structured format using gemini api: parser.py

## Command Surface Design

Standard shape for CLI tools: group + subcomamnds, which Jarvis follows. There is one group (`cli()`) and subcommands under the group (`add`/`edit`/`delete`/`list`).

## Thin CLI Layer

`cli.py` parses args, calls `jarvis.core.*`, and prints. All the Google/Gemini logic is in `core/`.

(test: could you build a web UI on `core/` without touching it? if yes, the boundary is right)

Helpers, `_find_events` / `_pick_event`, are right at the line - `_pick_event` fits in cli.py since it prompts but `_find_events` maybe should be in core. 