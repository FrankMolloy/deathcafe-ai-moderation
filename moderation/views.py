from django.shortcuts import render, redirect

from .forms import PostSubmissionForm
from .models import ModerationResult
from .services.moderation_engine import moderate_text
from .services.stats import get_moderation_stats


def submit_post(request):
    if request.method == "POST":
        form = PostSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.status = "pending"
            post.save()

            result = moderate_text(post.title, post.body)

            if result["recommendation"] == "approve":
                post.status = "approved"
                final_decision = "approved"
            elif result["recommendation"] == "reject":
                post.status = "rejected"
                final_decision = "rejected"
            else:
                post.status = "needs_review"
                final_decision = "needs_review"

            post.save()

            ModerationResult.objects.create(
                post=post,
                recommendation=result["recommendation"],
                confidence=result["confidence"],
                explanation=result["explanation"],
                triggered_rules=result.get("triggered_rules", []),
                triggered_rule_descriptions=result.get("triggered_rule_descriptions", []),
                raw_response=result,
                model_name=result.get("model_name", ""),
                final_decision=final_decision,
                decision_source="ai_auto",
            )

            return redirect("/admin/")
    else:
        form = PostSubmissionForm()

    return render(request, "moderation/submit_post.html", {"form": form})


def moderation_stats_view(request):
    stats = get_moderation_stats()
    return render(request, "moderation/stats.html", {"stats": stats})