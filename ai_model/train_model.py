import os
import json
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# Използване на относителен импорт
from .logistic_regression_model import LogisticRegression


# ==============================================================================
# --- СЕКЦИЯ 1: ДЕФИНИРАНЕ НА МЕТРИКИ ЗА ОЦЕНКА ---
# ==============================================================================

def accuracy_score(y_true, y_pred):
    """Изчислява точността (accuracy)."""
    return np.sum(y_true == y_pred) / len(y_true)


def error_rate(y_true, y_pred):
    """Изчислява процента грешки (error rate)."""
    return 1 - accuracy_score(y_true, y_pred)


def binary_cross_entropy(y_true, y_pred_proba):
    """Изчислява Binary Cross-Entropy Loss (Ентропия)."""
    epsilon = 1e-15
    y_pred_proba = np.clip(y_pred_proba, epsilon, 1 - epsilon)
    return -np.mean(y_true * np.log(y_pred_proba) + (1 - y_true) * np.log(1 - y_pred_proba))


def precision_recall_f1_score(y_true, y_pred):
    """Изчислява Precision, Recall и F1-Score."""
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    epsilon = 1e-7
    precision = tp / (tp + fp + epsilon)
    recall = tp / (tp + fn + epsilon)
    f1 = 2 * (precision * recall) / (precision + recall + epsilon)
    return precision, recall, f1


def plot_and_save_confusion_matrix(y_true, y_pred, output_dir):
    """Създава и запазва графика на матрицата на объркванията."""
    os.makedirs(output_dir, exist_ok=True)
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    tp = np.sum((y_true == 1) & (y_pred == 1))
    matrix = [[tn, fp], [fn, tp]]

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(matrix, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=['Ham (Predicted)', 'Spam (Predicted)'],
                yticklabels=['Ham (Actual)', 'Spam (Actual)'])
    ax.set_title('Матрица на объркванията (Confusion Matrix)')
    ax.set_ylabel('Реален етикет')
    ax.set_xlabel('Предсказан етикет')

    matrix_path = os.path.join(output_dir, 'confusion_matrix.png')
    plt.savefig(matrix_path, bbox_inches='tight')
    plt.close(fig)
    print(f"\nМатрицата на объркванията е запазена в '{matrix_path}'")
    return matrix_path


# ==============================================================================
# --- ОСНОВНА ЛОГИКА НА СКРИПТА ---
# ==============================================================================

# Динамично намиране на пътищата
CURRENT_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(CURRENT_DIR, 'processed_data.npz')
MODEL_PATH = os.path.join(CURRENT_DIR, 'spam_classifier_model.pkl')
VOCAB_PATH = os.path.join(CURRENT_DIR, 'vocabulary.pkl')
STATS_PATH = os.path.join(CURRENT_DIR, 'model_stats.json')

# --- 1. Зареждане на данни ---
print("Стъпка 1: Зареждане на данните...")
try:
    data = np.load(DATA_PATH, allow_pickle=True)
    X_train, y_train = data['X_train'], data['y_train']
    X_test, y_test = data['X_test'], data['y_test']
    vocabulary = data['vocabulary']
    print("Данните и речникът са заредени успешно.")
    print("-" * 30)
except FileNotFoundError:
    print(f"Грешка: Файлът '{DATA_PATH}' не е намерен. Моля, първо изпълнете 'main_preprocessing.py'.")
    exit()

# --- 2. Трениране на модела ---
print("Стъпка 2: Трениране на модела Logistic Regression...")
model = LogisticRegression(learning_rate=0.1, n_iterations=1000, verbose=True)
model.fit(X_train, y_train)
print("Моделът е обучен.")
print("-" * 30)

# --- 3. Оценка на модела ---
print("Стъпка 3: Оценка на модела върху тестовите данни...")
y_pred_test = model.predict(X_test)
y_pred_proba_test = model.predict_proba(X_test)

# Изчисляване на всички метрики
accuracy = accuracy_score(y_test, y_pred_test)
error = error_rate(y_test, y_pred_test)
loss = binary_cross_entropy(y_test, y_pred_proba_test)
precision, recall, f1 = precision_recall_f1_score(y_test, y_pred_test)

print(f"Точност (Accuracy): {accuracy:.4f} ({accuracy * 100:.2f}%)")
print(f"Ентропия (Log-Loss): {loss:.4f}")
print("-" * 20)
print("Детайлни метрики за класификация:")
print(f"Прецизност (Precision): {precision:.4f}")
print(f"Обхват (Recall): {recall:.4f}")
print(f"F1-Score: {f1:.4f}")

# Генериране и запазване на Confusion Matrix
saved_matrix_path = plot_and_save_confusion_matrix(y_test, y_pred_test, output_dir=CURRENT_DIR)

# --- 4. Анализ на теглата и запазване на статистики ---
print("\n" + "-" * 20)
print("Анализ и запазване на статистики...")

feature_weights = model.get_feature_weights()
features_df = pd.DataFrame({'word': vocabulary, 'weight': feature_weights})
top_spam_words = features_df.sort_values(by='weight', ascending=False).head(10)
top_ham_words = features_df.sort_values(by='weight', ascending=True).head(10)

print("\nТоп 10 думи, сочещи към SPAM:")
print(top_spam_words.to_string(index=False))
print("\nТоп 10 думи, сочещи към HAM (НЕ-SPAM):")
print(top_ham_words.to_string(index=False))

# Събиране на всички статистики в един речник
model_stats = {
    'accuracy': accuracy,
    'logloss': loss,
    'precision': precision,
    'recall': recall,
    'f1_score': f1,
    'top_spam_words': top_spam_words.to_dict('records'),
    'top_ham_words': top_ham_words.to_dict('records'),
    'confusion_matrix_path': os.path.join('ai_model', os.path.basename(saved_matrix_path))
}

# Запазване на статистиките в JSON файл
with open(STATS_PATH, 'w', encoding='utf-8') as f:
    json.dump(model_stats, f, ensure_ascii=False, indent=4)
print(f"\nМетриките са запазени в '{STATS_PATH}'")

print("-" * 30)

# --- 5. Запазване на тренирания модел и речника ---
print("Стъпка 5: Запазване на финалните артефакти...")
joblib.dump(model, MODEL_PATH)
joblib.dump(vocabulary, VOCAB_PATH)
print(f"Моделът е запазен в '{MODEL_PATH}'")
print(f"Речникът е запазен в '{VOCAB_PATH}'")
print("\nТренировъчният процес е завършен!")