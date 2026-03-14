"""
Google Drive connector — list, download, and read files from Google Drive.

Supports two auth methods:
1. Service Account JSON key file (for server-to-server, no user interaction)
2. OAuth2 token (for user-facing flows, token obtained via frontend)

Uses the Google Drive REST API v3 directly via httpx (no heavy SDK dependency).
"""
import io
import os
import fnmatch
from typing import Any, Optional

import httpx
import pandas as pd


DRIVE_API = "https://www.googleapis.com/drive/v3"
DRIVE_UPLOAD_API = "https://www.googleapis.com/upload/drive/v3"

# MIME type mappings
GOOGLE_SHEETS_MIME = "application/vnd.google-apps.spreadsheet"
GOOGLE_DOCS_MIME = "application/vnd.google-apps.document"
EXPORT_MIMES = {
    GOOGLE_SHEETS_MIME: "text/csv",
    GOOGLE_DOCS_MIME: "text/plain",
}


class GoogleDriveConnector:
    """Connect to Google Drive using a service account key or OAuth token."""

    def __init__(self, credentials: str = "", oauth_token: str = ""):
        """
        Parameters
        ----------
        credentials : str
            Path to a service account JSON key file, OR the JSON string itself.
        oauth_token : str
            A valid OAuth2 access token (obtained via frontend OAuth flow).
        """
        self._token: Optional[str] = None

        if oauth_token:
            self._token = oauth_token
        elif credentials:
            self._token = self._get_service_account_token(credentials)

        if not self._token:
            raise ValueError(
                "Google Drive connector requires either a service account "
                "JSON key path (credentials) or an OAuth access token (oauth_token)"
            )

    def _get_service_account_token(self, credentials: str) -> str:
        """Exchange a service account key for an access token using JWT."""
        import json
        import time
        import base64
        import hashlib
        import hmac

        # Load the key
        if os.path.isfile(credentials):
            with open(credentials) as f:
                key_data = json.load(f)
        else:
            key_data = json.loads(credentials)

        # For service accounts, we need to create a JWT and exchange it
        # This uses the google-auth library if available, otherwise falls back
        try:
            from google.oauth2 import service_account as sa
            from google.auth.transport.requests import Request

            creds = sa.Credentials.from_service_account_info(
                key_data,
                scopes=["https://www.googleapis.com/auth/drive.readonly"],
            )
            creds.refresh(Request())
            return creds.token
        except ImportError:
            # Fallback: use the JWT approach manually
            return self._jwt_exchange(key_data)

    def _jwt_exchange(self, key_data: dict) -> str:
        """Manual JWT-based token exchange for service accounts."""
        import json
        import time

        try:
            import jwt as pyjwt
        except ImportError:
            raise ImportError(
                "Install PyJWT (`pip install PyJWT cryptography`) or "
                "google-auth (`pip install google-auth`) for service account auth"
            )

        now = int(time.time())
        payload = {
            "iss": key_data["client_email"],
            "scope": "https://www.googleapis.com/auth/drive.readonly",
            "aud": "https://oauth2.googleapis.com/token",
            "iat": now,
            "exp": now + 3600,
        }

        signed = pyjwt.encode(payload, key_data["private_key"], algorithm="RS256")

        resp = httpx.post(
            "https://oauth2.googleapis.com/token",
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": signed,
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token}"}

    # ------------------------------------------------------------------
    # List files
    # ------------------------------------------------------------------
    def list_files(
        self,
        folder_id: str = "",
        recursive: bool = False,
        file_pattern: str = "*",
    ) -> list[dict[str, Any]]:
        """List files in a Google Drive folder.

        Returns a list of dicts with: FileName, FileId, MimeType, SizeBytes,
        ModifiedDate, FullPath.
        """
        query_parts = ["trashed = false"]
        if folder_id:
            query_parts.append(f"'{folder_id}' in parents")

        query = " and ".join(query_parts)
        fields = "nextPageToken, files(id, name, mimeType, size, modifiedTime, parents)"

        all_files: list[dict[str, Any]] = []
        page_token = None

        while True:
            params: dict[str, Any] = {
                "q": query,
                "fields": fields,
                "pageSize": 1000,
            }
            if page_token:
                params["pageToken"] = page_token

            resp = httpx.get(
                f"{DRIVE_API}/files",
                headers=self._headers(),
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

            for f in data.get("files", []):
                name = f["name"]
                # Apply file pattern filter
                if not fnmatch.fnmatch(name, file_pattern):
                    continue

                # Skip Google Apps native files unless they're Sheets
                mime = f.get("mimeType", "")
                if mime.startswith("application/vnd.google-apps.") and mime != GOOGLE_SHEETS_MIME:
                    continue

                all_files.append({
                    "FileName": name,
                    "FileId": f["id"],
                    "MimeType": mime,
                    "SizeBytes": int(f.get("size", 0)),
                    "ModifiedDate": f.get("modifiedTime", ""),
                    "FullPath": f"gdrive://{folder_id or 'root'}/{name}",
                })

                # Recurse into subfolders
                if recursive and mime == "application/vnd.google-apps.folder":
                    sub_files = self.list_files(f["id"], recursive=True, file_pattern=file_pattern)
                    all_files.extend(sub_files)

            page_token = data.get("nextPageToken")
            if not page_token:
                break

        return all_files

    # ------------------------------------------------------------------
    # Download a single file
    # ------------------------------------------------------------------
    def download_file(self, file_id: str, mime_type: str = "") -> bytes:
        """Download file content as bytes.

        For Google Sheets, exports as CSV. For regular files, downloads directly.
        """
        if mime_type in EXPORT_MIMES:
            # Export Google native format
            export_mime = EXPORT_MIMES[mime_type]
            resp = httpx.get(
                f"{DRIVE_API}/files/{file_id}/export",
                headers=self._headers(),
                params={"mimeType": export_mime},
            )
        else:
            resp = httpx.get(
                f"{DRIVE_API}/files/{file_id}",
                headers=self._headers(),
                params={"alt": "media"},
            )

        resp.raise_for_status()
        return resp.content

    # ------------------------------------------------------------------
    # Read files into DataFrames
    # ------------------------------------------------------------------
    def read_files(
        self,
        folder_id: str = "",
        file_pattern: str = "*.*",
        reader: str = "csv",
        add_filename_column: bool = True,
    ) -> list[pd.DataFrame]:
        """List + download + parse files from a Google Drive folder."""
        file_list = self.list_files(folder_id, file_pattern=file_pattern)

        frames = []
        for file_info in file_list:
            try:
                content = self.download_file(
                    file_info["FileId"],
                    file_info.get("MimeType", ""),
                )
                df = self._parse_content(content, file_info, reader)
                if add_filename_column:
                    df["FileName"] = file_info["FileName"]
                frames.append(df)
            except Exception:
                continue  # skip unreadable files

        return frames

    def read_single_file(
        self,
        file_id: str,
        mime_type: str = "",
        reader: str = "csv",
        **kwargs,
    ) -> pd.DataFrame:
        """Download and parse a single file."""
        content = self.download_file(file_id, mime_type)
        return self._parse_content(content, {"MimeType": mime_type}, reader, **kwargs)

    def _parse_content(
        self,
        content: bytes,
        file_info: dict,
        reader: str,
        **kwargs,
    ) -> pd.DataFrame:
        """Parse downloaded bytes into a DataFrame."""
        buf = io.BytesIO(content)
        mime = file_info.get("MimeType", "")

        # Google Sheets are exported as CSV
        if mime == GOOGLE_SHEETS_MIME:
            return pd.read_csv(io.StringIO(content.decode("utf-8")), **kwargs)

        if reader == "csv":
            return pd.read_csv(buf, **kwargs)
        elif reader == "excel":
            return pd.read_excel(buf, **kwargs)
        elif reader == "parquet":
            return pd.read_parquet(buf, **kwargs)
        elif reader == "json":
            return pd.read_json(buf, **kwargs)
        else:
            return pd.read_csv(buf, **kwargs)


# ------------------------------------------------------------------
# OAuth flow helpers (for frontend-initiated auth)
# ------------------------------------------------------------------
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
DRIVE_SCOPES = "https://www.googleapis.com/auth/drive.readonly"


def build_oauth_url(client_id: str, redirect_uri: str, state: str = "") -> str:
    """Build the Google OAuth2 authorization URL for the frontend to redirect to."""
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": DRIVE_SCOPES,
        "access_type": "offline",
        "prompt": "consent",
    }
    if state:
        params["state"] = state

    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GOOGLE_AUTH_URL}?{query}"


def exchange_code_for_token(
    code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> dict[str, Any]:
    """Exchange an authorization code for access + refresh tokens."""
    resp = httpx.post(
        GOOGLE_TOKEN_URL,
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
    )
    resp.raise_for_status()
    return resp.json()


def refresh_access_token(
    refresh_token: str,
    client_id: str,
    client_secret: str,
) -> dict[str, Any]:
    """Refresh an expired access token."""
    resp = httpx.post(
        GOOGLE_TOKEN_URL,
        data={
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
        },
    )
    resp.raise_for_status()
    return resp.json()
