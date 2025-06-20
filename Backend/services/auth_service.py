import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets

class AuthService:
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = "HS256"
        self.token_expiry_hours = 24
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def generate_token(self, user_data: Dict[str, Any]) -> str:
        """Generate a JWT token for authenticated user"""
        payload = {
            "user_id": user_data.get("id"),
            "email": user_data.get("email"),
            "exp": datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def extract_token_from_header(self, authorization_header: str) -> Optional[str]:
        """Extract token from Authorization header"""
        if not authorization_header:
            return None
        
        try:
            scheme, token = authorization_header.split()
            if scheme.lower() != 'bearer':
                return None
            return token
        except ValueError:
            return None

# Simple in-memory user store (replace with database in production)
class UserStore:
    def __init__(self):
        self.users = {}
        self.users_by_email = {}
        self.next_id = 1
    
    def create_user(self, email: str, password_hash: str, **kwargs) -> Dict[str, Any]:
        """Create a new user"""
        if email in self.users_by_email:
            raise ValueError("User already exists")
        
        user = {
            "id": self.next_id,
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        self.users[self.next_id] = user
        self.users_by_email[email] = user
        self.next_id += 1
        
        # Return user without password hash
        user_response = user.copy()
        del user_response["password_hash"]
        return user_response
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        return self.users_by_email.get(email)
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self.users.get(user_id)

# Initialize services
auth_service = AuthService()
user_store = UserStore()

""