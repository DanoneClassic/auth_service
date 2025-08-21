from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_user_repository, get_current_active_user
from app.models.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    RefreshTokenRequest,
    MessageResponse
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.utils.exceptions import get_http_exception, AuthServiceException

router = APIRouter(prefix="/auth", tags=["authentication"])


async def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> AuthService:
    """Get authentication service instance."""
    return AuthService(user_repo)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> UserResponse:
    """
    Register a new user.
    
    - **email**: User's email address (must be unique)
    - **username**: User's username (must be unique, 3-50 characters)
    - **password**: User's password (minimum 8 characters)
    """
    try:
        return await auth_service.register_user(user_data)
    except AuthServiceException as e:
        raise get_http_exception(e)


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Token:
    """
    Login user and return JWT tokens.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns access token (15 min) and refresh token (7 days).
    """
    try:
        return await auth_service.login_user(login_data)
    except AuthServiceException as e:
        raise get_http_exception(e)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Token:
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token and refresh token.
    """
    try:
        return await auth_service.refresh_access_token(refresh_data.refresh_token)
    except AuthServiceException as e:
        raise get_http_exception(e)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> UserResponse:
    """
    Get current user's profile information.
    
    Requires valid access token in Authorization header.
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout", response_model=MessageResponse)
async def logout() -> MessageResponse:
    """
    Logout user.
    
    Note: Since JWT tokens are stateless, logout is handled client-side
    by removing the tokens. This endpoint is provided for consistency
    and future token blacklisting implementation.
    """
    return MessageResponse(message="Successfully logged out")