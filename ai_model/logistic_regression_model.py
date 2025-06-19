import numpy as np


class LogisticRegression:
    """
    Имплементация на Логистична Регресия от нулата с NumPy.
    """

    def __init__(self, learning_rate=0.1, n_iterations=1500, verbose=True):
        """
        Инициализация на модела.

        Args:
            learning_rate (float): Стъпка на обучение. Контролира колко големи са промените
                                   в теглата при всяка итерация.
            n_iterations (int): Брой итерации (епохи) за обучение.
            verbose (bool): Ако е True, ще принтира информация за грешката по време на обучение.
        """
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.verbose = verbose
        self.weights = None  # Теглата на модела (w)
        self.bias = None  # Свободният член (b)

    def get_feature_weights(self):
        """
        Прост метод, който връща научените тегла за всеки признак.
        """
        return self.weights

    def _sigmoid(self, z):
        """
        Сигмоидна активационна функция.
        Тя преобразува всяко реално число в стойност между 0 и 1, което може да се
        интерпретира като вероятност.
        Формула: S(z) = 1 / (1 + e^(-z))
        """
        # Добавяме клипинг за избягване на overflow при много големи/малки стойности на z
        z = np.clip(z, -500, 500)
        return 1 / (1 + np.exp(-z))

    def fit(self, X, y):
        """
        Обучение на модела с помощта на Gradient Descent.

        Args:
            X (np.array): Матрица с признаци (тренировъчни данни). Shape: (n_samples, n_features)
            y (np.array): Вектор с етикети (0 или 1). Shape: (n_samples,)
        """
        n_samples, n_features = X.shape

        # 1. Инициализация на параметрите (тегла и свободен член) с нули.
        self.weights = np.zeros(n_features)
        self.bias = 0

        # Преоразмеряваме y, за да е сигурно, че е вектор-колона
        y = y.reshape(-1, 1)

        # 2. Оптимизационен цикъл (Gradient Descent)
        for i in range(self.n_iterations):
            # Изчисляване на линейната комбинация: z = X.w + b
            linear_model = np.dot(X, self.weights) + self.bias

            # Прилагане на сигмоидната функция за получаване на предсказания (вероятности)
            y_predicted = self._sigmoid(linear_model).reshape(-1, 1)

            # Изчисляване на грешката (cost) с Binary Cross-Entropy (за да следим прогреса)
            # Това е една от метриките, които се изискват.
            cost = - (1 / n_samples) * np.sum(y * np.log(y_predicted) + (1 - y) * np.log(1 - y_predicted))

            # Изчисляване на градиентите (производните) спрямо теглата и свободния член
            # Те показват посоката, в която трябва да променим параметрите, за да намалим грешката.
            dw = (1 / n_samples) * np.dot(X.T, (y_predicted - y))
            db = (1 / n_samples) * np.sum(y_predicted - y)

            # 3. Актуализиране на параметрите
            # "Стъпваме" в обратната посока на градиента.
            self.weights -= self.learning_rate * dw.flatten()
            self.bias -= self.learning_rate * db

            # Принтиране на прогреса на всеки 100 итерации
            if self.verbose and i % 100 == 0:
                print(f"Итерация {i}: Loss = {cost:.4f}")

    def predict_proba(self, X):
        """
        Предсказва вероятността даден пример да е от клас 1 (спам).
        """
        linear_model = np.dot(X, self.weights) + self.bias
        return self._sigmoid(linear_model)

    def predict(self, X, threshold=0.5):
        """
        Предсказва крайния клас (0 или 1).
        Ако вероятността е > от прага (threshold), класът е 1 (спам), иначе е 0 (ham).
        """
        probabilities = self.predict_proba(X)
        return (probabilities >= threshold).astype(int)