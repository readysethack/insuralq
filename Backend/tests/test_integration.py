import unittest
import json
from flask import Flask
from routes.auth import auth_bp, user_store

class TestAuthIntegration(unittest.TestCase):
    """Integration tests for the complete authentication flow."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = Flask(__name__)
        self.app.register_blueprint(auth_bp)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Clear user store before each test
        user_store.users.clear()
        user_store.users_by_email.clear()
        user_store.next_id = 1

    def test_complete_auth_flow(self):
        """Test complete authentication flow: register -> login -> access protected route."""
        # Step 1: Register
        register_data = {
            "email": "integration@example.com",
            "password": "integrationtest123",
            "name": "Integration Test User"
        }

        register_response = self.client.post(
            '/api/auth/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )

        self.assertEqual(register_response.status_code, 201)
        register_result = json.loads(register_response.data)
        register_token = register_result['token']

        # Step 2: Login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }

        login_response = self.client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )

        self.assertEqual(login_response.status_code, 200)
        login_result = json.loads(login_response.data)
        login_token = login_result['token']

        # Step 3: Access protected route with register token
        me_response1 = self.client.get(
            '/api/auth/me',
            headers={'Authorization': f'Bearer {register_token}'}
        )

        self.assertEqual(me_response1.status_code, 200)
        me_result1 = json.loads(me_response1.data)
        self.assertEqual(me_result1['user']['email'], register_data['email'])

        # Step 4: Access protected route with login token
        me_response2 = self.client.get(
            '/api/auth/me',
            headers={'Authorization': f'Bearer {login_token}'}
        )

        self.assertEqual(me_response2.status_code, 200)
        me_result2 = json.loads(me_response2.data)
        self.assertEqual(me_result2['user']['email'], register_data['email'])

    def test_case_insensitive_email(self):
        """Test that email handling is case insensitive."""
        # Register with lowercase email
        register_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }

        self.client.post(
            '/api/auth/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )

        # Try to login with uppercase email
        login_data = {
            "email": "TEST@EXAMPLE.COM",
            "password": "testpassword123"
        }

        login_response = self.client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )

        self.assertEqual(login_response.status_code, 200)

    def test_multiple_users_isolation(self):
        """Test that multiple users are properly isolated."""
        # Register two users
        user1_data = {
            "email": "user1@example.com",
            "password": "password123",
            "name": "User One"
        }

        user2_data = {
            "email": "user2@example.com",
            "password": "password456",
            "name": "User Two"
        }

        # Register both users
        response1 = self.client.post(
            '/api/auth/register',
            data=json.dumps(user1_data),
            content_type='application/json'
        )

        response2 = self.client.post(
            '/api/auth/register',
            data=json.dumps(user2_data),
            content_type='application/json'
        )

        # Get tokens
        token1 = json.loads(response1.data)['token']
        token2 = json.loads(response2.data)['token']

        # Verify each user gets their own data
        me_response1 = self.client.get(
            '/api/auth/me',
            headers={'Authorization': f'Bearer {token1}'}
        )

        me_response2 = self.client.get(
            '/api/auth/me',
            headers={'Authorization': f'Bearer {token2}'}
        )

        user1_result = json.loads(me_response1.data)['user']
        user2_result = json.loads(me_response2.data)['user']

        # Verify isolation
        self.assertEqual(user1_result['email'], user1_data['email'])
        self.assertEqual(user1_result['name'], user1_data['name'])
        self.assertEqual(user2_result['email'], user2_data['email'])
        self.assertEqual(user2_result['name'], user2_data['name'])
        self.assertNotEqual(user1_result['id'], user2_result['id'])
