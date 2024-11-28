from typing import Any
import json

from kitten.clients.luik_client import LuikClientInterface
from kitten.models.api_models import LuikPopResponse


def mock_tasks() -> list[dict[str, Any]]:
    with open("./tests/mock_data/mock_luik_queue.json") as f:
        data = f.read()
    return json.loads(data)


class MockLuikClient(LuikClientInterface):
    def __init__(self):
        self.tasks = mock_tasks()

    def pop_queue(
        self, task_capabilities: list[str], reachable_networks: list[str]
    ) -> LuikPopResponse | None:
        for i, task in enumerate(self.tasks):
            if (
                set(task["requirements"]).issubset(task_capabilities)
                and task["network"] in reachable_networks
            ):
                return LuikPopResponse.model_validate(self.tasks.pop(i))
        return None
