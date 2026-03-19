import logging
import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from config import settings
from models import CallWebhookPayload
from gemini_service import analyze_call
from sheets_service import append_call_row

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Extra Transcriber is up ✓")
    yield
    log.info("Extra Transcriber shutting down")


app = FastAPI(
    title="Extra Call Transcriber",
    description="מתמלל שיחות מאקסטרה ושומר ב-Google Sheets",
    lifespan=lifespan,
)


# ── בריאות ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}


# ── Webhook ────────────────────────────────────────────────────────────────────

@app.post("/webhook/call")
async def call_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    מקבל אירוע שיחה מאקסטרה :
    םשוהוממ_Yגׂ_Yהנ_ה פ_U�u� יות ב.W_^_^[^��>_י]U�W^W^MX^[�v�)�ݽy��Vu�u�E��טוׅה^�y�לש_Yוy�u�