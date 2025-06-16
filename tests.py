import os
import unittest
from app import create_app, db
from app.models import User
from config import Config

# --- 1. Създаваме тестова конфигурация ---
# Тя наследява основната, но променя базата данни, за да не пипаме продукционната.
class TestConfig:
    # --- Изрично дефинираме ВСИЧКИ нужни настройки ---
    # Не наследяваме, за да избегнем скрити проблеми.
    TESTING = True
    SECRET_KEY = 'a-secret-key-for-testing'  # Слагаме някакъв ключ
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # In-memory база данни
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False  # Много важно за тестовете

    # Настройки за Flask-Mail, за да не дава грешка, ако се използва
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    ADMINS = ['test@example.com']

    # Настройки, които преди се проваляха
    SERVER_NAME = 'localhost:5000'  # Понякога добавянето на порт помага
    APPLICATION_ROOT = '/'

# --- 2. Създаваме тестовия клас ---
class UserModelCase(unittest.TestCase):
    # setUp се изпълнява ПРЕДИ всеки тест
    def setUp(self):
        self.app = create_app(TestConfig)

        # --- КОРЕКЦИЯ НА ПЪТЯ ---
        # __file__ е tests.py. dirname(__file__) е главната папка.
        # Оттам конструираме пътя до tests/templates
        project_root = os.path.dirname(os.path.abspath(__file__))
        test_templates_path = os.path.join(project_root, 'tests', 'templates')

        # Проверяваме дали пътят е правилен
        print(f"DEBUG: Търся тестови шаблони в: {test_templates_path}")

        # Ако имаш 'jinja_loader'
        if hasattr(self.app, 'jinja_loader'):
            self.app.jinja_loader.searchpath.insert(0, test_templates_path)
        # Ако имаш 'jinja_env' (по-ново)
        elif hasattr(self.app, 'jinja_env'):
            from jinja2 import FileSystemLoader
            # Създаваме нов лоудър, който включва нашия път + оригиналните
            new_loader = FileSystemLoader([test_templates_path] + self.app.jinja_env.loader.searchpath)
            self.app.jinja_env.loader = new_loader

        # -------------------------

        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    # tearDown се изпълнява СЛЕД всеки тест
    def tearDown(self):
        # Премахваме сесията и изтриваме всички таблици
        db.session.remove()
        db.drop_all()
        # Премахваме контекста на приложението
        self.app_context.pop()

    # --- 3. Пишем първия си тест ---
    # Имената на тестовите методи ТРЯБВА да започват с 'test_'
    def test_password_hashing(self):
        # Създаваме нов потребител
        u = User(username='susan')
        # Задаваме му парола
        u.set_password('cat')
        # Проверяваме дали паролата НЕ е записана в явен вид
        self.assertFalse(u.password_hash == 'cat')
        # Проверяваме дали функцията за проверка на парола работи
        self.assertTrue(u.check_password('cat'))
        self.assertFalse(u.check_password('dog'))

    def test_user_registration_and_login(self):
        with self.app.test_client() as client:
            response_register = client.post('/auth/register', data={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'password123',
                'password2': 'password123'
            }, follow_redirects=True)
            self.assertEqual(response_register.status_code, 200)

            # --- КОРЕКЦИЯ ---
            # Декодираме отговора и търсим нормален стринг
            html_data = response_register.get_data(as_text=True)
            self.assertIn('Вход в системата', html_data)

            # ... проверката за user в базата остава същата ...
            with self.app.app_context():
                user = User.query.filter_by(username='testuser').first()
                self.assertIsNotNone(user)

            response_login = client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'password123'
            }, follow_redirects=True)
            self.assertEqual(response_login.status_code, 200)

            # --- КОРЕКЦИЯ ---
            html_data = response_login.get_data(as_text=True)
            self.assertIn('Изход', html_data)

    def test_user_registration_and_login(self):
        with self.app.test_client() as client:
            # --- КОРЕКЦИЯТА Е ТУК ---
            # Връщаме пълния речник с данни за формата
            response_register = client.post('/auth/register', data={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'password123',
                'password2': 'password123'
            }, follow_redirects=True)
            # -------------------------

            self.assertEqual(response_register.status_code, 200)
            html_data = response_register.get_data(as_text=True)
            self.assertIn('Вход в системата', html_data)

            with self.app.app_context():
                user = User.query.filter_by(username='testuser').first()
                self.assertIsNotNone(user)

            response_login = client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'password123'
            }, follow_redirects=True)
            self.assertEqual(response_login.status_code, 200)
            html_data = response_login.get_data(as_text=True)
            self.assertIn('Здравей, testuser!', html_data)

# --- 4. Позволяваме изпълнението на тестовете от командния ред ---
if __name__ == '__main__':
    unittest.main(verbosity=2)