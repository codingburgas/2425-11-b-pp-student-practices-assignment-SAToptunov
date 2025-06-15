import pandas as pd
import numpy as np
import re
import os
from collections import Counter

# --- КОРЕКЦИЯ 1: Динамични и надеждни пътища ---
# Намираме главната директория на проекта
CURRENT_DIR = os.path.dirname(__file__) # Папката ai_model/
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..')) # Главната папка на проекта

# Дефинираме пътищата до файловете, които ще четем и записваме
CSV_PATH = os.path.join(BASE_DIR, 'spam.csv')
OUTPUT_NPZ_PATH = os.path.join(CURRENT_DIR, 'processed_data.npz')


# --- 1. Зареждане на данните ---
print("Стъпка 1: Зареждане на данните...")
try:
    df = pd.read_csv(CSV_PATH, encoding='latin-1')
except FileNotFoundError:
    print(f"Грешка: Файлът '{CSV_PATH}' не е намерен.")
    exit()

df = df[['v1', 'v2']]
df.columns = ['Category', 'Message']
print("Данните са заредени успешно.")
print("-" * 30)

# --- 2. Предварителна обработка (Preprocessing) ---
print("Стъпка 2: Предварителна обработка на текста...")
df['Category'] = df['Category'].map({'spam': 1, 'ham': 0})

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

df['Cleaned_Message'] = df['Message'].apply(clean_text)
print("Текстът е почистен.")
print("-" * 30)


# --- 3. Извличане на признаци (Feature Engineering) - Bag of Words ---
print("Стъпка 3: Извличане на признаци (Bag of Words)...")

word_counts = Counter(" ".join(df['Cleaned_Message']).split())
vocabulary = [word for word, count in word_counts.most_common(2000)]

def message_to_vector(message, vocab):
    word_vector = np.zeros(len(vocab))
    words_in_message = set(message.split()) # Използваме 'set' за по-бърза проверка
    for i, word in enumerate(vocab):
        if word in words_in_message:
            word_vector[i] = 1
    return word_vector

X = np.array(list(df['Cleaned_Message'].apply(lambda msg: message_to_vector(msg, vocabulary))))
y = df['Category'].values

print(f"Създадохме матрица с признаци (X) с размер: {X.shape}")
print("-" * 30)


# --- 4. Разделяне на данните на тренировъчен и тестов сет ---
print("Стъпка 4: Разделяне на данните...")
np.random.seed(42) # Задаваме seed за възпроизводимост на резултатите
shuffled_indices = np.random.permutation(len(X))
X_shuffled = X[shuffled_indices]
y_shuffled = y[shuffled_indices]

split_ratio = 0.8
split_index = int(len(X) * split_ratio)

X_train, X_test = X_shuffled[:split_index], X_shuffled[split_index:]
y_train, y_test = y_shuffled[:split_index], y_shuffled[split_index:]

print(f"Размер на тренировъчния сет: X_train={X_train.shape}")
print(f"Размер на тестовия сет: X_test={X_test.shape}")
print("-" * 30)


# --- 5. Запазване на обработените данни и речника ---
print("Стъпка 5: Запазване на обектите...")

# --- КОРЕКЦИЯ 2: Запазваме речника ВЪТРЕ в .npz файла ---
# Това е единственият файл, от който train_model.py ще има нужда.
np.savez(
    OUTPUT_NPZ_PATH,
    X_train=X_train,
    y_train=y_train,
    X_test=X_test,
    y_test=y_test,
    vocabulary=np.array(vocabulary, dtype=object) # Запазваме и речника
)

print(f"Обработените данни и речникът са запазени в '{OUTPUT_NPZ_PATH}'")
print("Предварителната обработка е завършена!")