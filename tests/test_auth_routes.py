
import sys
import os
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
