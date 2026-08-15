import json
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel


logger = logging.getLogger(__name__)
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
_client: genai.Client | None = None
_client_api_key: str | None = None


class RcaNarrative(BaseModel):
    incident_summary: str
    impact: str
    probable_root_cause: str
    suggested_remediation: list[str]


def get_gemini_client(api_key: str) -> genai.Client:
    """Reuse one SDK client for the FastAPI process instead of closing it per request."""
    global _client, _client_api_key

    if _client is None or _client_api_key != api_key:
        _client = genai.Client(api_key=api_key)
        _client_api_key = api_key

    return _client


def generate_ai_rca(
    alert_text: str,
    extracted: dict[str, Any],
    matched_incidents: list[dict[str, Any]],
    matched_runbooks: list[dict[str, Any]],
    fallback: dict[str, Any],
) -> dict[str, Any]:
    """Use Gemini for narrative text while retaining deterministic evidence and confidence."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return fallback

    evidence = {
        "alert": alert_text,
        "extracted_fields": extracted,
        "matched_incidents": [item["incident"] for item in matched_incidents],
        "matched_runbooks": [item["runbook"] for item in matched_runbooks],
    }
    instructions = """You are an SRE incident RCA assistant. Create a concise, operator-friendly RCA using ONLY the supplied alert and retrieved evidence. Do not invent metrics, commands, incidents, runbooks, root causes, or remediation steps. If the evidence is insufficient, say that clearly. Write impact as a customer or service effect, not an environment name. Suggested remediation must be safe, human-reviewed actions, not automatically executed commands."""

    try:
        response = get_gemini_client(api_key).models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
            contents=json.dumps(evidence),
            config=types.GenerateContentConfig(
                system_instruction=instructions,
                response_mime_type="application/json",
                response_schema=RcaNarrative,
            ),
        )
        narrative = RcaNarrative.model_validate_json(response.text).model_dump()
        logger.info("Gemini RCA generated using model %s", os.getenv("GEMINI_MODEL", "gemini-3.5-flash"))
        return fallback | narrative
    except Exception:
        logger.exception("Gemini RCA generation failed; returning the rule-based fallback")
        return fallback
