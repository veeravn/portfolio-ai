# File: copilot/session_manager.py

import os
import json
from .logging_helper import log_info, log_error
from azure.data.tables import TableServiceClient, UpdateMode
from azure.core.exceptions import ResourceNotFoundError
from config.env import AZURE_STORAGE_CONNECTION_STRING

# Initialize the Table client once
if not AZURE_STORAGE_CONNECTION_STRING:
    raise RuntimeError("Missing AZURE_STORAGE_CONNECTION_STRING connection string")
_service = TableServiceClient.from_connection_string(conn_str=AZURE_STORAGE_CONNECTION_STRING)
_table = _service.get_table_client(table_name="CopilotSessions")

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

def delete_user_session(user_id: str) -> None:
    """
    Deletes the stored session for the given user_id.
    """
    _table.delete_entity(partition_key="session", row_key=user_id)
