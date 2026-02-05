import sys
import os
from cryptography.fernet import Fernet
# Set KEY before importing app/database modules as they read it at module level
os.environ['KEY'] = Fernet.generate_key().decode()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from app import app

class AuthRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_login_route(self):
        response = self.app.get('/auth/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data.lower()) # Check for some content

    def test_register_route(self):
        response = self.app.get('/auth/register', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'register', response.data.lower()) # Check for some content

    def test_profile_update(self):
        # Register and login first
        unique_login = 'testuser_' + os.urandom(4).hex()
        password = 'password123'
        resp_reg = self.app.post('/auth/register', data=dict(
            login=unique_login,
            password=password,
            confirm_password=password,
            role='student'
        ), follow_redirects=True)
        self.assertEqual(resp_reg.status_code, 200)
        
        resp_login = self.app.post('/auth/login', data=dict(
            login=unique_login,
            password=password
        ), follow_redirects=True)
        # Verify login success by checking for account page content
        profile_text = 'Профиль пользователя'.encode('utf-8')
        if profile_text not in resp_login.data:
            print("Login failed. Response content:", resp_login.data.decode('utf-8', errors='ignore'))
        self.assertIn(profile_text, resp_login.data, "Login failed, not on account page")

        # Update profile
        unique_email = f'test_{os.urandom(4).hex()}@example.com'
        response = self.app.post('/auth/account', data=dict(
            email=unique_email,
            allergen='Peanuts',
            preferences='Vegetarian'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify changes in page content
        self.assertIn(unique_email.encode(), response.data)
        self.assertIn(b'Peanuts', response.data)
        self.assertIn(b'Vegetarian', response.data)

    def test_profile_partial_update(self):
        # Register and login first
        unique_login = 'testuser_partial_' + os.urandom(4).hex()
        password = 'password123'
        self.app.post('/auth/register', data=dict(
            login=unique_login,
            password=password,
            confirm_password=password,
            role='student'
        ), follow_redirects=True)
        
        self.app.post('/auth/login', data=dict(
            login=unique_login,
            password=password
        ), follow_redirects=True)

        # Set initial values
        initial_email = f'initial_{os.urandom(4).hex()}@example.com'
        self.app.post('/auth/account', data=dict(
            email=initial_email,
            allergen='InitialAllergen',
            preferences='InitialPref'
        ), follow_redirects=True)

        # Update ONLY email
        updated_email = f'updated_{os.urandom(4).hex()}@example.com'
        response = self.app.post('/auth/account', data=dict(
            email=updated_email
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify email updated AND others preserved
        self.assertIn(updated_email.encode(), response.data)
        self.assertIn(b'InitialAllergen', response.data)
        self.assertIn(b'InitialPref', response.data)

    def test_account_redirect(self):
        # Should redirect to login if not logged in
        response = self.app.get('/auth/account')
        self.assertEqual(response.status_code, 302)
        self.assertIn(b'/auth/login', response.headers['Location'].encode())

    def test_logout_redirect(self):
        # Should redirect to login if not logged in (login_required intercept)
        response = self.app.get('/auth/logout')
        self.assertEqual(response.status_code, 302)
        # Verify redirect location
        self.assertIn(b'/auth/login', response.headers['Location'].encode())

if __name__ == '__main__':
    unittest.main()
