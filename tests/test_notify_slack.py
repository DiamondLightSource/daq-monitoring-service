from unittest.mock import Mock, patch

from daq_monitoring_service.notify_slack import send_slack_message


@patch("daq_monitoring_service.notify_slack.requests.post")
@patch.dict("os.environ", {"SLACK_WEBHOOK": "https://example.com/webhook"})
def test_send_slack_message(post: Mock):
    send_slack_message("Run failed")

    post.assert_called_once_with(
        "https://example.com/webhook",
        json={
            "message": "Run failed",
            "sent_by_url": "https://github.com/DiamondLightSource/daq-monitoring-service%7CDAQ-monitoring-service",
        },
    )
    post.return_value.raise_for_status.assert_called_once_with()
