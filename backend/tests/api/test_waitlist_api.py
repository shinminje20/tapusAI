"""API tests for waitlist endpoints.

REQ-WL-001-005: Waitlist API endpoints
Tests verify HTTP interface, request/response schemas, and error handling.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.v1.deps import get_waitlist_service
from app.domain.entities import EntrySource, WaitlistEntry, WaitlistStatus
from app.domain.exceptions import EntryNotFoundError, InvalidStatusTransitionError
from app.main import app


@pytest.fixture
def mock_service() -> AsyncMock:
    """Create mock WaitlistService."""
    return AsyncMock()


@pytest.fixture
def client(mock_service: AsyncMock) -> TestClient:
    """Create test client with mocked service."""
    app.dependency_overrides[get_waitlist_service] = lambda: mock_service
    yield TestClient(app)
    app.dependency_overrides.clear()


def create_mock_entry(
    entry_id: int = 1,
    guest_id: int = 1,
    party_size: int = 2,
    position: int = 1,
    status: WaitlistStatus = WaitlistStatus.WAITING,
    vip_flag: bool = False,
    source: EntrySource = EntrySource.KIOSK,
) -> MagicMock:
    """Create a mock WaitlistEntry."""
    entry = MagicMock(spec=WaitlistEntry)
    entry.id = entry_id
    entry.guest_id = guest_id
    entry.party_size = party_size
    entry.status = status.value
    entry.position = position
    entry.vip_flag = vip_flag
    entry.source = source.value
    entry.created_at = datetime(2026, 2, 1, 12, 0, 0)
    entry.updated_at = datetime(2026, 2, 1, 12, 0, 0)
    entry.guest = MagicMock()
    entry.guest.name = "John Doe"
    entry.guest.phone_number = "555-1234"
    return entry


class TestAddGuest:
    """Tests for POST /api/v1/waitlist/ endpoint."""

    def test_add_guest_success(
        self, client: TestClient, mock_service: AsyncMock
    ) -> None:
        """AC-WL-001: Entry appears immediately with status 'waiting'."""
        mock_entry = create_mock_entry()
        mock_service.add_guest.return_value = mock_entry
        mock_service.calculate_eta.return_value = 0

        response = client.post(
            "/api/v1/waitlist/",
            json={
                "name": "John Doe",
                "phone_number": "555-1234",
                "party_size": 2,
                "source": "kiosk",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "waiting"
        assert data["party_size"] == 2
        assert data["eta_minutes"] == 0

    def test_add_guest_invalid_party_size(
        self, client: TestClient, mock_service: AsyncMock
    ) -> None:
        """AC-WL-002: party_size must be >= 1."""
        response = client.post(
            "/api/v1/waitlist/",
            json={
                "name": "John Doe",
                "phone_number": "555-1234",
                "party_size": 0,  # Invalid
                "source": "kiosk",
            },
        )

        assert response.status_code == 422

    def test_add_guest_missing_required_fields(self, client: TestClient) -> None:
        """AC-WL-002: All fields required."""
        response = client.post(
            "/api/v1/waitlist/",
            json={"name": "John Doe"},  # Missing phone_number and party_size
        )

        assert response.status_code == 422


class TestGetWaitlist:
    """Tests for GET /api/v1/waitlist/ endpoint."""

    def test_get_waitlist_returns_ordered_entries(
        self, client: TestClient, mock_service: AsyncMock
    ) -> None:
        """REQ-WL-002: Real-time queue display ordered by position."""
        entry1 = create_mock_entry(entry_id=1, position=1)
        entry2 = create_mock_entry(entry_id=2, position=2)
        mock_service.get_all_waiting.return_value = [entry1, entry2]
        mock_service.calculate_eta.side_effect = [0, 15]

        response = client.get("/api/v1/waitlist/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["position"] == 1
        assert data[1]["position"] == 2

    def test_get_waitlist_empty(
        self, client: TestClient, mock_service: AsyncMock
    ) -> None:
        """Should return empty list when no waiting entries."""
        mock_service.get_all_waiting.return_value = []

        response = client.get("/api/v1/waitlist/")

        assert response.status_code == 200
        assert response.json() == []


class TestUpdateStatus:
    """Tests for PATCH /api/v1/waitlist/{entry_id}/status endpoint."""

    def test_update_status_success(
        self, client: TestClient, mock_service: AsyncMock
    ) -> None:
        """AC-WL-003: Valid status transition."""
        mock_entry = create_mock_entry(status=WaitlistStatus.SEATED)
        mock_service.update_status.return_value = mock_entry

        response = client.patch(
            "/api/v1/waitlist/1/status",
            json={"status": "seated"},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "seated"

    def test_update_status_not_found(
        self, client: TestClient, mock_service: AsyncMock
    ) -> None:
        """Should return 404 for non-existent entry."""
        mock_service.update_status.side_effect = EntryNotFoundError(999)

        response = client.patch(
            "/api/v1/waitlist/999/status",
            json={"status": "seated"},
        )

        assert response.status_code == 404

    def test_update_status_invalid_transition(
        self, client: TestClient, mock_service: AsyncMock
    ) -> None:
        """AC-WL-003: Invalid transitions return 422."""
        mock_service.update_status.side_effect = InvalidStatusTransitionError(
            "seated", "waiting"
        )

        response = client.patch(
            "/api/v1/waitlist/1/status",
            json={"status": "waiting"},
        )

        assert response.status_code == 422


class TestReorderEntries:
    """Tests for POST /api/v1/waitlist/reorder endpoint."""

    def test_reorder_entries_success(
        self, client: TestClient, mock_service: AsyncMock
    ) -> None:
        """REQ-WL-004: Ability to reorder."""
        entry1 = create_mock_entry(entry_id=2, position=1)
        entry2 = create_mock_entry(entry_id=1, position=2)
        mock_service.reorder_entries.return_value = [entry1, entry2]
        mock_service.calculate_eta.side_effect = [0, 15]

        response = client.post(
            "/api/v1/waitlist/reorder",
            json={"entry_ids": [2, 1]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data[0]["id"] == 2
        assert data[0]["position"] == 1

    def test_reorder_entries_not_found(
        self, client: TestClient, mock_service: AsyncMock
    ) -> None:
        """Should return 404 if entry doesn't exist."""
        mock_service.reorder_entries.side_effect = EntryNotFoundError(999)

        response = client.post(
            "/api/v1/waitlist/reorder",
            json={"entry_ids": [999]},
        )

        assert response.status_code == 404


class TestToggleVip:
    """Tests for PATCH /api/v1/waitlist/{entry_id}/vip endpoint."""

    def test_toggle_vip_on(
        self, client: TestClient, mock_service: AsyncMock
    ) -> None:
        """AC-WL-006: VIP flagging."""
        mock_entry = create_mock_entry(vip_flag=True)
        mock_service.mark_vip.return_value = mock_entry
        mock_service.calculate_eta.return_value = 0

        response = client.patch("/api/v1/waitlist/1/vip?vip=true")

        assert response.status_code == 200
        assert response.json()["vip_flag"] is True

    def test_toggle_vip_not_found(
        self, client: TestClient, mock_service: AsyncMock
    ) -> None:
        """Should return 404 for non-existent entry."""
        mock_service.mark_vip.side_effect = EntryNotFoundError(999)

        response = client.patch("/api/v1/waitlist/999/vip")

        assert response.status_code == 404


class TestGetEta:
    """Tests for GET /api/v1/waitlist/{entry_id}/eta endpoint."""

    def test_get_eta_success(
        self, client: TestClient, mock_service: AsyncMock
    ) -> None:
        """AC-WL-007: ETA calculation."""
        mock_service.calculate_eta.return_value = 45

        response = client.get("/api/v1/waitlist/1/eta")

        assert response.status_code == 200
        data = response.json()
        assert data["entry_id"] == 1
        assert data["eta_minutes"] == 45

    def test_get_eta_not_found(
        self, client: TestClient, mock_service: AsyncMock
    ) -> None:
        """Should return 404 for non-existent entry."""
        mock_service.calculate_eta.side_effect = EntryNotFoundError(999)

        response = client.get("/api/v1/waitlist/999/eta")

        assert response.status_code == 404
