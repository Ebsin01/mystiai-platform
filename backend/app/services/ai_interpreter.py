def generate_three_card_interpretation(question, cards):
    """
    cards = [
        {
            "position": "Past",
            "card_name": "...",
            "orientation": "...",
            "meaning": "..."
        }
    ]
    """

    question_text = question.strip() if question else "your question"
    question_lower = question_text.lower()

    card_map = {card["position"].lower(): card for card in cards}
    past_card = card_map.get("past", cards[0]) if len(cards) > 0 else None
    present_card = card_map.get("present", cards[1] if len(cards) > 1 else cards[0]) if len(cards) > 0 else None
    future_card = card_map.get("future", cards[2] if len(cards) > 2 else cards[-1]) if len(cards) > 0 else None

    if "job" in question_lower or "career" in question_lower or "work" in question_lower:
        guidance_focus = "career-focused advice"
        guidance_theme = (
            "This spread points to a moment where your effort and confidence can shape a stronger professional path. "
            "Stay open to new opportunities, sharpen your skills, and trust that steady progress will create momentum."
        )
    elif "love" in question_lower or "relationship" in question_lower or "marriage" in question_lower:
        guidance_focus = "relationship-focused advice"
        guidance_theme = (
            "This spread suggests that your emotional life needs honesty, patience, and a willingness to communicate with care. "
            "Let trust grow through small acts of consistency and open-hearted listening."
        )
    elif (
        "money" in question_lower
        or "finance" in question_lower
        or "business" in question_lower
        or "invest" in question_lower
        or "savings" in question_lower
        or "budget" in question_lower
        or "wealth" in question_lower
        or "debt" in question_lower
        or "income" in question_lower
        or "spend" in question_lower
    ):
        guidance_focus = "financial advice"
        guidance_theme = (
            "This spread encourages practical choices and thoughtful planning. "
            "Protect your energy, review your priorities, and make decisions that support long-term stability rather than short-term excitement. "
            "This is a strong moment for careful financial advice and disciplined action."
        )
    else:
        guidance_focus = "guidance"
        guidance_theme = (
            "This spread invites you to move with patience and self-trust. "
            "Honor what you have learned, act with clarity in the present, and let your next steps unfold with calm confidence."
        )

    def card_summary(card):
        if not card:
            return "The card's message is still unfolding."
        return f"{card['card_name']} ({card['orientation']}) speaks of {card['meaning'].lower()}"

    interpretation = []
    interpretation.append(f"Question: {question_text}\n")
    interpretation.append(
        f"Your question about {question_text.lower()} is being answered through a spread that feels personal, layered, and encouraging. "
        f"The cards suggest that your path is not random; it is being shaped by lessons already lived, choices being made now, and possibilities still opening ahead."
    )

    if past_card:
        interpretation.append(
            f"Past: {card_summary(past_card)}. This reflects earlier experiences, patterns, or emotional lessons that have prepared you for where you are now."
        )
    if present_card:
        interpretation.append(
            f"Present: {card_summary(present_card)}. This shows the energy surrounding your current moment and the kind of mindset or action that matters most right now."
        )
    if future_card:
        interpretation.append(
            f"Future: {card_summary(future_card)}. This points toward what is likely to grow or become clearer if you stay grounded and continue moving forward."
        )

    interpretation.append(
        f"Overall Guidance: {guidance_theme} In this reading, {guidance_focus} is especially important, because the cards are reminding you that growth comes from aligning your choices with your values."
    )

    return "\n".join(interpretation)