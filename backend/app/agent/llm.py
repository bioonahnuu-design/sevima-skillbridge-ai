import json
import logging
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

from app.agent.prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger("skillbridge.agent.llm")

def _load_env_fallback():
    backend_dir = Path(__file__).resolve().parent.parent.parent
    possible_env_paths = [
        backend_dir / ".env",
        backend_dir.parent / ".env",
        Path.cwd() / ".env",
    ]
    for p in possible_env_paths:
        if p.is_file():
            try:
                from dotenv import load_dotenv

                load_dotenv(p)
                return
            except ImportError:
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        for line in f:
                            stripped = line.strip()
                            if stripped and not stripped.startswith("#") and "=" in stripped:
                                k, v = stripped.split("=", 1)
                                k = k.strip()
                                v = v.strip().strip("'\"")
                                if k and k not in os.environ:
                                    os.environ[k] = v
                    return
                except Exception:
                    pass


_load_env_fallback()


def get_gemini_api_key() -> Optional[str]:
    """
    Safely retrieves the Gemini API key from the environment.
    Never exposes or logs the key value.
    """
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    return key if key and key != "your_api_key_here" else None


def get_gemini_model() -> str:
    """
    Retrieves the configured Gemini model name.
    Defaults to 'gemini-1.5-flash'.
    """
    return os.environ.get("GEMINI_MODEL", "gemini-1.5-flash").strip()


def parse_and_validate_ai_response(raw_text: str) -> Optional[Dict[str, Any]]:
    """
    Safely parses and validates the JSON output from Gemini.
    Removes any surrounding markdown code fences.
    """
    if not raw_text or not raw_text.strip():
        return None

    cleaned = raw_text.strip()
    # Strip markdown code blocks if present
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if code_block_match:
        cleaned = code_block_match.group(1).strip()

    try:
        data = json.loads(cleaned)
    except Exception as e:
        logger.warning("Failed to parse JSON response from Gemini: %s", str(e))
        return None

    if not isinstance(data, dict):
        return None

    # Required fields verification
    required_fields = [
        "summary",
        "why_this_match",
        "focus_areas",
        "recommended_strategy",
        "encouragement",
    ]
    for f in required_fields:
        if f not in data:
            logger.warning("Missing required field '%s' in AI personalization response", f)
            return None

    # Ensure focus_areas is a list of strings
    if not isinstance(data["focus_areas"], list):
        data["focus_areas"] = [str(data["focus_areas"])]
    else:
        data["focus_areas"] = [str(item) for item in data["focus_areas"] if item]

    return {
        "summary": str(data["summary"]),
        "why_this_match": str(data["why_this_match"]),
        "focus_areas": data["focus_areas"],
        "recommended_strategy": str(data["recommended_strategy"]),
        "encouragement": str(data["encouragement"]),
    }


def call_gemini_api(
    user_prompt: str,
    api_key: str,
    model: str,
    timeout_seconds: float = 10.0,
) -> Optional[str]:
    """
    Executes a direct HTTPS POST request to Google Gemini API.
    Does not log or expose the API key in error messages.
    """
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    payload = {
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}],
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_prompt}],
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json",
        },
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=req_data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            body = resp.read().decode("utf-8")
            res_json = json.loads(body)

            candidates = res_json.get("candidates", [])
            if not candidates:
                logger.warning("Gemini returned empty candidates list.")
                return None

            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                logger.warning("Gemini candidate has no parts.")
                return None

            return parts[0].get("text", "")
    except urllib.error.HTTPError as e:
        logger.warning("Gemini API HTTP Error %d: %s", e.code, e.reason)
        return None
    except urllib.error.URLError as e:
        logger.warning("Gemini API Network/URL Error: %s", str(e.reason))
        return None
    except Exception as e:
        logger.warning("Gemini API request failed: %s", str(e))
        return None


def generate_personalization(
    grounded_context: Dict[str, Any],
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Generates personalized guidance using Google Gemini based strictly
    on pre-evaluated deterministic context.

    Gracefully returns None if API key is not configured, or if any network/parsing
    error occurs, ensuring the core application never crashes.
    """
    effective_key = api_key or get_gemini_api_key()
    if not effective_key:
        logger.info("Gemini API key is not configured; skipping AI personalization.")
        return None

    effective_model = model or get_gemini_model()
    prompt = build_user_prompt(grounded_context)

    raw_response = call_gemini_api(
        user_prompt=prompt,
        api_key=effective_key,
        model=effective_model,
    )

    if not raw_response:
        return None

    return parse_and_validate_ai_response(raw_response)
