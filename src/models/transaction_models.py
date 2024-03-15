from sqlalchemy import ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class IncomeCategory(Base):
    __tablename__ = "in_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    user_id = Mapped[int] = mapped_column(ForeignKey("users.id"))

    incomes = relationship("Income")


class ExpenseCategory(Base):
    __tablename__ = "ex_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    user_id = Mapped[int] = mapped_column(ForeignKey("users.id"))


class Income(Base):
    __tablename__ = "incomes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("in_categories.id"))
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))
    amount: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column()
    date: Mapped[Date] = mapped_column(nullable=False)


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("ex_categories.id"))
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))
    amount: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column()
    date: Mapped[Date] = mapped_column(nullable=False)
