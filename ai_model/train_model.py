import numpy as np
import joblib
import os

# --- КОРЕКЦИЯ 1: Използване на относителен импорт ---
# Тъй като train_model.py и logistic_regression_model.py са в един и същи пакет (ai_model),
# използваме точка (.), за да кажем на Python да търси в текущата папка.
from logistic_regression_model import LogisticRegression

# --- 1. Дефиниране на метрики за оценка (Изискване 5) ---
# Това е направено отлично, оставяме го както е.

def accuracy_score(y_true, y_pred):
    """Изчислява точността (accuracy)."""
    correct_predictions = np.sum(y_true == y_pred)
    return correct_predictions / len(y_true)

def error_rate(y_true, y_pred):
    """Изчислява процента грешки (error rate)."""
    return 1 - accuracy_score(y_true, y_pred)

def binary_cross_entropy(y_true, y_pred_proba):
    """Изчислява Binary Cross-Entropy Loss."""
    epsilon = 1e-15
    y_pred_proba = np.clip(y_pred_proba, epsilon, 1 - epsilon)
    return -np.mean(y_true * np.log(y_pred_proba) + (1 - y_true) * np.log(1 - y_pred_proba))


# --- КОРЕКЦИЯ 2: Динамично намиране на пътищата ---
# Това прави скрипта независим от това от коя директория се стартира.
# __file__ е пътят до текущия файл (train_model.py)
# os.path.dirname(__file__) е папката, в която се намира (ai_model/)
CURRENT_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(CURRENT_DIR, 'processed_data.npz')
MODEL_PATH = os.path.join(CURRENT_DIR, 'spam_classifier_model.pkl')
# Речникът ще бъде запазен в същата папка, но трябва да го заредим от данните първо.
VOCAB_PATH = os.path.join(CURRENT_DIR, 'vocabulary.pkl')


# --- 2. Зареждане на обработените данни ---
print("Стъпка 1: Зареждане на данните...")
try:
    # Зареждаме от динамично изчисления път
    data = np.load(DATA_PATH, allow_pickle=True)
    X_train, y_train = data['X_train'], data['y_train']
    X_test, y_test = data['X_test'], data['y_test']
    # Зареждаме речника, който е запазен по време на препроцесинга
    vocabulary = data['vocabulary']
    print("Данните и речникът са заредени успешно.")
    print("-" * 30)
except FileNotFoundError:
    print(f"Грешка: Файлът '{DATA_PATH}' не е намерен.")
    print("Моля, първо изпълнете 'ai_model/main_preprocessing.py'.")
    exit()


# --- 3. Трениране на модела ---
print("Стъпка 2: Трениране на модела Logistic Regression...")
model = LogisticRegression(learning_rate=0.1, n_iterations=1500, verbose=True)
model.fit(X_train, y_train)
print("Моделът е обучен.")
print("-" * 30)


# --- 4. Оценка на модела ---
print("Стъпка 3: Оценка на модела върху тестовите данни...")
y_pred_test = model.predict(X_test)
y_pred_proba_test = model.predict_proba(X_test)

accuracy = accuracy_score(y_test, y_pred_test)
error = error_rate(y_test, y_pred_test)
loss = binary_cross_entropy(y_test, y_pred_proba_test)

print(f"Точност (Accuracy): {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"Процент грешки (Error Rate): {error:.4f} ({error*100:.2f}%)")
print(f"Загуба (Loss) на тестовия сет: {loss:.4f}")
print("-" * 30)


# --- 5. Запазване на тренирания модел и речника ---
print("Стъпка 4: Запазване на тренирания модел и речника...")
# Запазваме на динамично изчислените пътища
joblib.dump(model, MODEL_PATH)
joblib.dump(vocabulary, VOCAB_PATH) # Запазваме и речника!
print(f"Моделът е запазен в '{MODEL_PATH}'")
print(f"Речникът е запазен в '{VOCAB_PATH}'")
print("Тренировъчният процес е завършен!")