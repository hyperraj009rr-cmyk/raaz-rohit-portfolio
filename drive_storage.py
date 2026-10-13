import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload
import io

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

class DriveSetupError(RuntimeError):
    pass

class DriveStorage:
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
        self.refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN", "").strip()

    def is_connected(self):
        return bool(self.client_id and self.client_secret and self.refresh_token)

    def _flow(self, redirect_uri):
        if not self.client_id or not self.client_secret:
            raise DriveSetupError("First add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in Render Environment.")
        config = {"web": {"client_id": self.client_id, "client_secret": self.client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri]}}
        flow = Flow.from_client_config(config, scopes=SCOPES, redirect_uri=redirect_uri)
        return flow

    def authorization_url(self, redirect_uri):
        flow = self._flow(redirect_uri)
        url, _ = flow.authorization_url(access_type="offline", prompt="consent", include_granted_scopes="true")
        return url

    def exchange_code(self, callback_url, redirect_uri):
        flow = self._flow(redirect_uri)
        flow.fetch_token(authorization_response=callback_url)
        token = flow.credentials.refresh_token
        if not token:
            raise DriveSetupError("Google did not return a refresh token. Remove this app from Google Account access and connect again.")
        return token

    def _service(self):
        if not self.is_connected():
            raise DriveSetupError("Google Drive is not connected. Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET and GOOGLE_REFRESH_TOKEN.")
        creds = Credentials(None, refresh_token=self.refresh_token, token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id, client_secret=self.client_secret, scopes=SCOPES)
        return build("drive", "v3", credentials=creds, cache_discovery=False)

    def _find(self, name):
        service = self._service()
        escaped = name.replace("'", "\\'")
        result = service.files().list(q=f"name = '{escaped}' and trashed = false", pageSize=100,
            fields="files(id,name,mimeType)").execute()
        return next((f for f in result.get("files", []) if f["name"] == name), None)

    def upload_path(self, path, name, overwrite=True):
        service = self._service()
        existing = self._find(name) if overwrite else None
        media = MediaFileUpload(str(path), mimetype=None, resumable=False)
        if existing:
            return service.files().update(fileId=existing["id"], media_body=media, fields="id,name").execute()
        return service.files().create(body={"name": name}, media_body=media, fields="id,name").execute()

    def upload_bytes(self, content, name, mime_type="application/octet-stream", overwrite=True):
        service = self._service()
        existing = self._find(name) if overwrite else None
        media = MediaIoBaseUpload(io.BytesIO(content), mimetype=mime_type, resumable=False)
        if existing:
            return service.files().update(fileId=existing["id"], media_body=media, fields="id,name").execute()
        return service.files().create(body={"name": name}, media_body=media, fields="id,name").execute()

    def download_by_name(self, name):
        service = self._service()
        item = self._find(name)
        if not item:
            raise FileNotFoundError(name)
        request = service.files().get_media(fileId=item["id"])
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return buffer.getvalue(), item.get("mimeType")
