import os
import json
import logging

logger = logging.getLogger(__name__)

# Fetch AI provider API key securely from environment variables
AI_API_KEY = os.getenv("AI_API_KEY")
AI_PROVIDER = os.getenv("AI_PROVIDER", "mock") # e.g., 'openai', 'gemini', 'mock'

def _call_mock_ai(prompt: str) -> dict:
    """
    Fallback mock AI provider when no actual AI is configured.
    Returns a generic structured response based on the prompt.
    """
    return {
        "personality": "You are a naturally thoughtful individual who balances logic with intuition. Your measurements indicate a practical yet creative mindset.",
        "career": "You are likely to thrive in environments that require both structural planning and imaginative problem-solving. Roles in technology, design, or management suit you well.",
        "relationships": "In relationships, you value honesty and deep emotional connections. You offer loyalty and expect the same in return.",
        "life": "Your overall life trajectory suggests steady growth. You learn from your past experiences and adapt well to new challenges.",
        "overall_summary": "Overall, you possess a harmonious blend of energy and calmness. (Note: This is an AI generated entertainment reading, not professional advice.)"
    }

def _call_openai(prompt: str) -> dict:
    """
    Abstraction for OpenAI integration.
    """
    # Note: Requires `import openai` and proper setup.
    # openai.api_key = AI_API_KEY
    # response = openai.ChatCompletion.create(...)
    # return json.loads(response.choices[0].message.content)
    raise NotImplementedError("OpenAI provider is not fully implemented yet. Configure dependencies.")

def _call_gemini(prompt: str) -> dict:
    """
    Abstraction for Gemini integration.
    """
    # Note: Requires `import google.generativeai as genai`
    # genai.configure(api_key=AI_API_KEY)
    # model = genai.GenerativeModel('gemini-pro')
    # response = model.generate_content(prompt)
    # return json.loads(response.text)
    raise NotImplementedError("Gemini provider is not fully implemented yet. Configure dependencies.")

def generate_ai_interpretation(
    palm_shape: str,
    palm_width: float,
    palm_length: float,
    index_finger_length: float,
    middle_finger_length: float,
    landmarks: list
) -> dict:
    """
    Generates a personalized AI palmistry interpretation.
    """
    
    prompt = f"""
    You are an expert AI Palm Reader. Analyze the following palm measurements and generate a reading.
    
    Data:
    - Palm Shape: {palm_shape}
    - Palm Width: {palm_width}
    - Palm Length: {palm_length}
    - Index Finger Length: {index_finger_length}
    - Middle Finger Length: {middle_finger_length}
    - Landmarks Count: {len(landmarks) if landmarks else 0}
    
    Provide a JSON response with exactly the following keys, containing your interpretation paragraphs:
    - "personality"
    - "career"
    - "relationships"
    - "life"
    - "overall_summary"
    
    Make it sound mystical but grounded. Ensure it is purely for entertainment.
    """

    try:
        if AI_PROVIDER.lower() == "openai" and AI_API_KEY:
            return _call_openai(prompt)
        elif AI_PROVIDER.lower() == "gemini" and AI_API_KEY:
            return _call_gemini(prompt)
        else:
            logger.warning("No valid AI provider configured. Falling back to mock AI.")
            return _call_mock_ai(prompt)
    except Exception as e:
        logger.error(f"AI Interpretation failed: {e}")
        # Fallback in case of AI service outage
        return _call_mock_ai(prompt)
