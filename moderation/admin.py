from collections import Counter

from django.contrib import admin, messages
from django.db.models import Count

from .models import Post, ModerationResult


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "body")


@admin.register(ModerationResult)
class ModerationResultAdmin(admin.ModelAdmin):
    list_display = (
        "post",
        "recommendation",
        "confidence",
        "final_decision",
        "decision_source",
        "agreement_status",
        "model_name",
        "created_at",
    )
    list_filter = (
        "recommendation",
        "final_decision",
        "decision_source",
        "created_at",
    )
    search_fields = ("post__title", "post__body", "explanation", "moderator_notes")
    readonly_fields = (
        "post",
        "recommendation",
        "confidence",
        "explanation",
        "triggered_rules",
        "triggered_rule_descriptions",
        "raw_response",
        "model_name",
        "created_at",
        "agreement_status",
    )
    fields = (
        "post",
        "recommendation",
        "confidence",
        "explanation",
        "triggered_rules",
        "triggered_rule_descriptions",
        "raw_response",
        "model_name",
        "final_decision",
        "decision_source",
        "moderator_notes",
        "reviewed_at",
        "agreement_status",
        "created_at",
    )
    actions = ["mark_as_approved", "mark_as_rejected", "mark_as_needs_review"]

    def agreement_status(self, obj):
        agreed = obj.ai_human_agree()
        if agreed is None:
            return "Not reviewed"
        return "Agree" if agreed else "Override"

    agreement_status.short_description = "AI vs Human"

    @admin.action(description="Set final decision to Approved")
    def mark_as_approved(self, request, queryset):
        updated = 0
        for obj in queryset:
            obj.final_decision = "approved"
            obj.decision_source = (
                "human_manual"
                if obj.ai_mapped_decision() == "approved"
                else "human_override"
            )
            from django.utils import timezone
            obj.reviewed_at = timezone.now()
            obj.save()

            obj.post.status = "approved"
            obj.post.save()
            updated += 1

        self.message_user(request, f"{updated} result(s) marked as approved.", messages.SUCCESS)

    @admin.action(description="Set final decision to Rejected")
    def mark_as_rejected(self, request, queryset):
        updated = 0
        for obj in queryset:
            obj.final_decision = "rejected"
            obj.decision_source = (
                "human_manual"
                if obj.ai_mapped_decision() == "rejected"
                else "human_override"
            )
            from django.utils import timezone
            obj.reviewed_at = timezone.now()
            obj.save()

            obj.post.status = "rejected"
            obj.post.save()
            updated += 1

        self.message_user(request, f"{updated} result(s) marked as rejected.", messages.SUCCESS)

    @admin.action(description="Set final decision to Needs Review")
    def mark_as_needs_review(self, request, queryset):
        updated = 0
        for obj in queryset:
            obj.final_decision = "needs_review"
            obj.decision_source = (
                "human_manual"
                if obj.ai_mapped_decision() == "needs_review"
                else "human_override"
            )
            from django.utils import timezone
            obj.reviewed_at = timezone.now()
            obj.save()

            obj.post.status = "needs_review"
            obj.post.save()
            updated += 1

        self.message_user(request, f"{updated} result(s) marked as needs review.", messages.SUCCESS)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        queryset = ModerationResult.objects.all()

        total_results = queryset.count()
        ai_approve = queryset.filter(recommendation="approve").count()
        ai_reject = queryset.filter(recommendation="reject").count()
        ai_review = queryset.filter(recommendation="needs_review").count()

        final_approved = queryset.filter(final_decision="approved").count()
        final_rejected = queryset.filter(final_decision="rejected").count()
        final_review = queryset.filter(final_decision="needs_review").count()

        overrides = 0
        agreements = 0
        reviewed = 0

        rule_counter = Counter()

        for obj in queryset:
            if obj.final_decision:
                reviewed += 1
                if obj.ai_human_agree():
                    agreements += 1
                else:
                    overrides += 1

            for rule in obj.triggered_rule_descriptions:
                rule_counter[rule] += 1

        top_rules = rule_counter.most_common(5)

        extra_context["dashboard_stats"] = {
            "total_results": total_results,
            "ai_approve": ai_approve,
            "ai_reject": ai_reject,
            "ai_review": ai_review,
            "final_approved": final_approved,
            "final_rejected": final_rejected,
            "final_review": final_review,
            "reviewed": reviewed,
            "agreements": agreements,
            "overrides": overrides,
            "top_rules": top_rules,
        }

        return super().changelist_view(request, extra_context=extra_context)