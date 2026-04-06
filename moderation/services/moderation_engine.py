import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from .prompts import (
    MODERATION_POLICY,
    OUTPUT_FORMAT_INSTRUCTIONS,
    RULE_DESCRIPTIONS,
    PROMPT_VERSION,
)

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ALLOWED_RECOMMENDATIONS = {"approve", "reject", "needs_review"}


def _safe_fallback(reason: str = "The model output was invalid and requires human review.") -> dict:
    return {
        "recommendation": "needs_review",
        "confidence": 0.0,
        "triggered_rules": ["invalid_model_output"],
        "explanation": reason,
        "triggered_rule_descriptions": [
            RULE_DESCRIPTIONS.get("invalid_model_output", "Invalid model output")
        ],
        "raw_response": {},
        "model_name": "",
        "prompt_version": PROMPT_VERSION,
        "processing_status": "failed",
        "error_message": reason,
    }


def _validate_moderation_response(data: dict) -> dict:
    if not isinstance(data, dict):
        return _safe_fallback("Model output was not a valid JSON object.")

    recommendation = data.get("recommendation")
    confidence = data.get("confidence")
    triggered_rules = data.get("triggered_rules")
    explanation = data.get("explanation")

    if recommendation not in ALLOWED_RECOMMENDATIONS:
        return _safe_fallback("Model returned an invalid recommendation value.")

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        return _safe_fallback("Model returned an invalid confidence value.")

    if confidence < 0.0 or confidence > 1.0:
        return _safe_fallback("Model returned confidence outside the allowed range.")

    if not isinstance(triggered_rules, list):
        return _safe_fallback("Model returned triggered_rules in an invalid format.")

    cleaned_rules = []
    for rule in triggered_rules:
        if isinstance(rule, str):
            cleaned_rules.append(rule.strip())

    if not isinstance(explanation, str):
        return _safe_fallback("Model returned explanation in an invalid format.")

    explanation = explanation.strip()
    if not explanation:
        explanation = "No explanation was provided by the model."

    validated = {
        "recommendation": recommendation,
        "confidence": confidence,
        "triggered_rules": cleaned_rules,
        "explanation": explanation,
        "triggered_rule_descriptions": [
            RULE_DESCRIPTIONS.get(rule_id, f"Unknown rule: {rule_id}")
            for rule_id in cleaned_rules
        ],
        "raw_response": {},
        "model_name": "",
        "prompt_version": PROMPT_VERSION,
        "processing_status": "success",
        "error_message": "",
    }

    return validated


def moderate_text(title: str, body: str) -> dict:
    user_prompt = f"""
Review this blog submission according to the moderation policy.

Title:
{title}

Body:
{body}

{OUTPUT_FORMAT_INSTRUCTIONS}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-5.4-nano",
            messages=[
                {"role": "system", "content": MODERATION_POLICY},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
        )

        content = response.choices[0].message.content

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            result = _safe_fallback("The model did not return valid JSON.")
            result["raw_response"] = {"content": content}
            result["model_name"] = getattr(response, "model", "")
            return result

        validated = _validate_moderation_response(parsed)
        validated["raw_response"] = {"content": content}
        validated["model_name"] = getattr(response, "model", "")
        return validated

    except Exception as exc:
        result = _safe_fallback(f"Moderation request failed: {str(exc)}")
        result["error_message"] = str(exc)
        return result