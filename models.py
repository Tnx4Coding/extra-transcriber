from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class PhoneNumber(BaseModel):
    friendly: Optional[str] = None   # 054-1234567
    e164: Optional[str] = None       # +9725412345677


class Numbers(BaseModel):
    own: Optional[PhoneNumber] = None
    caller: Optional[PhoneNumber] = None
    destination: Optional[PhoneNumber] = None


class TimeInfo(BaseModel):
    timezone: Optional[str] = None
    gmt_offset: Optional[str] = None
    start: Optional[str] = None      # "2026-03-19 14:32:00"
    end: Optional[str] = None


class Contact(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None


class Recording(BaseModel):
    url: Optional[str] = None


class CallWebhookPayload(BaseModel):
    id: str
    event: Optional[str] = None      # "call_ended"
    type: Optional[str] = None       # "incoming" / "outgoing"
    own_type: Optional[str] = None
    ivr_dialed: Optional[int] = None
    duration: Optional[int] = None   # שניות
    note: Optional[str] = None
    starred: Optional[bool] = None
    time: Optional[TimeInfo] = None
    numbers: Optional[Numbers] = None
    contact: Optional[Contact] = None
    recording: Optional[Recording] = None


class CallAnalysis(BaseModel):
    """תוצאת עיבוד Gemini"""
    transcript: str = Field(description="תמלול מלא של השיחה")
    summary: str = Field(description="סיכום קצר 2-3 משפטים")
    tags: list[str] = Field(default_factory=list, description="תגיות השיחה")
