from predict import predict_category

questions = [
    "Will I get a software developer job?",
    "How is my love life?",
    "Should I invest in business?",
    "How is my health?",
    "Tell me about my future."
]

for q in questions:

    result = predict_category(q)

    print()

    print("Question :", q)

    print("Prediction :", result)