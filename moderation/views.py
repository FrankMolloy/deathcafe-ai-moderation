from django.shortcuts import render, redirect

from .forms import PostSubmissionForm
from .models import ModerationResult
from .services.moderation_engine import moderate_text


def submit_post(request):
    if request.method == "POST":
        form = PostSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.status = "pending"
            post.save()

            result = moderate_text(post.title, post.body)

            ModerationResult.objects.create(
              post=post,
              recommendation=result["recommendation"],
              confidence=result["confidence"],
              explanation=result["explanation"],
              triggered_rules=result.get("triggered_rules", []),
              triggered_rule_descriptions=result.get("triggered_rule_descriptions", []),
              raw_response=result,
              model_name=result.get("model_name", ""),
            )

            if result["recommendation"] == "approve":
                post.status = "approved"
            elif result["recommendation"] == "reject":
                post.status = "rejected"
            else:
                post.status = "needs_review"

            post.save()

            return redirect("/admin/")

    else:
        form = PostSubmissionForm()

    return render(request, "moderation/submit_post.html", {"form": form})