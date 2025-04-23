import os
import json
from azure.data.tables import TableServiceClient, UpdateMode

TABLE_NAME = os.getenv("AZ_TABLE_NAME", "sessions")
CONNECTION_STR = os.getenv("AZ_TABLE_CONNECTION")
svc_client = TableServiceClient.from_connection_string(CONNECTION_STR)
table_client = svc_client.get_table_client(TABLE_NAME)

def get_user_session(user_id: str) -> dict:
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
    table_client.upsert_entity(entity, mode=UpdateMode.MERGE)

