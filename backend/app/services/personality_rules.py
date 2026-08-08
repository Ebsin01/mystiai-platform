from app.model.palm_analysis import PalmAnalysis


def calculate_scores(analysis: PalmAnalysis):

    scores = {
        "optimism": 60,
        "leadership": 60,
        "confidence": 60,
        "creativity": 60,
        "communication": 60,
        "decision_making": 60,
        "emotional_intelligence": 60,
        "stress_management": 60,
        "adaptability": 60,
        "risk_taking": 60,
        "emotional_balance": 60,
    }

    strengths = []
    weaknesses = []

    shape = (analysis.palm_shape or "").lower()
    heart = (analysis.heart_line or "").lower()
    head = (analysis.head_line or "").lower()
    life = (analysis.life_line or "").lower()

    # ---------------- Fire ----------------

    if "fire" in shape:

        scores["leadership"] += 18
        scores["confidence"] += 15
        scores["risk_taking"] += 12
        scores["optimism"] += 8

        strengths.extend([
            "Natural Leader",
            "Energetic",
            "Action Oriented"
        ])

    # ---------------- Water ----------------

    elif "water" in shape:

        scores["creativity"] += 20
        scores["emotional_intelligence"] += 18
        scores["communication"] += 10

        strengths.extend([
            "Creative",
            "Emotionally Intelligent"
        ])

    # ---------------- Earth ----------------

    elif "earth" in shape:

        scores["decision_making"] += 18
        scores["confidence"] += 10
        scores["stress_management"] += 15

        strengths.extend([
            "Reliable",
            "Practical"
        ])

    # ---------------- Air ----------------

    elif "air" in shape:

        scores["communication"] += 20
        scores["creativity"] += 15
        scores["adaptability"] += 12

        strengths.extend([
            "Analytical",
            "Good Communicator"
        ])

    # ---------------- Heart Line ----------------

    if "curved" in heart:

        scores["optimism"] += 12
        scores["emotional_intelligence"] += 10
        scores["emotional_balance"] += 10

    elif "straight" in heart:

        scores["decision_making"] += 10
        scores["confidence"] += 8
        scores["emotional_balance"] += 5

    # ---------------- Head Line ----------------

    if "long" in head:

        scores["creativity"] += 15
        scores["decision_making"] += 15

    elif "short" in head:

        scores["confidence"] += 8
        scores["risk_taking"] += 10

    # ---------------- Life Line ----------------

    if "deep" in life:

        scores["optimism"] += 15
        scores["stress_management"] += 18
        scores["emotional_balance"] += 15

    elif "faint" in life:

        scores["stress_management"] -= 15
        scores["emotional_balance"] -= 10

        weaknesses.append(
            "Needs better stress management"
        )

    # ---------------- Limit Scores ----------------

    for key in scores:
        scores[key] = max(0, min(100, scores[key]))

    return scores, strengths, weaknesses