import datetime
import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(nullable=True)

    cards = relationship("Card")
    in_categories = relationship("IncomeCategory")
    ex_categories = relationship("ExpenseCategory")
    incomes = relationship("Income")
    expenses = relationship("Expense")


class IncomeCategory(Base):
    __tablename__ = "in_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))

    incomes = relationship("Income")


class ExpenseCategory(Base):
    __tablename__ = "ex_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))

    expenses = relationship("Expense")


class CardType(enum.Enum):
    debit_card = "Дебетовая"
    credit_card = "Кредитная"


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    card_type: Mapped[CardType]
    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    balance: Mapped[float] = mapped_column(nullable=False)

    incomes = relationship("Income")
    expenses = relationship("Expense")


class Income(Base):
    __tablename__ = "incomes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("in_categories.id"))
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))
    amount: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    date: Mapped[datetime.date] = mapped_column(default=datetime.date.today())


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("ex_categories.id"))
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))
    amount: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    date: Mapped[datetime.date] = mapped_column(default=datetime.date.today())

# all_models = [User, IncomeCategory, ExpenseCategory, Card, Income, Expense]
