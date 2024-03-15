import datetime

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
    username: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()

    cards = relationship("Card")
    in_categories = relationship("IncomeCategory")
    ex_categories = relationship("ExpenseCategory")


class IncomeCategory(Base):
    __tablename__ = "in_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    incomes = relationship("Income")


class ExpenseCategory(Base):
    __tablename__ = "ex_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    expenses = relationship("Expense")


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
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
