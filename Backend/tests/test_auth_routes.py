import unittest
import json
from unittest.mock import patch, MagicMock
from flask import Flask
from routes.auth import auth_bp, auth_service, user_store

class TestAuthRoutes(unittest.TestCase):
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
        
        self.test_user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "name": "Test User"
        }

    def test_register_success(self):
        """Test successful user registration."""
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        
        self.assertIn('message', data)
        self.assertIn('user', data)
        self.assertIn('token', data)
        self.assertEqual(data['user']['email'], self.test_user_data['email'])
        self.assertEqual(data['user']['name'], self.test_user_data['name'])
        self.assertNotIn('password_hash', data['user'])

    def test_register_missing_email(self):
        """Test registration with missing email."""
        incomplete_data = {
            "password": "testpassword123"
        }
        
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Email and password are required', data['message'])

    def test_register_missing_password(self):
        """Test registration with missing password."""
        incomplete_data = {
            "email": "test@example.com"
        }
        
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Email and password are required', data['message'])

    def test_register_short_password(self):
        """Test registration with password too short."""
        short_password_data = {
            "email": "test@example.com",
            "password": "123"
        }
        
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(short_password_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Password must be at least 6 characters', data['message'])

    def test_register_duplicate_user(self):
        """Test registration with duplicate email."""
        # Register first user
        self.client.post(
            '/api/auth/register',
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )
        
        # Try to register again with same email
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertIn('User already exists', data['message'])

    def test_login_success(self):
        """Test successful login."""
        # First register a user
        self.client.post(
            '/api/auth/register',
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )
        
        # Then try to login
        login_data = {
            "email": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('message', data)
        self.assertIn('user', data)
        self.assertIn('token', data)
        self.assertEqual(data['user']['email'], self.test_user_data['email'])

    def test_login_invalid_email(self):
        """Test login with non-existent email."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('Invalid credentials', data['message'])

    def test_login_invalid_password(self):
        """Test login with wrong password."""
        # Register user first
        self.client.post(
            '/api/auth/register',
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )
        
        # Try login with wrong password
        login_data = {
            "email": self.test_user_data["email"],
            "password": "wrongpassword"
        }
        
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('Invalid credentials', data['message'])

    def test_login_missing_credentials(self):
        """Test login with missing credentials."""
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Email and password are required', data['message'])

    def test_get_current_user_success(self):
        """Test getting current user with valid token."""
        # Register and get token
        register_response = self.client.post(
            '/api/auth/register',
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )
        register_data = json.loads(register_response.data)
        token = register_data['token']
        
        # Get current user
        response = self.client.get(
            '/api/auth/me',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], self.test_user_data['email'])

    def test_get_current_user_no_token(self):
        """Test getting current user without token."""
        response = self.client.get('/api/auth/me')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('Token is missing', data['message'])

    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token."""
        response = self.client.get(
            '/api/auth/me',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('Token is invalid or expired', data['message'])

    def test_verify_token_valid(self):
        """Test token verification with valid token."""
        # Register and get token
        register_response = self.client.post(
            '/api/auth/register',
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )
        register_data = json.loads(register_response.data)
        token = register_data['token']
        
        # Verify token
        response = self.client.post(
            '/api/auth/verify',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['valid'])
        self.assertIn('payload', data)

    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        response = self.client.post(
            '/api/auth/verify',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data['valid'])

    def test_verify_token_missing(self):
        """Test token verification without token."""
        response = self.client.post('/api/auth/verify')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['valid'])

