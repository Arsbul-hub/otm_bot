from pydantic import BaseModel
from pydantic_settings import BaseSettings, DotEnvSettingsSource


class Config(BaseSettings):
    BOT_TOKEN: str
    PG_USER: str
    PG_PASSWORD: str
    PG_DB_NAME: str
    CODE_EXPIRES_HOURS: int
    DEFAULT_ADMIN_USER_ID: int
    MARKER_EXPIRES_DAYS: int
    MAX_WRONG_ATTEMPT_COUNT: int
    COOLDOWN_WRONG_ATTEMPT_SECONDS: int
    CODE_LENGTH: int

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"postgresql://{self.PG_USER}:{self.PG_PASSWORD}@localhost:5432/{self.PG_DB_NAME}"

    @classmethod
    def settings_customise_sources(cls, settings_cls, **kwargs):
        return (DotEnvSettingsSource(settings_cls, "./.env"),)
config = Config()