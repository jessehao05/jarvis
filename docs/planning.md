## Main Components

- NLP extraction - handled by LLM
- Time resolution
- Google Calendar API
- Interface
- Google OAuth 2.0

## Intended Functionality

### Add events

Typical inputs might include: 

- 6:30pm study session at fgh
- study session on june 24 at 6:30pm at alumni hall
- study session next tuesday from 6:30 to 9pm at alumni hall

Example use for a CLI tool:  
`jarvis add "study session with will from 6:30pm to 9pm at alumni hall tomorrow"`

### Edit events (?)

Requires finding the event first.

Example use for a Mmlti-step CLI tool:
`jarvis search "tomorrow study session"`  
`jarvis edit 1 --start 4:30pm`

Example use for a smart NLP CLI tool:
`jarvis edit "change tomorrow's study session to 4:30pm"`

Example use for an chatbot-like interface:
`change tomorrow's study session to 4:30pm`

### Delete events (?)

Requires finding the event first.

Example use for a smart NLP CLI tool:
`jarvis delete "tomorrow's study session"`

> ### NOTE: Confirmations
> 
> Each time I create, edit, or delete an event, I want a message confirming the success of the action or notifiying me of any failures in the process.

## Edge Cases

Edge cases to consider for adding events:
- Ambigious inputs regarding AM/PM, like missing one (6:30 to 9pm, 6:30pm to 9) or both (6:30 to 9, 7:30, etc.)
- Events spanning midnight
- Events with a start time but not an end time
- Recurring events (every M, every T/Th)
- Multi-day events 
    - Events that happen at the same time
    - Events with different times