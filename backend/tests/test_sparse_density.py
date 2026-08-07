from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_sparse_limits_with_unspecified_components() -> None:
    response = client.post(
        "/api/graphs/limits",
        json={
            "graph_type": 0,
            "number_vertices": 10,
            "number_components": 0,
            "density_preference": 1,
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["minimum"] == 0
    assert response.json()["maximum"] == 9


def test_generate_sparse_simple_graph() -> None:
    response = client.post(
        "/api/graphs/generate",
        json={
            "generator": "conventional",
            "graph_type": 0,
            "number_vertices": 10,
            "number_components": 0,
            "density_preference": 1,
            "number_edges": 9,
            "allocation_factor": 0,
            "weighted": False,
            "seed": 42,
            "number_datasets": 1,
        },
    )
    assert response.status_code == 200, response.text
    dataset = response.json()["datasets"][0]
    assert dataset["number_edges"] == 9
    assert dataset["density"] == 0.2
