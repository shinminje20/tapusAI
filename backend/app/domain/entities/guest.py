"""Guest entity model.

REQ-WL-001: Add guests quickly (name, party size, phone number)
AC-WL-002: All fields required - name, phone_number, party_size
"""

from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class Guest(Base):
    """Guest entity representing a customer.

    AC-WL-002: Validate Input for Guest Add
    - name is REQUIRED
    - phone_number is REQUIRED and valid format
    """

    __tablename__ = "guests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    waitlist_entries: Mapped[list["WaitlistEntry"]] = relationship(
        "WaitlistEntry", back_populates="guest"
    )

    def __repr__(self) -> str:
        return f"<Guest(id={self.id}, name='{self.name}')>"
