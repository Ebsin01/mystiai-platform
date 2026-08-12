import os
import json
import logging
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Logging setup
logger = logging.getLogger(__name__)

# Global variable for lazy loading
_gemini_client = None


def _initialize_gemini_client():
    """
    Initialize the Gemini client on first use.
    This is called lazily to avoid startup issues if the API key is not set.
    """
    global _gemini_client
    
    if _gemini_client is not None:
        return _gemini_client
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        error_msg = (
            "GEMINI_API_KEY environment variable is not set. "
            "AI interpretation features will be unavailable. "
            "Please set GEMINI_API_KEY to enable Google Gemini AI features."
        )
        logger.warning(error_msg)
        raise RuntimeError(error_msg)
    
    try:
        logger.info("Initializing Google Gemini API client")
        _gemini_client = genai.Client(api_key=api_key)
        logger.info("Google Gemini API client initialized successfully")
        return _gemini_client
    except Exception as e:
        error_msg = f"Failed to initialize Gemini client: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def generate_ai_report(scores):
    """
    Generate a personality report using Google Gemini AI.
    
    Args:
        scores: Dictionary of personality scores
        
    Returns:
        Dictionary with personality report data
    """
    try:
        # Lazy load the Gemini client
        client = _initialize_gemini_client()

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

        logger.debug("Calling Gemini API for personality report generation")

        response = client.models.generate_content(
            model="models/gemini-3.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        logger.debug(f"Gemini response received ({len(text)} chars)")

        # Remove markdown if Gemini wraps the JSON
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()
        elif text.startswith("```"):
            text = text.replace("```", "").strip()

        try:
            return json.loads(text)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {str(e)}")
            logger.error(f"Raw response: {text}")

            return {
                "personality_type": "Balanced Individual",
                "summary": text,
                "career": "",
                "relationship": "",
                "health": "",
                "strengths": "",
                "weaknesses": ""
            }
    
    except RuntimeError as e:
        logger.error(f"Gemini service error: {str(e)}")
        # Return a safe fallback response
        return {
            "personality_type": "Unable to generate",
            "summary": "AI service unavailable",
            "career": "",
            "relationship": "",
            "health": "",
            "strengths": "",
            "weaknesses": "",
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error during AI report generation: {str(e)}")
        return {
            "personality_type": "Unable to generate",
            "summary": "An error occurred during report generation",
            "career": "",
            "relationship": "",
            "health": "",
            "strengths": "",
            "weaknesses": "",
            "error": str(e)
        }


if __name__ == "__main__":
    # Show all available models
    for model in client.models.list():
        print(model.name)