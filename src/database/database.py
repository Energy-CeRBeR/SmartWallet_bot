import datetime
import enum

from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from config_data.config import Config, load_config

config: Config = load_config(".env")
DATABASE_URL = config.database.url

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(nullable=True)

    cards = relationship("Card")
    in_categories = relationship("IncomeCategory")
    ex_categories = relationship("ExpenseCategory")


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
    debit_card = "debit_card"
    credit_card = "credit_card"


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    card_type: Mapped[CardType] = mapped_column()
    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    balance: Mapped[float] = mapped_column(nullable=False)


class Income(Base):
    __tablename__ = "incomes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("in_categories.id"))
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))
    amount: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column()
    date: Mapped[datetime.date] = mapped_column(nullable=False)


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("ex_categories.id"))
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))
    amount: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column()
    date: Mapped[datetime.date] = mapped_column(nullable=False)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
