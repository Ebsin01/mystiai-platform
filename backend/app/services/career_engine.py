def recommend_career(scores):

    if scores["leadership"] >= 85:

        return "Management, Entrepreneurship, Defence Officer, IPS"

    if scores["creativity"] >= 85:

        return "AI Engineer, Designer, Content Creator, Writer"

    if scores["decision_making"] >= 85:

        return "Software Engineer, Cybersecurity Analyst, Business Analyst"

    return "Technology, Administration, Engineering"