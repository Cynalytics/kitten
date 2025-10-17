from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class LuikPopResponse(BaseModel):
    oci_image: str
    task_id: str


class Boefje(BaseModel):
    id: str
    version: Any = None


class ScanProfile(BaseModel):
    scan_profile_type: str
    reference: str
    level: int
    user_id: int


class Input(BaseModel):
    object_type: str
    scan_profile: ScanProfile
    user_id: int
    primary_key: str
    network: str
    address: str
    netblock: Any = None


class Arguments(BaseModel):
    oci_arguments: list[str]
    input: dict[str, Any]


class BoefjeMeta(BaseModel):
    id: str
    started_at: Any = None
    ended_at: Any = None
    boefje: Boefje
    input_ooi: str
    arguments: Arguments
    organization: str
    runnable_hash: Any = None
    environment: dict[str, Any]


class BoefjeInputResponse(BaseModel):
    output_url: str
    task: dict


class LuikPopRequest(BaseModel):
    task_capabilities: list[str]
    reachable_networks: list[str]


class StatusEnum(str, Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class File(BaseModel):
    name: str | None = None
    content: str = Field(json_schema_extra={"contentEncoding": "base64"})
    tags: list[str] | None = None


class BoefjeOutput(BaseModel):
    status: StatusEnum
    files: list[File] | None = None
