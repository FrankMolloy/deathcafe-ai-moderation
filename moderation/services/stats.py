from collections import Counter

from django.db.models import Avg

from moderation.models import ModerationResult, Post


def get_moderation_stats():
    total_posts = Post.objects.count()
    total_results = ModerationResult.objects.count()

    approved_count = ModerationResult.objects.filter(recommendation="approve").count()
    rejected_count = ModerationResult.objects.filter(recommendation="reject").count()
    needs_review_count = ModerationResult.objects.filter(recommendation="needs_review").count()

    avg_confidence = ModerationResult.objects.aggregate(avg=Avg("confidence"))["avg"] or 0.0

    reviewed_results = ModerationResult.objects.exclude(final_decision__isnull=True)
    reviewed_count = reviewed_results.count()

    agreement_count = 0
    disagreement_count = 0

    for result in reviewed_results:
        agree = result.ai_human_agree()
        if agree is True:
            agreement_count += 1
        elif agree is False:
            disagreement_count += 1

    agreement_rate = 0.0
    if reviewed_count > 0:
        agreement_rate = (agreement_count / reviewed_count) * 100

    rule_counter = Counter()
    for result in ModerationResult.objects.all():
        for rule in result.triggered_rules:
            rule_counter[rule] += 1

    top_rules = rule_counter.most_common(10)

    latest_results = ModerationResult.objects.select_related("post").order_by("-created_at")[:10]

    return {
        "total_posts": total_posts,
        "total_results": total_results,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        "needs_review_count": needs_review_count,
        "avg_confidence": round(avg_confidence, 2),
        "reviewed_count": reviewed_count,
        "agreement_count": agreement_count,
        "disagreement_count": disagreement_count,
        "agreement_rate": round(agreement_rate, 1),
        "top_rules": top_rules,
        "latest_results": latest_results,
    }