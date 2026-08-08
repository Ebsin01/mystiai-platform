from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ai_model_info_endpoint():
    response = client.get("/ai/model-info")

    assert response.status_code == 200
    assert response.json() == {
        "model_name": "LSTM Neural Network",
        "framework": "TensorFlow 2.21.0",
        "test_accuracy": 100.0,
        "categories": ["Career", "Love", "Finance", "Health", "General"],
        "training_samples": 10000,
        "sequence_length": 20,
        "tokenizer_words": 5000,
    }
