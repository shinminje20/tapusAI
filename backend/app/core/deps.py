"""Core dependencies for authentication and authorization.

REQ-SEC-004: Role-based access control
NFR-SEC-010: Authentication required for admin access
NFR-SEC-011: Role-Based Access Control (RBAC)
AC-SEC-001: RBAC blocks unauthorized actions
"""

from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.domain.entities.user import User, UserRole
from app.infrastructure.database import get_db
from app.infrastructure.repositories.user_repository import UserRepository

# Bearer token security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get the current authenticated user from JWT token.

    NFR-SEC-010: Authentication required for admin access.
    NFR-SEC-012: Validate token expiry and validity.

    Args:
        credentials: Bearer token credentials from Authorization header.
        db: Database session.

    Returns:
        Authenticated User entity.

    Raises:
        HTTPException: 401 if no token, invalid token, or user not found.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = verify_token(token, token_type="access")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

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

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get the current active user.

    Args:
        current_user: User from get_current_user dependency.

    Returns:
        Active User entity.

    Raises:
        HTTPException: 401 if user is not active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )
    return current_user


def require_role(required_role: UserRole) -> Callable:
    """Create a dependency that requires a specific role level.

    AC-SEC-001: RBAC blocks unauthorized actions.
    NFR-SEC-011: Role-Based Access Control enforcement.

    Args:
        required_role: Minimum role level required.

    Returns:
        Dependency function that validates user role.
    """

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        """Check if user has the required role.

        Args:
            current_user: Authenticated user.

        Returns:
            User if authorized.

        Raises:
            HTTPException: 403 if insufficient role.
        """
        if not current_user.has_role(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role.value}",
            )
        return current_user

    return role_checker


# Pre-built role dependencies for common use cases
require_host = require_role(UserRole.HOST)
require_manager = require_role(UserRole.MANAGER)
require_owner = require_role(UserRole.OWNER)

# Type aliases for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
HostUser = Annotated[User, Depends(require_host)]
ManagerUser = Annotated[User, Depends(require_manager)]
OwnerUser = Annotated[User, Depends(require_owner)]
