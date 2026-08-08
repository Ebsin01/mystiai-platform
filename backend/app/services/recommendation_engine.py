def generate_recommendations(question, cards):
    recommendations = []

    q = (question or "").lower()

    if "job" in q or "career" in q or "work" in q:
        recommendations.append(
            "Continue improving your technical and professional skills."
        )
        recommendations.append(
            "Apply consistently and prepare well for interviews."
        )

    elif "love" in q or "relationship" in q or "marriage" in q:
        recommendations.append(
            "Communicate honestly with the people close to you."
        )
        recommendations.append(
            "Practice patience and empathy in relationships."
        )

    elif "money" in q or "finance" in q or "business" in q:
        recommendations.append(
            "Plan your budget carefully."
        )
        recommendations.append(
            "Avoid unnecessary financial risks."
        )

    else:
        recommendations.append(
            "Trust your intuition while making important decisions."
        )
        recommendations.append(
            "Stay positive and embrace personal growth."
        )

    return recommendations