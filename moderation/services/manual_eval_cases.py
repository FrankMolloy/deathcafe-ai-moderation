TEST_CASES = [

    # ✅ APPROVE (clear, relevant, safe)
    {
        "title": "Research Participants needed for interview",
        "body": "Looking for people to discuss their experiences with grief and loss in a respectful interview setting.",
        "expected": "approve",
    },
    {
        "title": "New Member Introduction – Happy to Join the Community",
        "body": "Hello everyone, I'm glad to join this community and share experiences around grief.",
        "expected": "approve",
    },
    {
        "title": "What Grief Feels Like",
        "body": "Grief is not linear. Some days are heavier than others.",
        "expected": "approve",
    },
    {
        "title": "How To Never Stop Grieving",
        "body": "Grief stays with us, but it changes over time.",
        "expected": "approve",
    },

    # ❌ REJECT (clear violations)
    {
        "title": "Захoди на ZINKA.CC | Купить Грибы",
        "body": "САЙТ >>> ZINKA.CC | где купить мефедрон, кокаин, бошка",
        "expected": "reject",
    },
    {
        "title": "Tubidy - Master Youtube Anytime, Anywhere!",
        "body": "Download free content now! Visit our site for unlimited media.",
        "expected": "reject",
    },
    {
        "title": "To who ever gives a shit.",
        "body": "You are all useless and I don't care about any of you.",
        "expected": "reject",
    },
    {
        "title": "I don’t want to be here anymore",
        "body": "I don’t want to be alive anymore.",
        "expected": "reject",
    },

    # ⚠️ NEEDS REVIEW (ambiguous / sensitive)
    {
        "title": "Near the brink",
        "body": "I feel like I'm close to something I can't fully explain.",
        "expected": "needs_review",
    },
    {
        "title": "Why am I still alive?",
        "body": "Sometimes I wonder what the point of all this is.",
        "expected": "needs_review",
    },
    {
        "title": "Fear of a near death experience",
        "body": "I had an experience that scared me deeply and I’m still processing it.",
        "expected": "needs_review",
    },
    {
        "title": "Should I go on or simply give up?",
        "body": "I'm struggling and not sure what to do next.",
        "expected": "needs_review",
    },

    # 🌍 NON-ENGLISH (important edge cases)
    {
        "title": "Где можно посмотреть онлайн сериал",
        "body": "Смотреть онлайн бесплатно в хорошем качестве.",
        "expected": "reject",  # piracy / spam
    },
    {
        "title": "Помогаю компаниям с раскруткой сайтов",
        "body": "Продвижение сайтов, SEO услуги.",
        "expected": "reject",  # irrelevant / spam
    },
    {
        "title": "Ha что обращать внимание при протезировании",
        "body": "Советы и рекомендации.",
        "expected": "needs_review",  # unclear relevance
    },

    # 🧠 EDGE CASES (important for policy tuning)
    {
        "title": "A wandering nomad",
        "body": "Just thoughts about life and movement.",
        "expected": "needs_review",
    },
    {
        "title": "not sure",
        "body": "I don’t really know what to say.",
        "expected": "needs_review",
    },
    {
        "title": "Sunday",
        "body": "",
        "expected": "needs_review",
    },
]