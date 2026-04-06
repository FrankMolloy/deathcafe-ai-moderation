from django.db import models


class Post(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("needs_review", "Needs Review"),
    ]

    title = models.CharField(max_length=255)
    body = models.TextField()
    image = models.ImageField(upload_to="posts/", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

from django.db import models


class Post(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("needs_review", "Needs Review"),
    ]

    title = models.CharField(max_length=255)
    body = models.TextField()
    image = models.ImageField(upload_to="posts/", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ModerationResult(models.Model):
    DECISION_CHOICES = [
        ("approve", "Approve"),
        ("reject", "Reject"),
        ("needs_review", "Needs Review"),
    ]

    FINAL_DECISION_CHOICES = [
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("needs_review", "Needs Review"),
    ]

    DECISION_SOURCE_CHOICES = [
        ("ai_auto", "AI Auto"),
        ("human_manual", "Human Manual"),
        ("human_override", "Human Override"),
    ]

    post = models.OneToOneField(
        Post,
        on_delete=models.CASCADE,
        related_name="moderation_result"
    )
    recommendation = models.CharField(max_length=20, choices=DECISION_CHOICES)
    confidence = models.FloatField()
    explanation = models.TextField()
    triggered_rules = models.JSONField(default=list)
    triggered_rule_descriptions = models.JSONField(default=list, blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    model_name = models.CharField(max_length=100, blank=True)

    final_decision = models.CharField(
        max_length=20,
        choices=FINAL_DECISION_CHOICES,
        null=True,
        blank=True
    )
    decision_source = models.CharField(
        max_length=20,
        choices=DECISION_SOURCE_CHOICES,
        default="human_manual"
    )
    moderator_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def ai_mapped_decision(self):
        mapping = {
            "approve": "approved",
            "reject": "rejected",
            "needs_review": "needs_review",
        }
        return mapping.get(self.recommendation)

    def ai_human_agree(self):
        if not self.final_decision:
            return None
        return self.ai_mapped_decision() == self.final_decision

    def __str__(self):
        return f"Moderation for {self.post.title}"