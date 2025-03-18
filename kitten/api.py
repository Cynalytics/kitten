import multiprocessing
from multiprocessing.context import ForkContext, ForkProcess
from uuid import UUID

import structlog
from fastapi import Depends, FastAPI, Response
from kitten.clients.luik_client import LuikClient, LuikClientInterface
from uvicorn import Config, Server

from kitten.config import settings
from kitten.models.api_models import BoefjeOutput

app = FastAPI(
    title="Kitten API",
    description="API for Kitten service for the docker containers",
    version="0.1.0",
)
logger = structlog.get_logger(__name__)
ctx: ForkContext = multiprocessing.get_context("fork")


def get_luik_client() -> LuikClientInterface:
    return LuikClient(
        base_url=str(settings.luik_api),
        auth_password=settings.auth_password,
    )


class UvicornServer(ForkProcess):
    def __init__(self, config: Config):
        super().__init__()
        self.server = Server(config=config)
        self.config = config

    def stop(self) -> None:
        self.terminate()

    def run(self, *args, **kwargs):
        self.server.run()


def run():
    config = Config(app, host=settings.kitten_host, port=settings.kitten_port)
    instance = UvicornServer(config=config)
    instance.start()
    return instance


@app.get("/health")
async def root():
    return "OK"


@app.get("/boefje_input/{task_id}")
def boefje_input(
    task_id: UUID,
    luik_client: LuikClient = Depends(get_luik_client),
) -> Response:
    logger.info(f"Boefje input called for {task_id}")
    inp = luik_client.boefje_input(str(task_id))
    return Response(status_code=200, content=inp)


@app.post("/boefje_output/{task_id}")
def boefje_output(
    task_id: UUID,
    boefje_output: BoefjeOutput,
    luik_client: LuikClient = Depends(get_luik_client),
) -> Response:
    logger.info(f"Boefje output called for {task_id}")
    luik_client.boefje_output(str(task_id), boefje_output)

    return Response(status_code=200)
