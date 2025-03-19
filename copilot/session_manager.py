import os
import json
from azure.data.tables import TableServiceClient

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
TABLE_NAME = "CopilotSessions"

def get_table_client():
    """Get Azure Table Storage client."""
    service_client = TableServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    return service_client.get_table_client(TABLE_NAME)

def get_user_session(user_id):
    """Fetch user session from Azure Table Storage."""
    table_client = get_table_client()
    try:
        session = table_client.get_entity(partition_key="session", row_key=user_id)
        return json.loads(session["Data"])
    except:
        return None

def save_user_session(user_id, session_data):
    """Save user session to Azure Table Storage."""
    table_client = get_table_client()
    entity = {
        "PartitionKey": "session",
        "RowKey": user_id,
        "Data": json.dumps(session_data)
    }
    table_client.upsert_entity(entity)
