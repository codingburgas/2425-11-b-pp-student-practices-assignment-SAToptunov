# app/classifier/utils.py

import joblib
import numpy as np
import re
import os
import sys

# --- 1. Дефинираме пътищата и променливите, но ги оставяме празни (None) ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from ai_model.logistic_regression_model import LogisticRegression

MODEL_PATH = os.path.join(BASE_DIR, 'ai_model', 'spam_classifier_model.pkl')
VOCAB_PATH = os.path.join(BASE_DIR, 'ai_model', 'vocabulary.pkl')

# Глобални променливи за модела и речника
model = None
vocabulary = None


def load_model_if_needed():
    global model, vocabulary
    if model is None or vocabulary is None:
        print("--- AI моделът не е зареден. Зареждам го сега... ---")
        try:
            model = joblib.load(MODEL_PATH)
            vocabulary = joblib.load(VOCAB_PATH)
            print("--- Моделът и речникът са заредени успешно. ---")
        except Exception as e:
            print(f"ГРЕШКА при зареждане на модела: {e}")
            pass


def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text


def message_to_vector(message, vocab):
    word_vector = np.zeros(len(vocab))
    words_in_message = set(message.split())
    for i, word in enumerate(vocab):
        if word in words_in_message:
            word_vector[i] = 1
    return word_vector


# --- 3. Основната ни функция първо извиква функцията за зареждане ---
def classify_message(message):
    """
    Основната функция, която приема съобщение и връща предсказание.
    """
    load_model_if_needed()

    if model is None or vocabulary is None:
        return "Грешка: AI моделът не е наличен или не може да бъде зареден.", 0.0

    cleaned_message = clean_text(message)
    vector = message_to_vector(cleaned_message, vocabulary)
    vector_reshaped = vector.reshape(1, -1)

    # --- КОРЕКЦИЯ НА ЛОГИКАТА ---
    # predict_proba връща само една вероятност (за клас 1 - Spam)
    prob_spam = model.predict_proba(vector_reshaped)[0]

    # Сравняваме я директно с нашия праг (0.5)
    if prob_spam > 0.5:
        # Връщаме класа "Spam" и неговата вероятност
        return "Spam", prob_spam
    else:
        # Връщаме класа "Ham" и неговата вероятност (която е 1 - prob_spam)
        return "Ham (Not Spam)", 1 - prob_spam