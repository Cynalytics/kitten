from tests.mock_clients.mock_luik_client import MockLuikClient


def test_luik_mock_data_1():
    luik_client = MockLuikClient()

    response = luik_client.pop_queue(["ipv4", "ipv6"], ["Network|internet2"])
    print(response)
    assert response
    assert response.task_id == "4387bb56-d362-4cc4-bbde-55c66c9868dd"


def test_luik_mock_data_2():
    luik_client = MockLuikClient()

    response = luik_client.pop_queue(["ipv6"], ["Network|internet2"])
    print(response)
    assert not response
