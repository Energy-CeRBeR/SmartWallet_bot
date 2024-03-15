from sqlalchemy import ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class CardType(Base):
    __tablename__ = "card_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)

    cards = relationship("Card")


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("card_types.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    balanse: Mapped[float] = mapped_column(nullable=False)
