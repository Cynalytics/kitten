from kitten.app import KittenDockerRunner
from kitten.clients.docker_client import NoOciImageException
from tests.mock_clients.mock_docker_client import MockDockerClient
from tests.mock_clients.mock_luik_client import MockLuikClient
import pytest


def test_kitten_1():
    mocked_kitten_runner = KittenDockerRunner(
        MockLuikClient(),
        MockDockerClient(),
        ["ipv4"],
        ["Network|internet2"],
        1,
        "http://luik_api:2580",
    )
    with pytest.raises(NoOciImageException):
        _ = mocked_kitten_runner.update()

    result1 = mocked_kitten_runner.update()
    assert result1
    assert (
        result1.id == "719c5bcbdbd20ab0e768418ec5a78040fd90c2e636dab8cfba17c27587aa162e"
    )

    result2 = mocked_kitten_runner.update()
    assert result2 is None

    result3 = mocked_kitten_runner.update()
    assert result3 is None


def test_kitten_all_jobs():
    mocked_kitten_runner = KittenDockerRunner(
        MockLuikClient(),
        MockDockerClient(),
        ["ipv4", "ipv6"],
        ["Network|internet", "Network|internet2"],
        1,
        "http://luik_api:2580",
    )
    result1 = mocked_kitten_runner.update()
    assert result1

    result2 = mocked_kitten_runner.update()
    assert result2

    with pytest.raises(NoOciImageException):
        _ = mocked_kitten_runner.update()

    result3 = mocked_kitten_runner.update()
    assert result3


def test_kitten_no_jobs():
    mocked_kitten_runner = KittenDockerRunner(
        MockLuikClient(),
        MockDockerClient(),
        ["ipv4", "ipv6"],
        ["Network|dentist"],
        1,
        "http://luik_api:2580",
    )

    result = mocked_kitten_runner.update()
    assert not result

    result2 = mocked_kitten_runner.update()
    assert not result2
