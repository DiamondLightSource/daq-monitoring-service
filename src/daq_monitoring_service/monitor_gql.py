import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import TypedDict, cast

import requests

KEYCLOAK_INSTANCE = (
    "https://identity-test.diamond.ac.uk/realms/dls/protocol/openid-connect/token"
)
# GRAPH_URL = "https://graph-nightly.diamond.ac.uk/graphql"
GRAPH_URL = "https://ulims-dev.diamond.ac.uk/graphql"

SESSION_STATE_FILE = "./data/last_sessions_state.json"


class ExperimentStatus(TypedDict):
    status: str


class SessionNode(TypedDict):
    instrumentSessionReference: str
    experimentStatus: ExperimentStatus | None


class SessionEdge(TypedDict):
    node: SessionNode


def get_token_from_keycloak(id: str, secret: str):
    response = requests.post(
        KEYCLOAK_INSTANCE,
        data={
            "grant_type": "client_credentials",
            "client_id": id,
            "client_secret": secret,
            "scope": "openid profile posix-uid",
        },
    )

    response.raise_for_status()
    access_token = response.json()["access_token"]

    return access_token


def get_session_statuses(token: str) -> list[SessionEdge]:
    graphql_query = """
    query GetSessionStatus($state: InstrumentSessionState!) {
        instrumentByKey(key: "I15-1") {
            instrumentSessions(filterBy: { state: {eq: $state } }) {
            edges {
                node {
                instrumentSessionReference
                experimentStatus {status}
                }
            }
            }
        }
    }"""
    sessions: list[SessionEdge] = []
    for state in ["IN_PROGRESS", "FUTURE"]:
        response = requests.post(
            GRAPH_URL,
            json={"query": graphql_query, "variable_values": {"state": state}},
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        session_data = response.json()
        sessions.extend(
            cast(
                list[SessionEdge],
                session_data["data"]["instrumentByKey"]["instrumentSessions"]["edges"],
            )
        )

    return sessions


def get_token():
    token = None  # os.getenv("MY_TOKEN")
    if token is None:
        print("Looking for client token")
        id = os.getenv("CLIENT_ID")
        secret = os.getenv("CLIENT_SECRET")
        if id is None or secret is None:
            raise Exception(
                "CLIENT_ID and CLIENT_SECRET must be set in environment variables"
            )
        token = get_token_from_keycloak(id, secret)
    return token


def get_changed_session_statuses(
    token: str,
    state_file: str | os.PathLike[str] = SESSION_STATE_FILE,
) -> dict[str, tuple[str | None, str | None]]:
    differences: dict[str, tuple[str | None, str | None]] = {}
    new_session_statuses: dict[str, str | None] = {
        session["node"]["instrumentSessionReference"]: (
            session["node"]["experimentStatus"]["status"]
            if session["node"]["experimentStatus"] is not None
            else None
        )
        for session in get_session_statuses(token)
    }

    if os.path.exists(state_file):
        with open(state_file) as f:
            old_session_statuses = cast(dict[str, str | None], json.load(f))

        for session, new_status in new_session_statuses.items():
            if session in old_session_statuses:
                old_status = old_session_statuses[session]
                if old_status != new_status:
                    differences[session] = (old_status, new_status)

    state_path = Path(state_file)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with state_path.open("w") as f:
        json.dump(new_session_statuses, f)

    return differences


def monitor_session_statuses(
    token: str,
    notify: Callable[[str], None],
) -> None:
    for session, (old_status, new_status) in get_changed_session_statuses(
        token
    ).items():
        notify(
            f'Session "{session}" status changed from "{old_status}" to "{new_status}"'
        )
