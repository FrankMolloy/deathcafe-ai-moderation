from django.shortcuts import render, redirect
from .forms import PostSubmissionForm


def submit_post(request):
    if request.method == "POST":
        form = PostSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.status = "pending"
            post.save()
            return redirect("submit_post")
    else:
        form = PostSubmissionForm()

    return render(request, "moderation/submit_post.html", {"form": form})