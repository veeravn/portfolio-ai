import os
import json
from azure.data.tables import TableClient, UpdateMode
from copilot.logging_helper import log_info

TABLE_NAME = "CopilotSessions"
CONNECTION_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

def get_user_session(user_id: str) -> dict:
    
    with TableClient.from_connection_string(
        conn_str=CONNECTION_STR, table_name=TABLE_NAME
        ) as table_client:
            try:
                entity = table_client.get_entity(partition_key="user", row_key=user_id)
                return json.loads(entity.get("session_data", "{}"))
            except:
                return {"history": []}

def save_user_session(user_id: str, session_data: dict) -> None:
    entity = {
        "PartitionKey": "user",
        "RowKey": user_id,
        "session_data": json.dumps(session_data)
    }
    # Debug: log what you’re actually sending
    log_info(f"About to upsert Table entity with keys: {list(entity.keys())}")
    with TableClient.from_connection_string(
       conn_str=CONNECTION_STR, table_name=TABLE_NAME
       ) as table_client:
            table_client.upsert_entity(entity, mode=UpdateMode.MERGE)

