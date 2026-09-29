import json

from healthtech_poll import InfraiClient, PollRequest, run_poll


if __name__ == "__main__":
    result = run_poll(
        InfraiClient(),
        PollRequest("session-042", "Which follow-up format helps most?", ("Video", "Phone", "Portal"), "demo-account"),
    )
    print(json.dumps(result, indent=2))
