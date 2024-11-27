from pathlib import Path

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).parent.resolve()


class Settings(BaseSettings):
    worker_heartbeat: int = Field(3, description="Seconds to wait between queue pops")

    queue: str = Field()

    luik_api: AnyHttpUrl = Field(
        ...,
        examples=["http://localhost:8019", "https://cynalytics.nl"],
        description="The URL on which the boefjes API is available",
    )

    boefje_reachable_networks: list[str] = Field(
        ...,
        description="List of networks the boefje-runner can reach",
        examples=[["Network|internet", "Network|dentist"], []],
    )

    boefje_task_capabilities: list[str] = Field(
        ...,
        description="List of technical requirements the boefje-runner is capable of running",
        examples=[[], ["ipv4", "wifi-pineapple"]],
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()  # type: ignore
