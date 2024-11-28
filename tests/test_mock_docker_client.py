from kitten.clients.docker_client import NoOciImageException
from tests.mock_clients.mock_docker_client import MockDockerClient

import pytest


def test_docker_mock_data():
    docker_client = MockDockerClient()

    response = docker_client.run_boefje("image_name", "https://cynalytics.nl")
    assert response
    assert response.image == "image_name"


def test_docker_client_no_image():
    docker_client = MockDockerClient()

    with pytest.raises(NoOciImageException):
        _ = docker_client.run_boefje("", "https://cynalytics.nl")
