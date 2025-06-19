# app/classifier/utils.py

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

MODEL_PATH = os.path.join(BASE_DIR, 'ai_model', 'spam_classifier_model.pkl')
VOCAB_PATH = os.path.join(BASE_DIR, 'ai_model', 'vocabulary.pkl')

# Зареждаме модела и речника
model = joblib.load(MODEL_PATH)
vocabulary = joblib.load(VOCAB_PATH)

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