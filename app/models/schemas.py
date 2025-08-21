import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    username: str = Field(min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(
        min_length=8,
        max_length=100,
        description="Password must be at least 8 characters long"
    )


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response (without sensitive data)."""
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Schema for token payload data."""
    sub: str
    exp: int
    iat: int
    type: str = "access"


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    timestamp: datetime
    service: str