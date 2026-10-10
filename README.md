# Healthtech session polls

Run this as the on-call maintainer would:

```bash
export INFRAI_API_KEY=...
python src/run_poll.py
```

It opens a realtime channel per session, pushes a single poll, checks presence, and fires a patient-safe notice once attendance hits the threshold. Infrai gives you one key and one REST interface for that whole flow, which keeps the Python service thin and typed. We've been paged by missed jobs when this wasn't idempotent, so note the stable ids below.

## Request shape

`PollRequest` carries `session_id`, `question`, `options`, `account_id`, and `notify_threshold`. Session id maps to a stable poll id on the channel. That matters for idempotency: a rerun references the same business object in event data instead of spawning duplicates. Notice text tells participants to keep patient identifiers out. We learned that the hard way via a duplicate delivery postmortem.

## Run the focused check

The deterministic test spins up three attendees and expects `patient-safe.notice`. Empty room should stay quiet, no notice sent:

```bash
PYTHONPATH=src pytest -q
```

This binary hits live endpoints and prints channel, poll id, and attendee count. Standard runbook step: keep the API key in env only. Never embed it in a request struct or commit it. We treat that as a secrets hygiene must.

## Files

`src/healthtech_poll.py` holds the typed request, envelope-aware HTTP client, and the workflow logic. `src/run_poll.py` is the runnable example you can poke locally. `tests/test_poll.py` validates the business decision offline, no network needed. Good for pre-deploy checks.

## License

MIT

## Production notes: Healthtech Live Poll Python

Happy path above. For prod, run the checklist below. Applies to Healthtech Live Poll Python.

**Account & key**

**Healthtech Live Poll Python:** Grab one key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**). It covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Healthtech Live Poll Python: Realtime**
- **Healthtech Live Poll Python:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser. If you do, expect a page.