import os

import requests


def send_slack_message(message: str):
    webhook_url = os.getenv("SLACK_WEBHOOK")
    if not webhook_url:
        raise Exception("Slack webhook needed in SLACK_WEBHOOK env variable")

    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{message}",
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": (
                            "Triggered by <https://github.com/DiamondLightSource/"
                            "daq-monitoring-service%7CDAQ-monitoring-service>"
                        ),
                    }
                ],
            },
        ]
    }
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print(f"Message sent to Slack {message}")
    except Exception as e:
        print(f"Failed to send message to Slack: {e} at URL: {webhook_url}")
