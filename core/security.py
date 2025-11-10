"""
Security utilities for API authentication.
Provides Bearer token authentication compatible with Swagger UI and Postman.
"""
from fastapi import HTTPException, status, Depends, Query, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from typing import Optional, Annotated

# Create HTTPBearer security scheme
# This will be automatically recognized by FastAPI's OpenAPI generation
security = HTTPBearer(
    auto_error=False,
    scheme_name="Bearer",
    description="Bearer token authentication. Enter your token without 'Bearer' prefix."
)

# Create API Key header for user_id
# This will appear in Swagger UI's Authorize dialog
# Using scheme_name to control how it appears in Swagger UI
user_id_header = APIKeyHeader(
    name="X-User-Id",
    auto_error=False,
    scheme_name="UserId",
    description="User ID for authentication. Enter your user ID (integer)."
)


async def get_bearer_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Extract Bearer token from Authorization header.
    Compatible with Swagger UI authorization and Postman.
    
    This function works exactly like OAuth2PasswordBearer but uses HTTPBearer
    which is properly supported by Swagger UI.
    
    Args:
        credentials: HTTPAuthorizationCredentials from HTTPBearer dependency
        
    Returns:
        str: Bearer token
        
    Raises:
        HTTPException: If token is missing
        
    Usage:
        ```python
        from core.security import get_bearer_token
        
        @router.post("/endpoint")
        async def endpoint(
            token: Annotated[str, Depends(get_bearer_token)],
            ...
        ):
            # Use token here
        ```
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


async def get_user_id(
    request: Request,
    user_id_header_value: Optional[str] = Depends(user_id_header)
) -> int:
    """
    Extract user_id from header (X-User-Id) or query parameter.
    Header takes precedence. This allows user_id to be set in Swagger UI's Authorize dialog.
    
    Args:
        request: FastAPI Request object to read query parameters
        user_id_header_value: User ID from X-User-Id header (preferred, from APIKeyHeader)
        
    Returns:
        int: User ID
        
    Raises:
        HTTPException: If user_id is missing from both header and query
        
    Usage:
        ```python
        from core.security import get_user_id
        
        @router.post("/endpoint")
        async def endpoint(
            user_id: Annotated[int, Depends(get_user_id)],
            ...
        ):
            # Use user_id here
        ```
    """
    # Try header first (from Swagger UI Authorize dialog via APIKeyHeader)
    if user_id_header_value:
        try:
            return int(user_id_header_value)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id in X-User-Id header. Must be an integer."
            )
    
    # Fallback to query parameter (for backward compatibility with Postman/other clients)
    user_id_query = request.query_params.get("user_id")
    if user_id_query:
        try:
            return int(user_id_query)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id in query parameter. Must be an integer."
            )
    
    # Neither provided
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="user_id is required. Provide it via X-User-Id header or user_id query parameter."
    )


def verify_user(user_id: int, token: str, db) -> bool:
    """
    Verify if the user exists and the token is valid.

    Args:
        user_id (int): The ID of the user to verify.
        token (str): The token to verify.
        db: The database session.

    Returns:
        bool: True if the user exists and the token is valid, False otherwise.
    """
    from database.db_users import User
    
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        return False

    if user.token != token:
        return False

    return True

