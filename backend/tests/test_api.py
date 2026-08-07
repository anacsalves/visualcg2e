from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "online"}


def test_conventional_generation() -> None:
    response = client.post(
        "/api/graphs/generate",
        json={
            "generator": "conventional",
            "graph_type": 0,
            "number_vertices": 10,
            "number_components": 1,
            "density_preference": 0,
            "number_edges": 12,
            "allocation_factor": 0,
            "weighted": False,
            "seed": 42,
            "number_datasets": 1,
        },
    )
    assert response.status_code == 200, response.text
    dataset = response.json()["datasets"][0]
    assert dataset["number_vertices"] == 10
    assert dataset["number_edges"] == 12
    assert len(dataset["edges"]) == 12


def test_powerlaw_generation() -> None:
    response = client.post(
        "/api/graphs/generate",
        json={
            "generator": "powerlaw",
            "graph_type": 0,
            "number_vertices": 20,
            "gamma": 2.5,
            "weighted": True,
            "min_weight": 1,
            "max_weight": 10,
            "seed": 7,
            "number_datasets": 1,
        },
    )
    assert response.status_code == 200, response.text
    dataset = response.json()["datasets"][0]
    assert dataset["number_vertices"] == 20
    assert all(edge["weight"] is not None for edge in dataset["edges"])
