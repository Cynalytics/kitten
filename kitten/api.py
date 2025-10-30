import multiprocessing
from multiprocessing.context import ForkContext, ForkProcess
from typing import Any
from uuid import UUID


import structlog
from fastapi import Body, Depends, FastAPI, Request, Response
from kitten.clients.luik_client import LuikClient, LuikClientInterface
from uvicorn import Config, Server

from kitten.config import settings
from kitten.models.api_models import BoefjeInputResponse, BoefjeOutput, Task, TaskIn, WorkerManager

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
        auth_token=settings.luik_auth_token,
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
    config = Config(app, host=settings.kitten_api.host, port=settings.kitten_api.port)
    instance = UvicornServer(config=config)
    instance.start()
    return instance


@app.get("/health")
async def root():
    return "OK"


@app.get("/boefje_input/{task_id}")
def boefje_input(
    task_id: UUID,
    luik_client: LuikClientInterface = Depends(get_luik_client),
) -> BoefjeInputResponse:
    logger.info(f"Boefje input called for {task_id}")
    inp = luik_client.boefje_input(str(task_id))

    inp.output_url = f"{str(settings.kitten_api).rstrip('/')}/boefje_output/{task_id}"

    return inp


@app.post("/boefje_output/{task_id}")
def boefje_output(
    task_id: UUID,
    boefje_output: BoefjeOutput,
    luik_client: LuikClient = Depends(get_luik_client),
) -> Response:
    logger.info(f"Boefje output called for {task_id}")
    luik_client.boefje_output(str(task_id), boefje_output)

    return Response(status_code=200)

###############################
### Scheduler API endpoints ###
###############################

@app.post("/api/v0/scheduler/boefje/pop", tags=["scheduler"])
async def pop_tasks(
    request: Request,
    limit: int = 1,
    filters: dict[str, Any] = dict(),
    luik_client: LuikClient = Depends(get_luik_client),
) -> dict[str, Any]:
    logger.info("Pop tasks called", body=await request.body(), limit=limit, filters=filters)
    
    # return dict()
    return luik_client.pop_items(filters, limit)


# @app.post("/api/v0/scheduler/{queue_id}/push", tags=["scheduler"])
# def push_item(
#     queue_id: str, p_item: Task, luik_client: LuikClient = Depends(get_luik_client)
# ) -> None:
#     return luik_client.push_item(p_item)


# @app.patch("/api/v0/scheduler/tasks/{task_id}", tags=["scheduler"])
# def patch_task(
#     task_id: UUID, task: TaskIn, luik_client: LuikClient = Depends(get_luik_client)
# ) -> None:
#     return luik_client.patch_task(task_id, task.status)


# @app.get("/api/v0/scheduler/tasks/{task_id}", response_model=Task, tags=["scheduler"])
# def get_task(task_id: UUID, luik_client: LuikClient = Depends(get_luik_client)) -> Task:
#     return get_task_from_scheduler(task_id, luik_client)

