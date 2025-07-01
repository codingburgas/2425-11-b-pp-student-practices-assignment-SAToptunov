# app/classifier/utils.py

import joblib
import numpy as np
import re
import os
import sys
import json

# --- 1. Дефинираме пътищата и променливите, но ги оставяме празни (None) ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from ai_model.logistic_regression_model import LogisticRegression

STATS_PATH = os.path.join(BASE_DIR, 'ai_model', 'model_stats.json')
MODEL_PATH = os.path.join(BASE_DIR, 'ai_model', 'spam_classifier_model.pkl')
VOCAB_PATH = os.path.join(BASE_DIR, 'ai_model', 'vocabulary.pkl')

# Глобални променливи за модела и речника
model = None
vocabulary = None
model_stats = None

def load_model_if_needed():
    global model, vocabulary, model_stats
    if model is None or vocabulary is None or model_stats is None:
        print("--- AI ресурсите не са заредени. Зареждам ги сега... ---")
        try:
            model = joblib.load(MODEL_PATH)
            vocabulary = joblib.load(VOCAB_PATH)
            with open(STATS_PATH, 'r', encoding='utf-8') as f:
                model_stats = json.load(f)
            print("--- Модел, речник и статистики са заредени успешно. ---")
        except Exception as e:
            print(f"ГРЕШКА при зареждане на AI ресурси: {e}")
            pass


def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

def get_model_stats():
    """
    Връща заредените статистики. Уверява се, че са заредени, ако не са.
    """
    load_model_if_needed()
    return model_stats

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