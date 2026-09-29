from healthtech_poll import PollRequest, run_poll


class FakeClient:
    def __init__(self, attendees):
        self.attendees = attendees
        self.events = []

    def create_channel(self, channel):
        self.events.append(("create", channel))

    def publish(self, channel, event, data, account_id):
        self.events.append((event, data))

    def presence(self, channel):
        return {"count": self.attendees}


def test_patient_safe_notice_is_sent_when_session_has_attendees():
    client = FakeClient(3)
    result = run_poll(client, PollRequest("s1", "Ready?", ("Yes", "No"), "acct", notify_threshold=2))
    assert result["attendees"] == 3
    assert any(event[0] == "patient-safe.notice" for event in client.events)


def test_notice_is_not_sent_for_empty_room():
    client = FakeClient(0)
    run_poll(client, PollRequest("s2", "Ready?", ("Yes", "No"), "acct"))
    assert not any(event[0] == "patient-safe.notice" for event in client.events)
