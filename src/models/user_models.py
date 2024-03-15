from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column()
    email = Mapped[str] = mapped_column()

    cards = relationship("Card")
    in_categories = relationship("IncomeCategory")
    ex_categories = relationship("ExpenseCategory")
