from collections.abc import Callable
from typing import TypedDict, cast

import requests

QUEUE_STATE_URL = "https://i15-1-daq-queue.diamond.ac.uk/queue/state"


class QueueState(TypedDict):
    paused: bool
    last_pause_reason: str | None


def get_queue_state() -> QueueState:
    response = requests.get(
        QUEUE_STATE_URL,
        headers={"accept": "*/*"},
        timeout=10,
    )
    response.raise_for_status()
    return cast(QueueState, response.json())


def queue_has_paused(previous: QueueState, current: QueueState) -> bool:
    return not previous["paused"] and current["paused"]


def monitor_queue(
    previous: QueueState | None,
    notify: Callable[[str], None],
) -> QueueState:
    current = get_queue_state()
    if previous is not None and queue_has_paused(previous, current):
        reason = current["last_pause_reason"] or "No reason provided"
        notify(f"DAQ queue paused: {reason}")
    return current
