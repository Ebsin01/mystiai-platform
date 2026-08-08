import json

from app.services.personality_rules import calculate_scores
from app.services.career_engine import recommend_career
from app.services.relationship_engine import relationship_advice
from app.services.health_engine import health_advice
from app.services.personality_summary import generate_summary
from app.services.gemini_service import generate_ai_report


def generate_personality_report(analysis):

    # Generate numerical scores from palm analysis
    scores, strengths, weaknesses = calculate_scores(analysis)

    try:
        # Get AI report from Gemini
        ai = generate_ai_report(scores)
        print("=" * 50)
        print("AI RESPONSE:")
        print(ai)
        print(type(ai))
        print("=" * 50)

        # If Gemini returns a string, convert it to JSON
        if isinstance(ai, str):
            ai = ai.replace("```json", "").replace("```", "").strip()
            ai = json.loads(ai)

        # Merge scores with AI report
        report = {
            **scores,

            "personality_type": ai.get("personality_type", "Balanced Personality"),

            "strengths": ai.get(
                "strengths",
                ", ".join(strengths)
            ),

            "weaknesses": ai.get(
                "weaknesses",
                ", ".join(weaknesses)
            ),

            "career": ai.get(
                "career",
                recommend_career(scores)
            ),

            "relationship": ai.get(
                "relationship",
                relationship_advice(scores)
            ),

            "health": ai.get(
                "health",
                health_advice(scores)
            ),

            "summary": ai.get(
                "summary",
                generate_summary(scores)[1]
            )
        }

        return report

    except Exception as e:

        print("=" * 60)
        print("GEMINI FAILED")
        print(e)
        print("=" * 60)

        # Fallback to rule-based report
        personality_type, summary = generate_summary(scores)

        return {
            **scores,

            "personality_type": personality_type,

            "strengths": ", ".join(strengths),

            "weaknesses": ", ".join(weaknesses),

            "career": recommend_career(scores),

            "relationship": relationship_advice(scores),

            "health": health_advice(scores),

            "summary": summary,
        }