from datetime import datetime, timedelta, timezone


def _format_event(event: dict) -> str:
    summary = event.get("summary", "(no title)")
    start = event.get("start", {})
    start_str = start.get("dateTime") or start.get("date", "")
    location = event.get("location", "")
    loc_part = f" @ {location}" if location else ""
    return f"{summary} — {start_str}{loc_part}  [id: {event['id']}]"


def create_event(service, parsed: dict) -> str:
    body = {"summary": parsed.get("summary")}

    for field in ("location", "description"):
        if parsed.get(field):
            body[field] = parsed[field]

    start = parsed.get("start")
    end = parsed.get("end")
    if start:
        body["start"] = {"dateTime": start, "timeZone": "UTC"}
        body["end"] = {"dateTime": end or _add_one_hour(start), "timeZone": "UTC"}

    if parsed.get("rrule"):
        body["recurrence"] = [f"RRULE:{parsed['rrule']}"]

    event = service.events().insert(calendarId="primary", body=body).execute()
    return f"Created: {_format_event(event)}"


def search_events(service, hint: str, time_min: datetime, time_max: datetime) -> list:
    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=time_min.isoformat(),
            timeMax=time_max.isoformat(),
            q=hint,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return result.get("items", [])


def edit_event(service, event_id: str, changes: dict) -> str:
    event = service.events().get(calendarId="primary", eventId=event_id).execute()

    for key, value in changes.items():
        if key in ("start", "end"):
            tz = event.get(key, {}).get("timeZone", "UTC")
            event[key] = {"dateTime": value, "timeZone": tz}
        else:
            event[key] = value

    updated = (
        service.events()
        .update(calendarId="primary", eventId=event_id, body=event)
        .execute()
    )
    return f"Updated: {_format_event(updated)}"


def delete_event(service, event_id: str) -> str:
    service.events().delete(calendarId="primary", eventId=event_id).execute()
    return "Deleted."


def list_events(service, time_min: datetime, time_max: datetime) -> str:
    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=time_min.isoformat(),
            timeMax=time_max.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = result.get("items", [])
    if not events:
        return "No events found."
    return "\n".join(f"  {i+1}. {_format_event(e)}" for i, e in enumerate(events))


def _add_one_hour(dt_str: str) -> str:
    dt = datetime.fromisoformat(dt_str)
    return (dt + timedelta(hours=1)).isoformat()
