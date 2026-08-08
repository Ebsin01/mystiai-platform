import pandas as pd
import random

career = [
    "Will I get a software developer job?",
    "Will I get placed this year?",
    "How is my career?",
    "Will I receive a promotion?",
    "Can I become a software engineer?",
    "Will I get an internship?",
    "Should I switch my job?",
    "Will I work abroad?",
    "Can I clear my interview?",
    "Will my career grow?"
]

love = [
    "How is my love life?",
    "Will I get married?",
    "Does my partner love me?",
    "Will my relationship improve?",
    "Will I find true love?",
    "Should I propose?",
    "Is my relationship stable?",
    "Will my ex come back?",
    "Will I meet my soulmate?",
    "Will my marriage be happy?"
]

finance = [
    "Will I become rich?",
    "How is my financial future?",
    "Should I invest?",
    "Will my business grow?",
    "Will my salary increase?",
    "Can I buy a house?",
    "Should I save money?",
    "Will I earn more?",
    "Will I become financially stable?",
    "How is my income?"
]

health = [
    "How is my health?",
    "Will I recover soon?",
    "Should I exercise more?",
    "Will my health improve?",
    "Am I healthy?",
    "Should I change my lifestyle?",
    "Will I stay fit?",
    "Can I recover completely?",
    "How is my fitness?",
    "Will I overcome my illness?"
]

general = [
    "What does my future look like?",
    "What does destiny have for me?",
    "How is my future?",
    "What should I expect in life?",
    "What lies ahead?",
    "What is my destiny?",
    "How will my future be?",
    "What opportunities await me?",
    "What should I prepare for?",
    "Tell me about my future."
]

data = []

for _ in range(2000):
    data.append([random.choice(career), "Career"])
    data.append([random.choice(love), "Love"])
    data.append([random.choice(finance), "Finance"])
    data.append([random.choice(health), "Health"])
    data.append([random.choice(general), "General"])

random.shuffle(data)

df = pd.DataFrame(data, columns=["question", "category"])

df.to_csv("dataset/questions.csv", index=False)

print("Dataset created successfully!")
print("Total samples:", len(df))