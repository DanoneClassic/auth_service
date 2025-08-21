import uuid
from datetime import datetime, timezone
from typing import Dict, Any

from jose import JWTError

from app.config import settings
from app.models.schemas import UserCreate, UserLogin, Token, UserResponse
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.security import SecurityUtils
from app.utils.exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidTokenError,
    TokenExpiredError
)


class AuthService:
    """Service layer for authentication operations."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.security = SecurityUtils()
    
    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """Register a new user."""
        # Check if user already exists
        if await self.user_repository.exists_by_email(user_data.email):
            raise UserAlreadyExistsError("User with this email already exists")
        
        if await self.user_repository.exists_by_username(user_data.username):
            raise UserAlreadyExistsError("User with this username already exists")
        
        # Hash password and create user
        hashed_password = self.security.hash_password(user_data.password)
        
        user_dict = {
            "email": user_data.email,
            "username": user_data.username,
            "hashed_password": hashed_password,
            "is_active": True,
        }
        
        user = await self.user_repository.create(user_dict)
        return UserResponse.model_validate(user)
    
    async def authenticate_user(self, login_data: UserLogin) -> User:
        """Authenticate user with email and password."""
        user = await self.user_repository.get_by_email(login_data.email)
        
        if not user:
            raise AuthenticationError("Invalid email or password")
        
        if not user.is_active:
            raise AuthenticationError("User account is inactive")
        
        if not self.security.verify_password(login_data.password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        
        return user
    
    async def login_user(self, login_data: UserLogin) -> Token:
        """Login user and return JWT tokens."""
        user = await self.authenticate_user(login_data)
        
        # Create token data
        token_data = {"sub": str(user.id)}
        
        # Generate tokens
        access_token = self.security.create_access_token(token_data)
        refresh_token = self.security.create_refresh_token(token_data)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
    
    async def refresh_access_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token."""
        try:
            payload = self.security.decode_token(refresh_token)
            
            # Check if it's a refresh token
            if payload.get("type") != "refresh":
                raise InvalidTokenError("Invalid token type")
            
            user_id = payload.get("sub")
            if not user_id:
                raise InvalidTokenError("Invalid token payload")
            
            # Check if user still exists and is active
            user = await self.user_repository.get_by_id(user_id)
            if not user or not user.is_active:
                raise AuthenticationError("User not found or inactive")
            
            # Create new tokens
            token_data = {"sub": str(user.id)}
            new_access_token = self.security.create_access_token(token_data)
            new_refresh_token = self.security.create_refresh_token(token_data)
            
            return Token(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=settings.access_token_expire_minutes * 60
            )
        
        except JWTError as e:
            if "expired" in str(e).lower():
                raise TokenExpiredError("Refresh token has expired")
            raise InvalidTokenError("Invalid refresh token")
    
    async def get_user_profile(self, user_id: str | uuid.UUID) -> UserResponse:
        """Get user profile by ID."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        
        return UserResponse.model_validate(user)
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and return payload."""
        try:
            payload = self.security.decode_token(token)
            
            # Check token type
            if payload.get("type") != "access":
                raise InvalidTokenError("Invalid token type")
            
            # Check expiration (jose already handles this, but we can add custom logic)
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                raise TokenExpiredError("Token has expired")
            
            return payload
        
        except JWTError as e:
            if "expired" in str(e).lower():
                raise TokenExpiredError("Token has expired")
            raise InvalidTokenError("Invalid token")