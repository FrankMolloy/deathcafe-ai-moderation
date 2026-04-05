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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Moderation for {self.post.title}"