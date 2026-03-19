"""
Google Sheets service — OAuth2 version
───────────────────────────────────────
משתמש ב-refresh token במקום Service Account JSON.
"""
from __future__ import annotations

import logging
from datetime import datetime

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import settings
from models import CallAnalysis, CallWebhookPayload

log = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

HEADERS = [
    "call_id","תאריך","שעת_התחלה","שעת_סיום","משך_שניות",
    "כיוון","מספר_מתקשר","מספר_עצמי","מספר_יעד","שם_איש_קשר",
    "סיכום","תגיות","תמלול_מל׀",
]


def _get_credentials() -> Credentials:
    creds = Credentials(
        token=None,
        refresh_token=settings.GOOGLE_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def _get_service():
    return build("sheets", "v4", credentials=_get_credentials(), cache_discovery=False)


async def ensure_header_row() -> None:
    svc = _get_service()
    try:
        result = (svc.spreadsheets().values()
                  .get(spreadsheetId=settings.SPREADSHEET_ID, range="A1:A1")
                  .execute())
        if result.get("values"):
            return
    except HttpError:
        pass
    svc.spreadsheets().values().update(
        spreadsheetId=settings.SPREADSHEET_ID, range="A1",
        valueInputOption="RAW", body={"values": [HEADERS]},
    ).execute()
    log.info("Header row created in Sheets")


async def append_call_row(payload: CallWebhookPayload, analysis: CallAnalysis) -> None:
    row = _build_row(payload, analysis)
    _get_service().spreadsheets().values().append(
        spreadsheetId=settings.SPREADSHEET_ID, range="A1",
        valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()


def _build_row(payload: CallWebhookPayload, analysis: CallAnalysis) -> list:
    t = payload.time or {}
    date_str, start_str, end_str = _format_times(t)
    caller  = (payload.numbers.caller.friendly      if payload.numbers and payload.numbers.caller      else "") or ""
    own     = (payload.numbers.own.friendly          if payload.numbers and payload.numbers.own          else "") or ""
    dest    = (payload.numbers.destination.friendly  if payload.numbers and payload.numbers.destination  else "") or ""
    contact = (payload.contact.name                  if payload.contact else "") or ""
    return [payload.id, date_str, start_str, end_str, payload.duration or 0,
            payload.type or "", caller, own, dest, contact,
            analysis.summary, ", ".join(analysis.tags), analysis.transcript]


def _format_times(time_info) -> tuple[str, str, str]:
    start_raw = getattr(time_info, "start", None) or ""
    end_raw   = getattr(time_info, "end",   None) or ""
    fmt = "%Y-%m-%d %H:%M:%S"
    try:
        dt = datetime.strptime(start_raw, fmt)
        return dt.strftime("%d/%m/%Y"), dt.strftime("%H:%M"), ""
    except (ValueError, TypeError):
        pass
    try:
        return start_raw[:10], start_raw[11:16], end_raw[11:16]
    except Exception:
        return "", "", ""