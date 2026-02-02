"""Table entity model.

For future use - tracking restaurant tables.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class Table(Base):
    """Restaurant table entity.

    For future use in seating assignment and capacity planning.
    """

    __tablename__ = "tables"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(String(20), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=4)

    def __init__(self, number: str, capacity: int = 4, **kwargs) -> None:
        super().__init__(number=number, capacity=capacity, **kwargs)

    def __repr__(self) -> str:
        return f"<Table(id={self.id}, number='{self.number}', capacity={self.capacity})>"
