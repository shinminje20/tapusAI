"""Authentication API endpoints.

REQ-SEC-004: Role-based access control
NFR-SEC-010: Authentication required for admin access
NFR-SEC-012: Session security - login, token refresh, logout
AC-SEC-001: RBAC blocks unauthorized actions
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)
from app.core.deps import CurrentUser
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_token,
)
from app.infrastructure.database import get_db
from app.infrastructure.repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
    description="NFR-SEC-010: Authenticate user and return JWT tokens.",
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate user with email and password.

    NFR-SEC-010: Authentication required for admin access.
    NFR-SEC-012: Session security - token creation.

    Args:
        login_data: Email and password credentials.
        db: Database session.

    Returns:
        TokenResponse with access and refresh tokens.

    Raises:
        HTTPException: 401 if credentials are invalid.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(login_data.email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens with user info in payload
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "restaurant_id": user.restaurant_id,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="NFR-SEC-012: Secure token refresh mechanism.",
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh access token using refresh token.

    NFR-SEC-012: Refresh mechanism must be secure.

    Args:
        refresh_data: Refresh token.
        db: Database session.

    Returns:
        TokenResponse with new access and refresh tokens.

    Raises:
        HTTPException: 401 if refresh token is invalid or expired.
    """
    payload = verify_token(refresh_data.refresh_token, token_type="refresh")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user still exists and is active
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "restaurant_id": user.restaurant_id,
    }

    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user info",
    description="REQ-SEC-004: Return authenticated user information.",
)
async def get_current_user_info(
    current_user: CurrentUser,
) -> UserResponse:
    """Get current authenticated user information.

    REQ-SEC-004: Role-based access control - user info exposure.
    NFR-SEC-010: Requires authentication.

    Args:
        current_user: Authenticated user from JWT token.

    Returns:
        UserResponse with user information.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        restaurant_id=current_user.restaurant_id,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )
