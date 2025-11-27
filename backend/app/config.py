from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


_BASE_DIR = Path(__file__).resolve().parent.parent


def _default_db_path() -> str:
    return f"sqlite:///{_BASE_DIR / 'instalily.db'}"


def _default_data_dir() -> Path:
    return _BASE_DIR / "data"


def _default_chroma_dir() -> Path:
    return _BASE_DIR / "chroma_db"


class Settings(BaseSettings):
    """Centralized configuration with optional overrides via environment vars."""

    database_url: str = Field(default_factory=_default_db_path)
    data_dir: Path = Field(default_factory=_default_data_dir)
    chroma_dir: Path = Field(default_factory=_default_chroma_dir)
    chroma_collection: str = "documents"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="INSTALILY_")


settings = Settings()
