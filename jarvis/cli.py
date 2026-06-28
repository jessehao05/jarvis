from datetime import datetime, timedelta, timezone

import click

from jarvis.core.auth import get_calendar_service
from jarvis.core.calendar import (
    create_event,
    delete_event,
    edit_event,
    list_events,
    search_events,
)
from jarvis.core.parser import parse


@click.group()
def cli():
    pass


@cli.command()
def auth():
    """Run the one-time Google OAuth setup."""
    get_calendar_service()
    click.echo("Auth complete. Token saved to ~/.jarvis/token.json")


@cli.command()
@click.argument("text")
def add(text):
    """Create a calendar event from natural language."""
    now = datetime.now(tz=timezone.utc).astimezone()
    parsed = parse(text, now)

    if parsed.get("clarification_needed"):
        click.echo(f"Clarification needed: {parsed['clarification_needed']}")
        return

    service = get_calendar_service()
    click.echo(create_event(service, parsed))


@cli.command()
@click.argument("text")
def edit(text):
    """Edit a calendar event from natural language."""
    now = datetime.now(tz=timezone.utc).astimezone()
    parsed = parse(text, now)

    if parsed.get("clarification_needed"):
        click.echo(f"Clarification needed: {parsed['clarification_needed']}")
        return

    service = get_calendar_service()
    hint = parsed.get("search_hint") or parsed.get("summary") or text
    events = _find_events(service, hint, now)

    if not events:
        click.echo("No matching events found.")
        return

    event = _pick_event(events)
    if event is None:
        return

    changes = parsed.get("changes") or {}
    click.echo(edit_event(service, event["id"], changes))


@cli.command()
@click.argument("text")
def delete(text):
    """Delete a calendar event from natural language."""
    now = datetime.now(tz=timezone.utc).astimezone()
    parsed = parse(text, now)

    service = get_calendar_service()
    hint = parsed.get("search_hint") or parsed.get("summary") or text
    events = _find_events(service, hint, now)

    if not events:
        click.echo("No matching events found.")
        return

    event = _pick_event(events)
    if event is None:
        return

    click.echo(delete_event(service, event["id"]))


@cli.command(name="list")
@click.argument("period", default="today", type=click.Choice(["today", "week"]))
def list_cmd(period):
    """List upcoming events (today or this week)."""
    now = datetime.now(tz=timezone.utc).astimezone()
    if period == "today":
        time_max = now.replace(hour=23, minute=59, second=59)
    else:
        time_max = now + timedelta(days=7)

    service = get_calendar_service()
    click.echo(list_events(service, now, time_max))


def _find_events(service, hint: str, now: datetime) -> list:
    time_min = now - timedelta(days=1)
    time_max = now + timedelta(days=30)
    return search_events(service, hint, time_min, time_max)


def _pick_event(events: list) -> dict | None:
    if len(events) == 1:
        event = events[0]
        summary = event.get("summary", "(no title)")
        start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date", "")
        click.echo(f"Found: {summary} — {start}")
        if not click.confirm("Confirm?", default=False):
            return None
        return event

    click.echo("Multiple events found:")
    for i, e in enumerate(events):
        summary = e.get("summary", "(no title)")
        start = e.get("start", {}).get("dateTime") or e.get("start", {}).get("date", "")
        click.echo(f"  {i + 1}. {summary} — {start}")

    choice = click.prompt("Which event?", type=click.IntRange(1, len(events)))
    return events[choice - 1]
