import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from .prompts import MODERATION_POLICY, OUTPUT_FORMAT_INSTRUCTIONS, RULE_DESCRIPTIONS

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def moderate_text(title: str, body: str) -> dict:
    user_prompt = f"""
Review this blog submission according to the moderation policy.

Title:
{title}

Body:
{body}

{OUTPUT_FORMAT_INSTRUCTIONS}
"""

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
        parsed = {
            "recommendation": "needs_review",
            "confidence": 0.0,
            "triggered_rules": ["invalid_model_output"],
            "explanation": "The model did not return valid JSON.",
        }

    parsed["triggered_rule_descriptions"] = [
        RULE_DESCRIPTIONS.get(rule_id, f"Unknown rule: {rule_id}")
        for rule_id in parsed.get("triggered_rules", [])
    ]

    parsed["raw_response"] = {"content": content}
    parsed["model_name"] = response.model
    return parsed