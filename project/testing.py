import unittest
from flask_login import current_user
from werkzeug.security import generate_password_hash
from .models import User
from . import create_app, db


class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_profile_route_requires_login(self):
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers.get('Location'))

    def test_login(self):
        user = User(email='test@example.com', name='Test User', password=generate_password_hash('password'))
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/login', data={'email': 'test@example.com', 'password': 'password'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/profile', response.headers.get('Location'))

    def test_signup(self):
        response = self.client.post('/signup', data={'email': 'test@example.com', 'name': 'Test User', 'password': 'password'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers.get('Location'))
        user = User.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.name, 'Test User')
        self.assertTrue(user.password, 'password')

    def test_logout(self):
        user = User(email='test@example.com', name='Test User', password=generate_password_hash('password'))
        db.session.add(user)
        db.session.commit()

        with self.client:
            self.client.post('/login', data={'email': 'test@example.com', 'password': 'password'})
            response = self.client.get('/logout')
            self.assertEqual(response.status_code, 302)
            self.assertIn('/', response.headers.get('Location'))
            self.assertFalse(current_user.is_authenticated)


if __name__ == '__main__':
    unittest.main()
