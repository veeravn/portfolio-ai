# File: copilot/session_manager.py

import os
import json
from .logging_helper import log_info, log_error
from azure.data.tables import TableServiceClient, UpdateMode
from azure.core.exceptions import ResourceNotFoundError

# Initialize the Table client once
_CONNECTION_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
if not _CONNECTION_STR:
    raise RuntimeError("Missing AZURE_STORAGE_CONNECTION_STRING connection string")
_service = TableServiceClient.from_connection_string(conn_str=_CONNECTION_STR)
_table = _service.get_table_client(table_name="sessions")


def save_user_session(user_id: str, session_data: dict) -> None:
    """
    Upserts a single entity per user into the 'sessions' table.
    - PartitionKey = session
    - RowKey       = "default_user" (a constant)
    - Data  = JSON blob of the session_data dict
    """
    entity = {
        "PartitionKey": "session",            # EXACT casing required
        "RowKey":       user_id,          # EXACT casing required
        "Data":  json.dumps(session_data)
    }

    log_info(f"[session_manager] upserting entity keys={list(entity.keys())} for user_id={user_id}")
    _table.upsert_entity(entity=entity, mode=UpdateMode.MERGE)


def get_user_session(user_id: str) -> dict:
    """
    Retrieves the saved session_data for a given user_id.
    Returns an empty dict if none exists.
    """
    try:
        ent = _table.get_entity(partition_key="session", row_key=user_id)
        return json.loads(ent["Data"])
    except ResourceNotFoundError:
        log_error("[session_manager] no existing session for user_id={user_id}")
        return {}
