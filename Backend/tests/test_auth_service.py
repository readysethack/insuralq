import unittest
import jwt
from datetime import datetime, timedelta
from services.auth_service import AuthService, UserStore

class TestAuthService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.auth_service = AuthService(secret_key="test_secret_key")
        self.test_password = "test_password123"
        self.test_user_data = {
            "id": 1,
            "email": "test@example.com"
        }

    def test_hash_password(self):
        """Test password hashing functionality."""
        hashed = self.auth_service.hash_password(self.test_password)
        
        # Hash should be different from original password
        self.assertNotEqual(hashed, self.test_password)
        # Hash should be a string
        self.assertIsInstance(hashed, str)
        # Hash should have reasonable length (bcrypt hashes are typically 60 chars)
        self.assertGreater(len(hashed), 50)

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        hashed = self.auth_service.hash_password(self.test_password)
        is_valid = self.auth_service.verify_password(self.test_password, hashed)
        self.assertTrue(is_valid)

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        hashed = self.auth_service.hash_password(self.test_password)
        is_valid = self.auth_service.verify_password("wrong_password", hashed)
        self.assertFalse(is_valid)

    def test_generate_token(self):
        """Test JWT token generation."""
        token = self.auth_service.generate_token(self.test_user_data)
        
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)
        
        # Decode token to verify contents
        payload = jwt.decode(token, self.auth_service.secret_key, algorithms=[self.auth_service.algorithm])
        self.assertEqual(payload["user_id"], self.test_user_data["id"])
        self.assertEqual(payload["email"], self.test_user_data["email"])
        self.assertIn("exp", payload)
        self.assertIn("iat", payload)

    def test_verify_token_valid(self):
        """Test token verification with valid token."""
        token = self.auth_service.generate_token(self.test_user_data)
        payload = self.auth_service.verify_token(token)
        
        self.assertIsNotNone(payload)
        self.assertEqual(payload["user_id"], self.test_user_data["id"])
        self.assertEqual(payload["email"], self.test_user_data["email"])

    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        invalid_token = "invalid.token.here"
        payload = self.auth_service.verify_token(invalid_token)
        self.assertIsNone(payload)

    def test_verify_token_expired(self):
        """Test token verification with expired token."""
        # Create token with past expiration
        past_time = datetime.utcnow() - timedelta(hours=1)
        payload = {
            "user_id": self.test_user_data["id"],
            "email": self.test_user_data["email"],
            "exp": past_time,
            "iat": past_time - timedelta(minutes=5)
        }
        expired_token = jwt.encode(payload, self.auth_service.secret_key, algorithm=self.auth_service.algorithm)
        
        result = self.auth_service.verify_token(expired_token)
        self.assertIsNone(result)

    def test_extract_token_from_header_valid(self):
        """Test token extraction from valid Authorization header."""
        token = "sample_token_123"
        header = f"Bearer {token}"
        extracted = self.auth_service.extract_token_from_header(header)
        self.assertEqual(extracted, token)

    def test_extract_token_from_header_invalid_scheme(self):
        """Test token extraction with invalid scheme."""
        header = "Basic sample_token_123"
        extracted = self.auth_service.extract_token_from_header(header)
        self.assertIsNone(extracted)

    def test_extract_token_from_header_malformed(self):
        """Test token extraction from malformed header."""
        header = "InvalidHeader"
        extracted = self.auth_service.extract_token_from_header(header)
        self.assertIsNone(extracted)

    def test_extract_token_from_header_empty(self):
        """Test token extraction from empty header."""
        extracted = self.auth_service.extract_token_from_header("")
        self.assertIsNone(extracted)


class TestUserStore(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.user_store = UserStore()
        self.test_email = "test@example.com"
        self.test_password_hash = "hashed_password_123"
        self.test_name = "Test User"

    def test_create_user_success(self):
        """Test successful user creation."""
        user = self.user_store.create_user(
            email=self.test_email,
            password_hash=self.test_password_hash,
            name=self.test_name
        )
        
        self.assertEqual(user["email"], self.test_email)
        self.assertEqual(user["name"], self.test_name)
        self.assertEqual(user["id"], 1)
        self.assertNotIn("password_hash", user)  # Should not return password hash
        self.assertIn("created_at", user)

    def test_create_user_duplicate_email(self):
        """Test user creation with duplicate email."""
        # Create first user
        self.user_store.create_user(
            email=self.test_email,
            password_hash=self.test_password_hash
        )
        
        # Try to create another user with same email
        with self.assertRaises(ValueError) as context:
            self.user_store.create_user(
                email=self.test_email,
                password_hash="another_hash"
            )
        
        self.assertIn("User already exists", str(context.exception))

    def test_get_user_by_email_exists(self):
        """Test getting user by email when user exists."""
        self.user_store.create_user(
            email=self.test_email,
            password_hash=self.test_password_hash,
            name=self.test_name
        )
        
        user = self.user_store.get_user_by_email(self.test_email)
        self.assertIsNotNone(user)
        self.assertEqual(user["email"], self.test_email)
        self.assertEqual(user["password_hash"], self.test_password_hash)

    def test_get_user_by_email_not_exists(self):
        """Test getting user by email when user doesn't exist."""
        user = self.user_store.get_user_by_email("nonexistent@example.com")
        self.assertIsNone(user)

    def test_get_user_by_id_exists(self):
        """Test getting user by ID when user exists."""
        created_user = self.user_store.create_user(
            email=self.test_email,
            password_hash=self.test_password_hash
        )
        
        user = self.user_store.get_user_by_id(created_user["id"])
        self.assertIsNotNone(user)
        self.assertEqual(user["id"], created_user["id"])

    def test_get_user_by_id_not_exists(self):
        """Test getting user by ID when user doesn't exist."""
        user = self.user_store.get_user_by_id(999)
        self.assertIsNone(user)

    def test_multiple_users_different_ids(self):
        """Test that multiple users get different IDs."""
        user1 = self.user_store.create_user(
            email="user1@example.com",
            password_hash="hash1"
        )
        user2 = self.user_store.create_user(
            email="user2@example.com",
            password_hash="hash2"
        )
        
        self.assertNotEqual(user1["id"], user2["id"])
        self.assertEqual(user2["id"], user1["id"] + 1)