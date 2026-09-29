from unittest.mock import Mock, patch

from daq_monitoring_service import monitor_queue


@patch("daq_monitoring_service.monitor_queue.requests.get")
def test_get_queue_state(get: Mock):
    response = Mock()
    response.json.return_value = {
        "paused": True,
        "last_pause_reason": "Paused as queue completed",
    }
    get.return_value = response

    assert monitor_queue.get_queue_state() == response.json.return_value
    get.assert_called_once_with(
        monitor_queue.QUEUE_STATE_URL,
        headers={"accept": "*/*"},
        timeout=10,
    )
    response.raise_for_status.assert_called_once_with()


@patch("daq_monitoring_service.monitor_queue.get_queue_state")
def test_monitor_notifies_only_when_queue_becomes_paused(
    get_queue_state: Mock,
):
    get_queue_state.side_effect = [
        {"paused": False, "last_pause_reason": None},
        {"paused": True, "last_pause_reason": "Queue completed"},
    ]
    notify = Mock()

    previous = monitor_queue.monitor_queue(None, notify)
    current = monitor_queue.monitor_queue(previous, notify)

    assert current == {"paused": True, "last_pause_reason": "Queue completed"}
    notify.assert_called_once_with("DAQ queue paused: Queue completed")
