from typing import Any

from pydantic import BaseModel


class LuikPopResponse(BaseModel):
    oci_image: str
    task_id: str


class File(BaseModel):
    name: str | None = None
    content: str
    tags: list[str]


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


class LuikBoefjeInputResponse(BaseModel):
    task_id: str
    output_url: str
    boefje_meta: BoefjeMeta
