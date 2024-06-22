from dataclasses import dataclass
from environs import Env


@dataclass
class DataBase:
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@dataclass
class TgBot:
    token: str
    redis_host: str


@dataclass
class Config:
    tg_bot: TgBot
    database: DataBase


def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'), redis_host=env("REDIS_HOST")),
                  database=DataBase(DB_HOST=env("DB_HOST"), DB_PORT=env("DB_PORT"), DB_USER=env("DB_USER"),
                                    DB_PASS=env("DB_PASS"), DB_NAME=env("DB_NAME")))
