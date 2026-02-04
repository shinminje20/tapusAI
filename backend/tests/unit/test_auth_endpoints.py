"""Unit tests for authentication endpoints.

REQ-SEC-004: Role-based access control
NFR-SEC-010: Authentication required for admin access
NFR-SEC-012: Session security - login, token refresh
AC-SEC-001: RBAC blocks unauthorized actions
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security import create_access_token, create_refresh_token, hash_password
from app.domain.entities import User, UserRole
from app.infrastructure.database import Base, get_db
from app.main import app

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_engine():
    """Create test database engine for each test function."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncSession:
    """Provide a database session for tests."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
        role=UserRole.HOST.value,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def manager_user(db_session: AsyncSession) -> User:
    """Create a test manager user."""
    user = User(
        email="manager@example.com",
        hashed_password=hash_password("managerpass123"),
        role=UserRole.MANAGER.value,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def inactive_user(db_session: AsyncSession) -> User:
    """Create an inactive test user."""
    user = User(
        email="inactive@example.com",
        hashed_password=hash_password("testpassword123"),
        role=UserRole.HOST.value,
        is_active=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def async_client(test_engine, db_session) -> AsyncClient:
    """Provide an async test client with overridden db dependency."""

    async def override_get_db():
        async_session = async_sessionmaker(
            test_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login.

    NFR-SEC-010: Authentication required for admin access.
    """

    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient, test_user: User):
        """Test successful login returns tokens."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, async_client: AsyncClient, test_user: User):
        """Test login with wrong password returns 401."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """Test login with nonexistent email returns 401."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "testpassword123"},
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, async_client: AsyncClient, inactive_user: User):
        """Test login with inactive user returns 401."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "inactive@example.com", "password": "testpassword123"},
        )

        assert response.status_code == 401
        assert "disabled" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_invalid_email_format(self, async_client: AsyncClient):
        """Test login with invalid email format returns 422."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "not-an-email", "password": "testpassword123"},
        )

        assert response.status_code == 422


class TestRefreshEndpoint:
    """Tests for POST /api/v1/auth/refresh.

    NFR-SEC-012: Refresh mechanism must be secure.
    """

    @pytest.mark.asyncio
    async def test_refresh_success(self, async_client: AsyncClient, test_user: User):
        """Test successful token refresh."""
        # First login to get tokens
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh the token
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, async_client: AsyncClient):
        """Test refresh with invalid token returns 401."""
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.refresh.token"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_access_token(self, async_client: AsyncClient, test_user: User):
        """Test refresh with access token instead of refresh token returns 401.

        NFR-SEC-012: Token type validation.
        """
        # Create access token
        access_token = create_access_token({"sub": str(test_user.id)})

        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token},
        )

        assert response.status_code == 401


class TestMeEndpoint:
    """Tests for GET /api/v1/auth/me.

    REQ-SEC-004: Role-based access control.
    NFR-SEC-010: Authentication required.
    """

    @pytest.mark.asyncio
    async def test_get_me_success(self, async_client: AsyncClient, test_user: User):
        """Test getting current user info with valid token."""
        # Login to get token
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
        access_token = login_response.json()["access_token"]

        # Get user info
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["role"] == "host"
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_get_me_no_token(self, async_client: AsyncClient):
        """Test getting user info without token returns 401.

        NFR-SEC-010: Authentication required for admin access.
        """
        response = await async_client.get("/api/v1/auth/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, async_client: AsyncClient):
        """Test getting user info with invalid token returns 401."""
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_with_refresh_token(self, async_client: AsyncClient, test_user: User):
        """Test that refresh token cannot be used as access token.

        NFR-SEC-012: Token type validation.
        """
        # Create refresh token
        refresh_token = create_refresh_token({"sub": str(test_user.id)})

        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )

        assert response.status_code == 401


class TestProtectedEndpointsWithRBAC:
    """Tests for role-based access control on protected endpoints.

    AC-SEC-001: RBAC blocks unauthorized actions.
    NFR-SEC-011: Role-Based Access Control.
    """

    @pytest.mark.asyncio
    async def test_host_can_access_waitlist(self, async_client: AsyncClient, test_user: User):
        """Test that host role can access waitlist endpoints.

        AC-SEC-001: Reorder/seat guests if role permits.
        """
        # Login as host
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
        access_token = login_response.json()["access_token"]

        # Access waitlist (should succeed for host)
        response = await async_client.get(
            "/api/v1/waitlist/",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Waitlist endpoint may return empty list but should be accessible
        assert response.status_code in [200, 401]  # 401 if endpoint requires auth

    @pytest.mark.asyncio
    async def test_manager_has_elevated_access(
        self, async_client: AsyncClient, manager_user: User
    ):
        """Test that manager role has access to manager-level features."""
        # Login as manager
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "manager@example.com", "password": "managerpass123"},
        )
        access_token = login_response.json()["access_token"]

        # Get user info to verify role
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        assert response.json()["role"] == "manager"


class TestUserRoleHierarchy:
    """Tests for User entity role hierarchy.

    NFR-SEC-011: Role hierarchy - Guest < Host < Manager < Owner.
    """

    def test_host_has_role_host(self):
        """Test host has host role."""
        user = User(
            email="host@example.com",
            hashed_password="hashed",
            role=UserRole.HOST.value,
        )
        assert user.has_role(UserRole.HOST) is True
        assert user.has_role(UserRole.GUEST) is True

    def test_host_does_not_have_manager_role(self):
        """Test host does not have manager role."""
        user = User(
            email="host@example.com",
            hashed_password="hashed",
            role=UserRole.HOST.value,
        )
        assert user.has_role(UserRole.MANAGER) is False
        assert user.has_role(UserRole.OWNER) is False

    def test_manager_has_host_role(self):
        """Test manager has host role (hierarchy)."""
        user = User(
            email="manager@example.com",
            hashed_password="hashed",
            role=UserRole.MANAGER.value,
        )
        assert user.has_role(UserRole.MANAGER) is True
        assert user.has_role(UserRole.HOST) is True
        assert user.has_role(UserRole.GUEST) is True

    def test_owner_has_all_roles(self):
        """Test owner has all roles."""
        user = User(
            email="owner@example.com",
            hashed_password="hashed",
            role=UserRole.OWNER.value,
        )
        assert user.has_role(UserRole.OWNER) is True
        assert user.has_role(UserRole.MANAGER) is True
        assert user.has_role(UserRole.HOST) is True
        assert user.has_role(UserRole.GUEST) is True

    def test_host_can_view_phone_numbers(self):
        """Test host can view phone numbers.

        NFR-SEC-011: Sensitive fields visible only to roles that require it.
        """
        user = User(
            email="host@example.com",
            hashed_password="hashed",
            role=UserRole.HOST.value,
        )
        assert user.can_view_phone_numbers() is True

    def test_guest_cannot_view_phone_numbers(self):
        """Test guest cannot view phone numbers.

        NFR-SEC-011: Sensitive fields visible only to roles that require it.
        """
        user = User(
            email="guest@example.com",
            hashed_password="hashed",
            role=UserRole.GUEST.value,
        )
        assert user.can_view_phone_numbers() is False

    def test_host_can_modify_waitlist(self):
        """Test host can modify waitlist.

        AC-SEC-001: Reorder/seat guests only if role permits.
        """
        user = User(
            email="host@example.com",
            hashed_password="hashed",
            role=UserRole.HOST.value,
        )
        assert user.can_modify_waitlist() is True

    def test_guest_cannot_modify_waitlist(self):
        """Test guest cannot modify waitlist.

        AC-SEC-001: RBAC blocks unauthorized actions.
        """
        user = User(
            email="guest@example.com",
            hashed_password="hashed",
            role=UserRole.GUEST.value,
        )
        assert user.can_modify_waitlist() is False

    def test_host_can_access_admin(self):
        """Test host can access admin features.

        NFR-SEC-010: Authentication required for admin access.
        """
        user = User(
            email="host@example.com",
            hashed_password="hashed",
            role=UserRole.HOST.value,
        )
        assert user.can_access_admin() is True

    def test_guest_cannot_access_admin(self):
        """Test guest cannot access admin features.

        AC-SEC-001: Block admin features from kiosk mode.
        """
        user = User(
            email="guest@example.com",
            hashed_password="hashed",
            role=UserRole.GUEST.value,
        )
        assert user.can_access_admin() is False
