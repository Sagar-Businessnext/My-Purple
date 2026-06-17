"""Google (Gmail + Calendar) integration — Purple's reach into your real inbox/schedule.

This is the one part of Purple that isn't local: it calls Google's APIs over OAuth. The
token is stored locally (google_token.json). Authorize once with:

    python -m purple.integrations.google_auth

The google client is synchronous; tools call these methods via asyncio.to_thread.
"""

from __future__ import annotations

import base64
from datetime import UTC
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

from purple.config import ROOT, settings
from purple.utils.logging import get_logger

log = get_logger("google")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
]


def _path(p: str) -> Path:
    path = Path(p)
    return path if path.is_absolute() else ROOT / path


class GoogleClient:
    def __init__(self) -> None:
        self._creds: Any | None = None
        self._gmail: Any | None = None
        self._cal: Any | None = None

    def _load_creds(self) -> Any:
        if self._creds is not None:
            return self._creds
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        token = _path(settings.google_token_path)
        if not token.exists():
            raise RuntimeError(
                "Google not authorized yet — run `python -m purple.integrations.google_auth` "
                f"(expected token at {token})."
            )
        creds = Credentials.from_authorized_user_file(str(token), SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token.write_text(creds.to_json())
        self._creds = creds
        return creds

    def _gmail_service(self) -> Any:
        if self._gmail is None:
            from googleapiclient.discovery import build

            self._gmail = build("gmail", "v1", credentials=self._load_creds())
        return self._gmail

    def _cal_service(self) -> Any:
        if self._cal is None:
            from googleapiclient.discovery import build

            self._cal = build("calendar", "v3", credentials=self._load_creds())
        return self._cal

    # --- Gmail ---
    def _summarise(self, svc: Any, msg_id: str) -> dict[str, str]:
        msg = (
            svc.users()
            .messages()
            .get(
                userId="me",
                id=msg_id,
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            )
            .execute()
        )
        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        return {
            "id": msg_id,
            "from": headers.get("From", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "snippet": msg.get("snippet", ""),
        }

    def list_emails(self, max_results: int = 10) -> list[dict[str, str]]:
        svc = self._gmail_service()
        res = (
            svc.users()
            .messages()
            .list(userId="me", maxResults=max_results, labelIds=["INBOX"])
            .execute()
        )
        return [self._summarise(svc, m["id"]) for m in res.get("messages", [])]

    def search_emails(self, query: str, max_results: int = 10) -> list[dict[str, str]]:
        svc = self._gmail_service()
        res = svc.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        return [self._summarise(svc, m["id"]) for m in res.get("messages", [])]

    def read_email(self, msg_id: str) -> dict[str, str]:
        svc = self._gmail_service()
        msg = svc.users().messages().get(userId="me", id=msg_id, format="full").execute()
        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        body = self._extract_body(msg["payload"])
        return {
            "from": headers.get("From", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "body": body[:8000],
        }

    @staticmethod
    def _extract_body(payload: dict) -> str:
        if payload.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode(errors="replace")
        for part in payload.get("parts", []):
            if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                return base64.urlsafe_b64decode(part["body"]["data"]).decode(errors="replace")
        return ""

    def _raw(self, to: str, subject: str, body: str) -> dict[str, str]:
        mime = MIMEText(body)
        mime["to"] = to
        mime["subject"] = subject
        return {"raw": base64.urlsafe_b64encode(mime.as_bytes()).decode()}

    def create_draft(self, to: str, subject: str, body: str) -> str:
        svc = self._gmail_service()
        draft = (
            svc.users()
            .drafts()
            .create(userId="me", body={"message": self._raw(to, subject, body)})
            .execute()
        )
        return draft["id"]

    def send_email(self, to: str, subject: str, body: str) -> str:
        svc = self._gmail_service()
        sent = svc.users().messages().send(userId="me", body=self._raw(to, subject, body)).execute()
        return sent["id"]

    # --- Calendar ---
    def list_events(self, max_results: int = 10) -> list[dict[str, str]]:
        from datetime import datetime

        svc = self._cal_service()
        now = datetime.now(UTC).isoformat()
        res = (
            svc.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        out = []
        for e in res.get("items", []):
            start = e.get("start", {})
            out.append(
                {
                    "id": e.get("id", ""),
                    "summary": e.get("summary", "(no title)"),
                    "start": start.get("dateTime", start.get("date", "")),
                }
            )
        return out

    def create_event(self, summary: str, start_iso: str, end_iso: str) -> str:
        svc = self._cal_service()
        event = (
            svc.events()
            .insert(
                calendarId="primary",
                body={
                    "summary": summary,
                    "start": {"dateTime": start_iso},
                    "end": {"dateTime": end_iso},
                },
            )
            .execute()
        )
        return event.get("htmlLink", event.get("id", ""))


# Process-wide Google client.
google = GoogleClient()
