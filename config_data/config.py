from dataclasses import dataclass
from environs import Env


@dataclass
class DataBase:
    url: str


@dataclass
class TgBot:
    token: str


@dataclass
class Config:
    tg_bot: TgBot
    database: DataBase


def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')), database=DataBase(url=env("DATABASE_URL")))