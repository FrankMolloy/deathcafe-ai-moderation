class ThresholdPolicy:
    VERSION = "v1"

    APPROVE_THRESHOLD = 0.97
    REJECT_THRESHOLD = 0.995

    def decide(self, recommendation: str, confidence: float, triggered_rules: list) -> dict:
        reject_rules = [rule for rule in triggered_rules if isinstance(rule, str) and rule.startswith("R")]

        if recommendation == "approve" and confidence >= self.APPROVE_THRESHOLD:
            return {
                "auto_action_taken": "auto_approved",
                "auto_action_reason": "High confidence approve.",
                "final_decision": "approved",
            }

        if recommendation == "reject" and confidence >= self.REJECT_THRESHOLD and reject_rules:
            return {
                "auto_action_taken": "auto_rejected",
                "auto_action_reason": "High confidence reject with reject rule triggered.",
                "final_decision": "rejected",
            }

        return {
            "auto_action_taken": "queued_for_review",
            "auto_action_reason": "Below threshold or needs human review.",
            "final_decision": "needs_review",
        }