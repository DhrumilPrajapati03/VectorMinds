"""ElevenLabs TTS helper (TKT-028). Uses httpx — no ElevenLabs SDK."""

from __future__ import annotations

import logging

import httpx
from fastapi import HTTPException

from config import settings

logger = logging.getLogger(__name__)

ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
ELEVENLABS_MODEL = "eleven_multilingual_v2"
TTS_TIMEOUT_SECONDS = 60.0


async def synthesize_speech(text: str) -> bytes:
    """Convert text to MPEG audio via ElevenLabs.

    Raises:
        HTTPException: 503 if API key missing; 502 on upstream failure.
    """
    api_key = (settings.elevenlabs_api_key or "").strip()
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "Text-to-speech is unavailable: ELEVENLABS_API_KEY is not configured. "
                "Set it in lexo/backend/.env to enable POST /api/voice/speak."
            ),
        )

    voice_id = (settings.elevenlabs_voice_id or "").strip() or "21m00Tcm4TlvDq8ikWAM"
    url = ELEVENLABS_TTS_URL.format(voice_id=voice_id)
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": ELEVENLABS_MODEL,
    }

    try:
        async with httpx.AsyncClient(timeout=TTS_TIMEOUT_SECONDS) as client:
            response = await client.post(url, headers=headers, json=payload)
    except httpx.TimeoutException:
        logger.exception("elevenlabs_tts_timeout")
        raise HTTPException(
            status_code=502,
            detail="Text-to-speech timed out. Please try again.",
        ) from None
    except httpx.HTTPError:
        logger.exception("elevenlabs_tts_http_error")
        raise HTTPException(
            status_code=502,
            detail="Text-to-speech request failed. Please try again.",
        ) from None

    if response.status_code == 401 or response.status_code == 403:
        logger.info("elevenlabs_tts_auth_failed status=%s", response.status_code)
        raise HTTPException(
            status_code=503,
            detail="Text-to-speech is unavailable: invalid ELEVENLABS_API_KEY.",
        )
    if response.status_code >= 400:
        logger.info(
            "elevenlabs_tts_upstream_error status=%s",
            response.status_code,
        )
        raise HTTPException(
            status_code=502,
            detail="Text-to-speech provider returned an error. Please try again.",
        )

    audio = response.content
    if not audio:
        raise HTTPException(
            status_code=502,
            detail="Text-to-speech returned empty audio.",
        )
    logger.info("elevenlabs_tts_ok bytes=%s", len(audio))
    return audio
