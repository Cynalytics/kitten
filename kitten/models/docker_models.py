from pydantic import BaseModel, Field


class DockerRunResponse(BaseModel):
    id: str = Field("")
    image: str = Field("")
