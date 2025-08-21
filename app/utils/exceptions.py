from fastapi import HTTPException, status


class AuthServiceException(Exception):
    """Base exception for auth service."""
    pass


class AuthenticationError(AuthServiceException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(AuthServiceException):
    """Raised when authorization fails."""
    pass


class UserAlreadyExistsError(AuthServiceException):
    """Raised when trying to create a user that already exists."""
    pass


class UserNotFoundError(AuthServiceException):
    """Raised when user is not found."""
    pass


class InvalidTokenError(AuthServiceException):
    """Raised when token is invalid."""
    pass


class TokenExpiredError(AuthServiceException):
    """Raised when token has expired."""
    pass


# HTTP Exception mappings
def get_http_exception(exc: AuthServiceException) -> HTTPException:
    """Convert auth service exceptions to HTTP exceptions."""
    
    exception_mappings = {
        AuthenticationError: HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        ),
        AuthorizationError: HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        ),
        UserAlreadyExistsError: HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        ),
        UserNotFoundError: HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ),
        InvalidTokenError: HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ),
        TokenExpiredError: HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ),
    }
    
    return exception_mappings.get(
        type(exc),
        HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
    )