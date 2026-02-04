"""User entity model for authentication and RBAC.

REQ-SEC-004: Role-based access control
NFR-SEC-011: Roles at minimum - Guest, Host, Manager, Owner
AC-SEC-001: RBAC blocks unauthorized actions
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class UserRole(str, Enum):
    """User roles for RBAC.

    NFR-SEC-011: Role-Based Access Control
    - Guest: limited to own guest link view
    - Host: waitlist operations
    - Manager: configuration + overrides
    - Owner: reports/admin-level controls
    """

    GUEST = "guest"
    HOST = "host"
    MANAGER = "manager"
    OWNER = "owner"


class User(Base):
    """User entity for authentication and authorization.

    REQ-SEC-004: Role-based access control
    NFR-SEC-010: Authentication required for admin access
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default=UserRole.HOST.value)
    # Note: Foreign key to restaurants table will be added when restaurants entity is created
    restaurant_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

    @property
    def role_enum(self) -> UserRole:
        """Get role as UserRole enum."""
        return UserRole(self.role)

    def has_role(self, required_role: UserRole) -> bool:
        """Check if user has at least the required role level.

        Role hierarchy: guest < host < manager < owner

        AC-SEC-001: RBAC blocks unauthorized actions
        """
        role_hierarchy = {
            UserRole.GUEST: 0,
            UserRole.HOST: 1,
            UserRole.MANAGER: 2,
            UserRole.OWNER: 3,
        }
        user_level = role_hierarchy.get(self.role_enum, 0)
        required_level = role_hierarchy.get(required_role, 0)
        return user_level >= required_level

    def can_view_phone_numbers(self) -> bool:
        """Check if user can view sensitive phone number data.

        NFR-SEC-011: Sensitive fields visible only to roles that require it.
        """
        # Host, Manager, Owner can view phone numbers for operations
        return self.has_role(UserRole.HOST)

    def can_modify_waitlist(self) -> bool:
        """Check if user can reorder or modify waitlist.

        AC-SEC-001: Reorder/seat guests only if role permits.
        """
        return self.has_role(UserRole.HOST)

    def can_access_admin(self) -> bool:
        """Check if user can access admin features.

        NFR-SEC-010: Admin features require authenticated access.
        AC-SEC-001: Block admin features from kiosk mode.
        """
        return self.has_role(UserRole.HOST)
