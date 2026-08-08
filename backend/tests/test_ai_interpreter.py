import pytest

from app.services.ai_interpreter import generate_three_card_interpretation


@pytest.mark.parametrize(
    ("question", "expected_focus"),
    [
        ("What should I do about my career path?", "career"),
        ("How can I strengthen my relationship?", "relationship"),
        ("Should I invest my savings this year?", "financial"),
    ],
)
def test_generate_three_card_interpretation_is_personalized(question, expected_focus):
    cards = [
        {
            "position": "Past",
            "card_name": "The Fool",
            "orientation": "Upright",
            "meaning": "A new beginning and bold energy.",
        },
        {
            "position": "Present",
            "card_name": "The Magician",
            "orientation": "Upright",
            "meaning": "Manifestation, confidence, and taking action.",
        },
        {
            "position": "Future",
            "card_name": "The Star",
            "orientation": "Upright",
            "meaning": "Hope, healing, and a brighter path ahead.",
        },
    ]

    interpretation = generate_three_card_interpretation(question, cards)
    word_count = len(interpretation.split())

    assert f"Question: {question}" in interpretation
    assert "Past:" in interpretation
    assert "Present:" in interpretation
    assert "Future:" in interpretation
    assert "Overall Guidance:" in interpretation
    assert 200 <= word_count <= 400
    assert expected_focus in interpretation.lower()
