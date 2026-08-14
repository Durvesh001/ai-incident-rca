import json
import logging
import os
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

RCA_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "incident_summary": {"type": "string"},
        "impact": {"type": "string"},
        "evidence": {"type": "array", "items": {"type": "string"}},
        "probable_root_cause": {"type": "string"},
        "suggested_remediation": {"type": "array", "items": {"type": "string"}},
        "confidence_score": {"type": "integer", "minimum": 0, "maximum": 95},
    },
    "required": [
        "incident_summary",
        "impact",
        "evidence",
        "probable_root_cause",
        "suggested_remediation",
        "confidence_score",
    ],
}


def generate_ai_rca(
    alert_text: str,
    extracted: dict[str, Any],
    matched_incidents: list[dict[str, Any]],
    matched_runbooks: list[dict[str, Any]],
    fallback: dict[str, Any],
) -> dict[str, Any]:
    """Generate an RCA with local Ollama from application-selected evidence."""

    evidence = {
        "alert": alert_text,
        "extracted_fields": extracted,
        "matched_incidents": [item["incident"] for item in matched_incidents],
        "matched_runbooks": [item["runbook"] for item in matched_runbooks],
    }
    instructions = """You are an SRE incident RCA assistant. Create a concise RCA using ONLY the supplied alert and retrieved evidence. Do not invent metrics, commands, incidents, runbooks, root causes, or remediation steps. If the evidence is insufficient, say that clearly and use a low confidence score. Evidence entries must name the supporting incident or runbook ID when one exists. Suggested remediation must be safe, human-reviewed actions, not automatically executed commands."""

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    payload = {
        "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
        "messages": [
            {"role": "system", "content": instructions},
            {"role": "user", "content": json.dumps(evidence)},
        ],
        "format": RCA_SCHEMA,
        "options": {"temperature": 0.2},
        "stream": False,
    }

    try:
        request = Request(
            f"{base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=60) as response:
            response_body = json.loads(response.read().decode("utf-8"))
        return json.loads(response_body["message"]["content"])
    except (KeyError, OSError, URLError, ValueError, json.JSONDecodeError):
        logger.exception("Local Ollama RCA generation failed; returning the rule-based fallback")
        return fallback
