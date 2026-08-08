import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout

# Load dataset
df = pd.read_csv("dataset/questions.csv")

questions = df["question"].astype(str)
labels = df["category"]

# Encode labels
label_encoder = LabelEncoder()
labels_encoded = label_encoder.fit_transform(labels)

# Save label encoder
joblib.dump(label_encoder, "models/label_encoder.pkl")

# Tokenize
tokenizer = Tokenizer(num_words=5000)
tokenizer.fit_on_texts(questions)

joblib.dump(tokenizer, "models/tokenizer.pkl")

sequences = tokenizer.texts_to_sequences(questions)

max_length = 20

X = pad_sequences(
    sequences,
    maxlen=max_length,
    padding="post"
)

y = labels_encoded

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Build model
model = Sequential()

model.add(
    Embedding(
        input_dim=5000,
        output_dim=64
    )
)

model.add(
    LSTM(64)
)

model.add(
    Dropout(0.3)
)

model.add(
    Dense(
        32,
        activation="relu"
    )
)

model.add(
    Dense(
        len(label_encoder.classes_),
        activation="softmax"
    )
)

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

history = model.fit(
    X_train,
    y_train,
    epochs=10,
    validation_split=0.2,
    batch_size=32
)

# Evaluate
loss, accuracy = model.evaluate(X_test, y_test)

print("\nTest Accuracy:", accuracy)

# Save model
model.save("models/question_classifier.keras")

# Accuracy graph
plt.plot(history.history["accuracy"], label="Training")
plt.plot(history.history["val_accuracy"], label="Validation")

plt.title("Model Accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.legend()

plt.savefig("models/accuracy.png")

plt.close()

# Loss graph
plt.plot(history.history["loss"], label="Training")
plt.plot(history.history["val_loss"], label="Validation")

plt.title("Model Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()

plt.savefig("models/loss.png")

print("\nModel saved successfully!")