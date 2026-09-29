"""Interface for ``python -m daq_monitoring_service``."""

import time
from collections.abc import Sequence

from daq_monitoring_service.monitor_gql import get_token, monitor_session_statuses
from daq_monitoring_service.monitor_queue import monitor_queue
from daq_monitoring_service.notify_slack import send_slack_message

__all__ = ["main"]

POLL_INTERVAL_SECONDS = 5


def main(args: Sequence[str] | None = None) -> None:
    token = get_token()
    previous_queue_state = None

    while True:
        monitor_session_statuses(token, send_slack_message)
        previous_queue_state = monitor_queue(previous_queue_state, send_slack_message)
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
