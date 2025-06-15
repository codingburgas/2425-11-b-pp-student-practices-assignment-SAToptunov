# app/classifier/utils.py
import traceback

import joblib
import numpy as np
import re
import os
import sys

# Дефинираме пътищата до файловете на модела веднъж
# Това е по-стабилно от относителни пътища
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from ai_model.logistic_regression_model import LogisticRegression
import traceback

MODEL_PATH = os.path.join(BASE_DIR, 'ai_model', 'spam_classifier_model.pkl')
VOCAB_PATH = os.path.join(BASE_DIR, 'ai_model', 'vocabulary.pkl')

print("--- ДЕБЪГ НА ПЪТИЩАТА ---")
print(f"Изчислен базов път (BASE_DIR): {BASE_DIR}")
print(f"Пълен път до модела (MODEL_PATH): {MODEL_PATH}")
print(f"Пълен път до речника (VOCAB_PATH): {VOCAB_PATH}")
print("-------------------------")

# Зареждаме модела и речника
model = None
vocabulary = None

print("--- ПРОВЕРКА НА СЪЩЕСТВУВАНЕТО НА ФАЙЛОВЕ ---")

# Проверка за файла на модела
if not os.path.exists(MODEL_PATH):
    print(f"ГРЕШКА: Файлът на модела НЕ Е НАМЕРЕН на път: {MODEL_PATH}")
else:
    print(f"OK: Файлът на модела е намерен на път: {MODEL_PATH}")
    try:
        model = joblib.load(MODEL_PATH)
        print(">>> Моделът е зареден успешно.")
    except Exception as e:
        print(f"ГРЕШКА при зареждане на модела: {e}")
        traceback.print_exc()

        # Проверка за файла на речника
if not os.path.exists(VOCAB_PATH):
    print(f"ГРЕШКА: Файлът на речника НЕ Е НАМЕРЕН на път: {VOCAB_PATH}")
else:
    print(f"OK: Файлът на речника е намерен на път: {VOCAB_PATH}")
    try:
        vocabulary = joblib.load(VOCAB_PATH)
        print(">>> Речникът е зареден успешно.")
    except Exception as e:
        print(f"ГРЕШКА при зареждане на речника: {e}")

print("-------------------------------------------------")



def clean_text(text):
    """Почиства текста по същия начин, както при обучението."""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text


def message_to_vector(message, vocab):
    """Превръща текстово съобщение в числов вектор (Bag of Words)."""
    word_vector = np.zeros(len(vocab))
    words_in_message = message.split()
    for i, word in enumerate(vocab):
        if word in words_in_message:
            word_vector[i] = 1
    return word_vector


def classify_message(message):
    """
    Основната функция, която приема съобщение и връща предсказание.
    Връща: (клас, вероятност) -> ('Spam', 0.98) или ('Ham', 0.05)
    """
    if model is None or vocabulary is None:
        return "Грешка: Моделът не е зареден.", 0.0

    cleaned_message = clean_text(message)
    vector = message_to_vector(cleaned_message, vocabulary)

    # Моделът очаква 2D масив, затова преоразмеряваме вектора
    vector_reshaped = vector.reshape(1, -1)

    # Предсказване
    prediction_class = model.predict(vector_reshaped)[0]
    prediction_proba = model.predict_proba(vector_reshaped)[0]

    if prediction_class == 1:
        return "Spam", prediction_proba
    else:
        # За Ham, вероятността е 1 - P(Spam)
        return "Ham (Not Spam)", 1 - prediction_proba