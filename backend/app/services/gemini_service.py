import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

print("===== GEMINI SERVICE LOADED =====")
print(__file__)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_ai_report(scores):

    prompt = f"""
You are an expert Palmistry Personality Analyst.

Based on the following personality scores, generate a professional personality report.

Scores:

Optimism: {scores["optimism"]}
Leadership: {scores["leadership"]}
Confidence: {scores["confidence"]}
Creativity: {scores["creativity"]}
Communication: {scores["communication"]}
Decision Making: {scores["decision_making"]}
Emotional Intelligence: {scores["emotional_intelligence"]}
Stress Management: {scores["stress_management"]}
Adaptability: {scores["adaptability"]}
Risk Taking: {scores["risk_taking"]}
Emotional Balance: {scores["emotional_balance"]}

Return ONLY valid JSON.

{{
    "personality_type":"",
    "summary":"",
    "career":"",
    "relationship":"",
    "health":"",
    "strengths":"",
    "weaknesses":""
}}
"""

    print("USING GEMINI 2.5 PRO")

    response = client.models.generate_content(
        model="models/gemini-3.5-flash",
        contents=prompt
    )

    text = response.text.strip()

    print("========== GEMINI RAW RESPONSE ==========")
    print(text)
    print("=========================================")

    # Remove markdown if Gemini wraps the JSON
    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()

    try:
        return json.loads(text)

    except Exception as e:
        print("JSON Parse Error:", e)
        print("Returned Text:")
        print(text)

        return {
            "personality_type": "Balanced Individual",
            "summary": text,
            "career": "",
            "relationship": "",
            "health": "",
            "strengths": "",
            "weaknesses": ""
        }


if __name__ == "__main__":
    # Show all available models
    for model in client.models.list():
        print(model.name)