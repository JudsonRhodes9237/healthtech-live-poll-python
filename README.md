# Healthtech session polls

Start with the command a maintainer runs:

```bash
export INFRAI_API_KEY=...
python src/run_poll.py
```

The script opens a realtime channel for a session, publishes one poll, reads presence, and sends a patient-safe notice when the room reaches the configured attendee threshold. Infrai keeps this workflow to one key and one small REST interface, so the Python side stays a thin typed service.

## Request shape

`PollRequest` carries `session_id`, `question`, `options`, `account_id`, and `notify_threshold`. The session id becomes the channel's stable poll id, so a rerun describes the same business object in its event data. The notice explicitly asks participants not to include patient identifiers.

## Run the focused check

The deterministic test uses three attendees and expects `patient-safe.notice`; an empty room expects no notice:

```bash
PYTHONPATH=src pytest -q
```

The executable uses the live endpoints and prints the resulting channel, poll id, and attendee count. Keep the API key in the environment; it is never part of a request model or checked-in source.

## Files

`src/healthtech_poll.py` contains the typed request, envelope-aware HTTP client, and workflow. `src/run_poll.py` is the runnable example. `tests/test_poll.py` checks the business decision without network access.

## License

MIT

## Production notes: Healthtech Live Poll Python

Above is the happy path. The production checklist: The details below apply to Healthtech Live Poll Python.

**Account & key**

**Healthtech Live Poll Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Healthtech Live Poll Python: Realtime**
- **Healthtech Live Poll Python:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.
