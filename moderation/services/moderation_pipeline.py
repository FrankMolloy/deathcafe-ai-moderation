from moderation.models import ModerationResult
from .moderation_engine import moderate_text
from .thresholds import ThresholdPolicy


def run_moderation_pipeline(post, apply_auto_actions=False):
    ai_result = moderate_text(post.title, post.body)
    threshold_policy = ThresholdPolicy()

    threshold_result = threshold_policy.decide(
        recommendation=ai_result["recommendation"],
        confidence=ai_result["confidence"],
        triggered_rules=ai_result["triggered_rules"],
    )

    moderation_result, _ = ModerationResult.objects.update_or_create(
        post=post,
        defaults={
            "recommendation": ai_result["recommendation"],
            "confidence": ai_result["confidence"],
            "explanation": ai_result["explanation"],
            "triggered_rules": ai_result["triggered_rules"],
            "triggered_rule_descriptions": ai_result["triggered_rule_descriptions"],
            "raw_response": ai_result["raw_response"],
            "model_name": ai_result["model_name"],
            "prompt_version": ai_result.get("prompt_version", ""),
            "threshold_version": threshold_policy.VERSION,
            "auto_action_taken": threshold_result["auto_action_taken"],
            "auto_action_reason": threshold_result["auto_action_reason"],
            "processing_status": ai_result.get("processing_status", "success"),
            "error_message": ai_result.get("error_message", ""),
        },
    )

    if apply_auto_actions:
        post.status = threshold_result["final_decision"]
        moderation_result.final_decision = threshold_result["final_decision"]
        moderation_result.decision_source = "ai_auto"
        post.save(update_fields=["status"])
        moderation_result.save(update_fields=["final_decision", "decision_source"])

    return moderation_result