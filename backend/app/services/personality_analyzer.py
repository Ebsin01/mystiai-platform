def analyze_personality(cards):
    strengths = []
    challenges = []

    for card in cards:
        name = card["card_name"]
        orientation = card["orientation"]

        if orientation == "Upright":
            strengths.append(
                f"{name} indicates confidence and positive growth."
            )
        else:
            challenges.append(
                f"{name} suggests an area for improvement."
            )

    advice = (
        "Focus on your strengths while working patiently on your challenges."
    )

    return {
        "strengths": strengths,
        "challenges": challenges,
        "advice": advice
    }