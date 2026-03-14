from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from altryx.connectors.sql_connector import (
    test_connection,
    list_tables,
    list_columns,
    preview_table,
)

router = APIRouter(prefix="/api/connectors", tags=["connectors"])


class ConnectionTestRequest(BaseModel):
    connection_string: str


class TableRequest(BaseModel):
    connection_string: str
    table_name: str | None = None


class GoogleDriveAuthRequest(BaseModel):
    client_id: str
    redirect_uri: str
    state: str = ""


class GoogleDriveTokenRequest(BaseModel):
    code: str
    client_id: str
    client_secret: str
    redirect_uri: str


class GoogleDriveRefreshRequest(BaseModel):
    refresh_token: str
    client_id: str
    client_secret: str


class GoogleDriveListRequest(BaseModel):
    oauth_token: str = ""
    credentials_json: str = ""
    folder_id: str = ""
    file_pattern: str = "*"
    recursive: bool = False


@router.post("/test")
def test_db_connection(body: ConnectionTestRequest) -> dict[str, Any]:
    return test_connection(body.connection_string)


@router.post("/tables")
def get_tables(body: ConnectionTestRequest) -> dict[str, list[str]]:
    tables = list_tables(body.connection_string)
    return {"tables": tables}


@router.post("/columns")
def get_columns(body: TableRequest) -> dict[str, Any]:
    if not body.table_name:
        return {"columns": []}
    cols = list_columns(body.connection_string, body.table_name)
    return {"columns": cols}


@router.post("/preview")
def preview(body: TableRequest) -> dict[str, Any]:
    if not body.table_name:
        return {"columns": [], "row_count": 0, "data": []}
    return preview_table(body.connection_string, body.table_name)


# --- Google Drive endpoints ---

@router.post("/google-drive/auth-url")
def google_drive_auth_url(body: GoogleDriveAuthRequest) -> dict[str, str]:
    """Get the OAuth2 authorization URL to redirect the user to."""
    from altryx.connectors.google_drive import build_oauth_url
    url = build_oauth_url(body.client_id, body.redirect_uri, body.state)
    return {"auth_url": url}


@router.post("/google-drive/token")
def google_drive_token(body: GoogleDriveTokenRequest) -> dict[str, Any]:
    """Exchange an authorization code for access + refresh tokens."""
    from altryx.connectors.google_drive import exchange_code_for_token
    return exchange_code_for_token(body.code, body.client_id, body.client_secret, body.redirect_uri)


@router.post("/google-drive/refresh")
def google_drive_refresh(body: GoogleDriveRefreshRequest) -> dict[str, Any]:
    """Refresh an expired access token."""
    from altryx.connectors.google_drive import refresh_access_token
    return refresh_access_token(body.refresh_token, body.client_id, body.client_secret)


@router.post("/google-drive/list")
def google_drive_list_files(body: GoogleDriveListRequest) -> dict[str, Any]:
    """List files in a Google Drive folder."""
    from altryx.connectors.google_drive import GoogleDriveConnector
    try:
        connector = GoogleDriveConnector(
            credentials=body.credentials_json,
            oauth_token=body.oauth_token,
        )
        files = connector.list_files(
            folder_id=body.folder_id,
            recursive=body.recursive,
            file_pattern=body.file_pattern,
        )
        return {"files": files, "count": len(files)}
    except Exception as e:
        return {"error": str(e), "files": [], "count": 0}
