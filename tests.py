import os
import unittest
from app import create_app, db
from app.models import User, Role
from config import Config
from itsdangerous import URLSafeTimedSerializer
from flask_login import login_user


class TestConfig:
    TESTING = True
    SECRET_KEY = 'a-secret-key-for-testing'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    ADMINS = ['admin@example.com']
    SERVER_NAME = 'localhost:5000'
    APPLICATION_ROOT = '/'


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        from jinja2 import ChoiceLoader, FileSystemLoader
        app_templates_path = os.path.join(self.app.root_path, 'templates')
        test_templates_path = os.path.join(os.path.dirname(__file__), 'tests', 'templates')
        self.app.jinja_loader = ChoiceLoader([
            FileSystemLoader(test_templates_path),
            FileSystemLoader(app_templates_path)
        ])
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan', email='susan@example.com')
        u.set_password('cat')
        self.assertFalse(u.password_hash == 'cat')
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
            html_data = response_register.get_data(as_text=True)
            self.assertIn('Вход в системата', html_data)
            with self.app.app_context():
                user = User.query.filter_by(username='testuser').first()
                self.assertIsNotNone(user)
                self.assertEqual(user.role.name, 'User')
            response_login = client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'password123'
            }, follow_redirects=True)
            self.assertEqual(response_login.status_code, 200)
            html_data = response_login.get_data(as_text=True)
            self.assertIn('Здравей, testuser!', html_data)

    def test_anonymous_user_access(self):
        with self.app.test_client() as client:
            response_profile = client.get('/user/testuser', follow_redirects=True)
            response_classify = client.get('/classify', follow_redirects=True)
            self.assertIn('Вход в системата', response_profile.get_data(as_text=True))
            self.assertIn('Вход в системата', response_classify.get_data(as_text=True))

    def test_email_confirmation(self):
        with self.app.test_client() as client:
            client.post('/auth/register', data={
                'username': 'confirm_user',
                'email': 'confirm@example.com',
                'password': 'password',
                'password2': 'password'
            })
            client.post('/auth/login', data={'username': 'confirm_user', 'password': 'password'})
            user = User.query.filter_by(username='confirm_user').first()
            self.assertFalse(user.email_confirmed)
            serializer = URLSafeTimedSerializer(self.app.config['SECRET_KEY'])
            token = serializer.dumps(user.email, salt='email-confirmation-salt')
            response_confirm = client.get(f'/auth/confirm/{token}', follow_redirects=True)
            self.assertEqual(response_confirm.status_code, 200)
            self.assertIn('Здравей, confirm_user!', response_confirm.get_data(as_text=True))
            self.assertTrue(user.email_confirmed)

    def test_admin_access(self):
        # Използваме with, за да сме сигурни, че имаме контекст за всичко
        with self.app.test_request_context():
            # Създаваме потребителите
            role_user = Role.query.filter_by(name='User').first()
            role_admin = Role.query.filter_by(name='Admin').first()

            user = User(username='normal_user', email='user@example.com', role=role_user)
            admin_user = User(username='admin_user', email='admin@example.com', role=role_admin)

            # Задаваме им пароли, за да е по-реалистично
            user.set_password('password')
            admin_user.set_password('password')

            db.session.add_all([user, admin_user])
            db.session.commit()

            # --- НАЧАЛО НА ПРОМЕНИТЕ В ТЕСТА ---
            client = self.app.test_client()

            # 1. Тест като нелогнат
            response_anon = client.get('/admin/users')
            self.assertEqual(response_anon.status_code, 403)  # Проверката е за 403

            # 2. Тест като обикновен потребител
            # Логваме потребителя директно, без да минаваме през формата
            login_user(user)
            response_user = client.get('/admin/users')
            self.assertEqual(response_user.status_code, 403)
            # logout_user() # Не е задължително, следващият login ще го презапише

            # 3. Тест като администратор
            login_user(admin_user)
            response_admin = client.get('/admin/users')
            self.assertEqual(response_admin.status_code, 200)  # Очакваме 200
            self.assertIn('Администраторски панел', response_admin.get_data(as_text=True))
            self.assertIn('Списък с потребители', response_admin.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main(verbosity=2)