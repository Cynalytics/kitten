from pydantic import BaseModel


class DockerRunResponse(BaseModel):
    id: str
    image: str
