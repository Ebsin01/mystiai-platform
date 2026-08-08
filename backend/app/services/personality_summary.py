def generate_summary(scores):

    if scores["leadership"] > 85:

        personality = "Visionary Leader"

    elif scores["creativity"] > 85:

        personality = "Creative Thinker"

    elif scores["communication"] > 85:

        personality = "Excellent Communicator"

    elif scores["decision_making"] > 85:

        personality = "Strategic Planner"

    else:

        personality = "Balanced Individual"

    summary = (
        f"You are a {personality}. "
        "Your personality demonstrates confidence, adaptability, and "
        "a balanced approach to personal and professional life."
    )

    return personality, summary