import json
from pathlib import Path
from unittest.mock import Mock, patch

from daq_monitoring_service import monitor_gql

INITIAL_STATE = {"CM12168-1": None, "CM12168-2": None}


@patch("daq_monitoring_service.monitor_gql.get_session_statuses")
def test_get_changed_session_statuses_creates_state_file(
    get_session_statuses: Mock,
    tmp_path: Path,
):
    state_file = tmp_path / "data" / "last_sessions_state.json"
    get_session_statuses.return_value = [
        {
            "node": {
                "instrumentSessionReference": "CM12168-1",
                "experimentStatus": None,
            }
        }
    ]

    assert monitor_gql.get_changed_session_statuses("token", state_file) == {}
    assert json.loads(state_file.read_text()) == {"CM12168-1": None}


@patch("daq_monitoring_service.monitor_gql.get_session_statuses")
def test_get_changed_session_statuses(
    get_session_statuses: Mock,
    tmp_path: Path,
):
    state_file = tmp_path / "last_sessions_state.json"
    state_file.write_text(json.dumps(INITIAL_STATE))
    sessions: list[monitor_gql.SessionEdge] = [
        {
            "node": {
                "instrumentSessionReference": "CM12168-1",
                "experimentStatus": None,
            }
        },
        {
            "node": {
                "instrumentSessionReference": "CM12168-1",
                "experimentStatus": None,
            }
        },
    ]
    get_session_statuses.return_value = sessions

    assert monitor_gql.get_changed_session_statuses("token", state_file) == {}

    sessions[0]["node"]["experimentStatus"] = {"status": "SUBMITTED"}
    sessions[1]["node"]["experimentStatus"] = {"status": "SUBMITTED"}

    assert monitor_gql.get_changed_session_statuses("token", state_file) == {
        "CM12168-1": (None, "SUBMITTED")
    }
    assert json.loads(state_file.read_text()) == {"CM12168-1": "SUBMITTED"}


@patch("daq_monitoring_service.monitor_gql.get_changed_session_statuses")
def test_monitor_session_statuses(get_changed_session_statuses: Mock):
    get_changed_session_statuses.return_value = {"CM12168-1": (None, "SUBMITTED")}
    notify = Mock()

    monitor_gql.monitor_session_statuses("token", notify)

    notify.assert_called_once_with(
        'Session "CM12168-1" status changed from "None" to "SUBMITTED"'
    )
