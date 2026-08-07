from collections import defaultdict

from app.generators.convencional.gerador import geraDataset
from app.generators.convencional.utils import criaMatrizAdjacenciasValorada
from app.schemas import GenerateGraphRequest
from app.services import generate_graphs


def test_conventional_api_matches_original_gera_dataset():
    params = dict(
        graph_type=31,
        number_vertices=30,
        number_edges=55,
        seed=249,
        number_datasets=1,
        number_components=1,
        allocation_factor=0,
    )

    original = geraDataset(
        params["graph_type"],
        params["number_vertices"],
        params["number_edges"],
        params["seed"],
        params["number_datasets"],
        params["number_components"],
        params["allocation_factor"],
    )

    response = generate_graphs(
        GenerateGraphRequest(
            generator="conventional",
            density_preference=0,
            weighted=False,
            min_weight=1,
            max_weight=10,
            **params,
        )
    )

    api_edges = [
        [(edge.source, edge.target) for edge in dataset.edges]
        for dataset in response.datasets
    ]

    assert api_edges == original


def test_weighted_conventional_api_matches_original_random_sequence():
    params = dict(
        graph_type=31,
        number_vertices=20,
        number_edges=30,
        seed=77,
        number_datasets=2,
        number_components=1,
        allocation_factor=0,
    )

    original = geraDataset(
        params["graph_type"],
        params["number_vertices"],
        params["number_edges"],
        params["seed"],
        params["number_datasets"],
        params["number_components"],
        params["allocation_factor"],
    )
    original_matrices = [
        criaMatrizAdjacenciasValorada(
            dataset,
            params["number_vertices"],
            params["graph_type"],
            1,
            10,
        )
        for dataset in original
    ]

    expected = []
    for dataset, matrix in zip(original, original_matrices):
        occurrence = defaultdict(int)
        weighted_edges = []
        for source, target in dataset:
            position = occurrence[(source, target)]
            weighted_edges.append(
                (source, target, int(matrix[source][target][position]))
            )
            occurrence[(source, target)] += 1
        expected.append(weighted_edges)

    response = generate_graphs(
        GenerateGraphRequest(
            generator="conventional",
            density_preference=0,
            weighted=True,
            min_weight=1,
            max_weight=10,
            **params,
        )
    )

    actual = [
        [(edge.source, edge.target, edge.weight) for edge in dataset.edges]
        for dataset in response.datasets
    ]

    assert actual == expected
    assert [dataset.adjacency_matrix for dataset in response.datasets] == original_matrices
