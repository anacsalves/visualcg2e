from __future__ import annotations

import math
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

import networkx as nx

from .generators.convencional.constants import (
    GERACAO,
    TIPOS_DIRIGIDOS,
    TIPOS_GRAFOS,
)
from .generators.convencional.gerador import geraDataset, verificaAresta
from .generators.convencional.utils import (
    criaMatrizAdjacencias,
    criaMatrizAdjacenciasValorada,
)
from .generators.pwl.pwl import geraGrafoPwl, tipoGrafo as detect_powerlaw_type
from .generators.convencional.visualizacao import save_graph_png as save_conventional_png
from .generators.pwl.visualizacao import save_graph_png as save_powerlaw_png
from .schemas import (
    DatasetResponse,
    EdgeResponse,
    GenerateGraphRequest,
    GenerateGraphResponse,
    LimitsRequest,
    LimitsResponse,
    NodeResponse,
)


GRAPH_TYPES = {int(key): value for key, value in TIPOS_GRAFOS.items()}
DIRECTED_TYPES = set(TIPOS_DIRIGIDOS)
UNDIRECTED_TYPES = {0, 20, 30}
GENERATED_IMAGES_DIR = Path(__file__).resolve().parents[1] / "generated_images"
GENERATED_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    normalized = re.sub(r"-+", "-", normalized).strip("-._")
    return normalized or "grafo"


def _build_image_filename(dataset_name: str) -> str:
    return f"{_slugify(dataset_name)}-{uuid4().hex}.png"


def _build_image_url(filename: str) -> str:
    return f"/generated-images/{filename}"


def _create_conventional_image(matrix: list[list[Any]], dataset_name: str) -> str:
    filename = _build_image_filename(dataset_name)
    output_path = GENERATED_IMAGES_DIR / filename
    save_conventional_png(matrix, output_path)
    return _build_image_url(filename)


def _create_powerlaw_image(graph: nx.Graph, dataset_name: str, directed: bool) -> str:
    filename = _build_image_filename(dataset_name)
    output_path = GENERATED_IMAGES_DIR / filename
    save_powerlaw_png(graph, output_path, directed=directed)
    return _build_image_url(filename)



def normalized_maximum_edges(graph_type: int, number_vertices: int) -> int:
    """Base finita usada pelo projeto original para calcular densidade."""
    if graph_type in (0, 20):
        return number_vertices * (number_vertices - 1) // 2
    if graph_type in (1, 21):
        return number_vertices * (number_vertices - 1)
    if graph_type == 30:
        return number_vertices * (number_vertices - 1) // 2 + number_vertices
    if graph_type == 31:
        return number_vertices * (number_vertices - 1) + number_vertices
    raise ValueError(f"Tipo de grafo inválido: {graph_type}")


def calculate_limits(request: LimitsRequest) -> LimitsResponse:
    # Componentes=0 significa que o usuário não exige uma quantidade específica
    # de componentes. Nesse caso, não aplicamos o mínimo de conectividade, pois
    # isso impediria a geração de vários grafos esparsos.
    if request.number_components == 0:
        if request.graph_type in (0, 1):
            minimum = 0
            maximum = normalized_maximum_edges(
                request.graph_type,
                request.number_vertices,
            )
        elif request.graph_type in (20, 21):
            # O gerador de multigrafos precisa de pelo menos duas arestas para
            # garantir a existência de uma aresta múltipla.
            minimum = 2
            maximum = math.inf
        else:
            # O gerador de pseudógrafos precisa de ao menos uma aresta para
            # garantir a presença de um laço.
            minimum = 1
            maximum = math.inf
    else:
        minimum, maximum = verificaAresta(
            request.graph_type,
            request.number_vertices,
            request.number_components,
        )

    normalized_maximum = normalized_maximum_edges(
        request.graph_type,
        request.number_vertices,
    )

    if request.density_preference == 1:
        lower = int(minimum)
        upper = int(0.2 * normalized_maximum)
    elif request.density_preference == 2:
        lower = max(int(minimum), int(0.8 * normalized_maximum))
        upper = normalized_maximum
    else:
        lower = int(minimum)
        upper = None if math.isinf(maximum) else int(maximum)

    if upper is not None and upper < lower:
        raise ValueError(
            "A preferência de densidade é incompatível com os demais parâmetros."
        )

    return LimitsResponse(
        minimum=lower,
        maximum=upper,
        normalized_maximum=normalized_maximum,
        maximum_is_unbounded=upper is None,
    )


def _build_edges(
    raw_edges: Iterable[tuple[int, int]],
    weighted: bool,
    min_weight: int,
    max_weight: int,
    seed: int,
) -> list[EdgeResponse]:
    weight_random = random.Random(seed ^ 0x9E3779B1)
    result: list[EdgeResponse] = []

    for index, raw_edge in enumerate(raw_edges):
        source, target = int(raw_edge[0]), int(raw_edge[1])
        result.append(
            EdgeResponse(
                id=index,
                source=source,
                target=target,
                weight=(
                    weight_random.randint(min_weight, max_weight)
                    if weighted
                    else None
                ),
            )
        )

    return result


def _build_matrix(
    number_vertices: int,
    graph_type: int,
    edges: list[EdgeResponse],
    weighted: bool,
) -> list[list[Any]]:
    if weighted:
        matrix: list[list[Any]] = [
            [[] for _ in range(number_vertices)]
            for _ in range(number_vertices)
        ]
        for edge in edges:
            matrix[edge.source][edge.target].append(edge.weight)
            if graph_type in UNDIRECTED_TYPES and edge.source != edge.target:
                matrix[edge.target][edge.source].append(edge.weight)
        return matrix

    matrix = [
        [0 for _ in range(number_vertices)]
        for _ in range(number_vertices)
    ]
    for edge in edges:
        matrix[edge.source][edge.target] += 1
        if graph_type in UNDIRECTED_TYPES and edge.source != edge.target:
            matrix[edge.target][edge.source] += 1
    return matrix


def _build_adjacency_list(
    number_vertices: int,
    graph_type: int,
    edges: list[EdgeResponse],
) -> dict[str, list[dict[str, Any]]]:
    adjacency: dict[str, list[dict[str, Any]]] = {
        str(vertex): [] for vertex in range(number_vertices)
    }

    for edge in edges:
        adjacency[str(edge.source)].append(
            {"target": edge.target, "weight": edge.weight}
        )
        if graph_type in UNDIRECTED_TYPES and edge.source != edge.target:
            adjacency[str(edge.target)].append(
                {"target": edge.source, "weight": edge.weight}
            )

    return adjacency


def _count_components(
    number_vertices: int,
    graph_type: int,
    raw_edges: list[tuple[int, int]],
) -> int:
    graph: nx.Graph | nx.DiGraph
    graph = nx.DiGraph() if graph_type in DIRECTED_TYPES else nx.Graph()
    graph.add_nodes_from(range(number_vertices))
    graph.add_edges_from(raw_edges)

    if graph.is_directed():
        return nx.number_weakly_connected_components(graph)
    return nx.number_connected_components(graph)


def _dataset_name(
    generator: str,
    graph_type: int,
    number_vertices: int,
    number_edges: int,
    seed: int,
    index: int,
    number_components: int | None,
    allocation_factor: int | None = None,
    gamma: float | None = None,
) -> str:
    if generator == "powerlaw":
        return (
            f"{GRAPH_TYPES[graph_type]}-PowerLaw-{number_vertices}-"
            f"{number_edges}-{seed}-{index}-gamma{gamma:.2f}"
        )

    generation_name = GERACAO.get(allocation_factor or 0, "Aleatório")
    return (
        f"{GRAPH_TYPES[graph_type]}-{generation_name}-{number_vertices}-"
        f"{number_edges}-{seed}-{index}-{number_components}"
    )


def _create_dataset_response(
    *,
    dataset_id: int,
    generator: str,
    dataset_seed: int,
    graph_type: int,
    number_vertices: int,
    raw_edges: list[tuple[int, int]],
    weighted: bool,
    min_weight: int,
    max_weight: int,
    detected_type: int,
    number_components: int | None,
    allocation_factor: int | None = None,
    gamma: float | None = None,
    degrees: list[int] | dict[str, list[int]] | None = None,
    edges_override: list[EdgeResponse] | None = None,
    matrix_override: list[list[Any]] | None = None,
    image_url: str | None = None,
) -> DatasetResponse:
    edges = edges_override or _build_edges(
        raw_edges,
        weighted,
        min_weight,
        max_weight,
        dataset_seed,
    )
    matrix = matrix_override or _build_matrix(number_vertices, graph_type, edges, weighted)
    adjacency = _build_adjacency_list(number_vertices, graph_type, edges)
    normalized_maximum = normalized_maximum_edges(graph_type, number_vertices)
    density = len(edges) / normalized_maximum if normalized_maximum else 0.0
    actual_components = _count_components(number_vertices, graph_type, raw_edges)

    warning = None
    if detected_type != graph_type:
        warning = (
            f"O gerador recebeu o tipo {graph_type}, mas a estrutura produzida "
            f"foi detectada como tipo {detected_type}."
        )

    name = _dataset_name(
        generator,
        graph_type,
        number_vertices,
        len(edges),
        dataset_seed,
        dataset_id,
        number_components,
        allocation_factor,
        gamma,
    )

    return DatasetResponse(
        id=dataset_id,
        name=name,
        generator=generator,  # type: ignore[arg-type]
        seed=dataset_seed,
        requested_type=graph_type,
        detected_type=detected_type,
        type_description=GRAPH_TYPES[graph_type],
        directed=graph_type in DIRECTED_TYPES,
        weighted=weighted,
        number_vertices=number_vertices,
        number_edges=len(edges),
        number_components=actual_components,
        density=round(density, 6),
        gamma=gamma,
        warning=warning,
        nodes=[NodeResponse(id=index) for index in range(number_vertices)],
        edges=edges,
        adjacency_matrix=matrix,
        adjacency_list=adjacency,
        degrees=degrees,
        image_url=image_url,
    )


def generate_graphs(request: GenerateGraphRequest) -> GenerateGraphResponse:
    base_seed = request.seed
    if base_seed is None:
        base_seed = random.randint(0, 1000)

    if request.generator == "conventional":
        limits = calculate_limits(
            LimitsRequest(
                graph_type=request.graph_type,
                number_vertices=request.number_vertices,
                number_components=request.number_components,
                density_preference=request.density_preference,
            )
        )
        assert request.number_edges is not None

        if request.number_edges < limits.minimum:
            raise ValueError(
                f"O número de arestas deve ser pelo menos {limits.minimum}."
            )
        if limits.maximum is not None and request.number_edges > limits.maximum:
            raise ValueError(
                f"O número de arestas deve ser no máximo {limits.maximum}."
            )

        # Mantém exatamente o mesmo caminho de execução do main.py original.
        # A função geraDataset() inicializa a semente e escolhe internamente entre
        # os geradores específicos (numC <= 1) e geraComponente() (numC > 1).
        raw_datasets = geraDataset(
            request.graph_type,
            request.number_vertices,
            request.number_edges,
            base_seed,
            request.number_datasets,
            request.number_components,
            request.allocation_factor,
        )

        datasets: list[DatasetResponse] = []
        for index, raw_dataset in enumerate(raw_datasets, start=1):
            raw_edges = [(int(source), int(target)) for source, target in raw_dataset]

            # Também preserva a mesma sequência aleatória usada pelo programa
            # original para atribuir pesos depois de gerar todos os datasets.
            if request.weighted:
                original_matrix = criaMatrizAdjacenciasValorada(
                    raw_edges,
                    request.number_vertices,
                    request.graph_type,
                    request.min_weight,
                    request.max_weight,
                )
                occurrence: dict[tuple[int, int], int] = defaultdict(int)
                edges: list[EdgeResponse] = []
                for edge_id, (source, target) in enumerate(raw_edges):
                    position = occurrence[(source, target)]
                    weight = int(original_matrix[source][target][position])
                    occurrence[(source, target)] += 1
                    edges.append(
                        EdgeResponse(
                            id=edge_id,
                            source=source,
                            target=target,
                            weight=weight,
                        )
                    )
                matrix = original_matrix
            else:
                edges = [
                    EdgeResponse(
                        id=edge_id,
                        source=source,
                        target=target,
                        weight=None,
                    )
                    for edge_id, (source, target) in enumerate(raw_edges)
                ]
                original_matrix = criaMatrizAdjacencias(
                    raw_edges,
                    request.number_vertices,
                    request.graph_type,
                )
                matrix = original_matrix.tolist()

            dataset_name = _dataset_name(
                "conventional",
                request.graph_type,
                request.number_vertices,
                len(edges),
                base_seed,
                index,
                request.number_components,
                request.allocation_factor,
            )
            image_url = _create_conventional_image(matrix, dataset_name)

            datasets.append(
                _create_dataset_response(
                    dataset_id=index,
                    generator="conventional",
                    dataset_seed=base_seed,
                    graph_type=request.graph_type,
                    number_vertices=request.number_vertices,
                    raw_edges=raw_edges,
                    weighted=request.weighted,
                    min_weight=request.min_weight,
                    max_weight=request.max_weight,
                    detected_type=request.graph_type,
                    number_components=request.number_components,
                    allocation_factor=request.allocation_factor,
                    edges_override=edges,
                    matrix_override=matrix,
                    image_url=image_url,
                )
            )

        return GenerateGraphResponse(
            seed=base_seed,
            quantity=len(datasets),
            datasets=datasets,
            limits=limits,
        )

    datasets = []
    for index in range(1, request.number_datasets + 1):
        dataset_seed = base_seed + index - 1
        directed = request.graph_type in DIRECTED_TYPES
        raw_edges, graph, raw_degrees = geraGrafoPwl(
            request.number_vertices,
            request.gamma,
            directed,
            request.graph_type,
            dataset_seed,
            request.unbalanced_directed_degrees,
        )
        converted_edges = [(int(source), int(target)) for source, target in raw_edges]
        detected_type = int(detect_powerlaw_type(graph))

        if isinstance(raw_degrees, tuple):
            degrees: list[int] | dict[str, list[int]] = {
                "out": [int(value) for value in raw_degrees[0]],
                "in": [int(value) for value in raw_degrees[1]],
            }
        else:
            degrees = [int(value) for value in raw_degrees]

        dataset_name = _dataset_name(
            "powerlaw",
            request.graph_type,
            request.number_vertices,
            len(converted_edges),
            dataset_seed,
            index,
            None,
            None,
            request.gamma,
        )
        image_url = _create_powerlaw_image(graph, dataset_name, directed)

        datasets.append(
            _create_dataset_response(
                dataset_id=index,
                generator="powerlaw",
                dataset_seed=dataset_seed,
                graph_type=request.graph_type,
                number_vertices=request.number_vertices,
                raw_edges=converted_edges,
                weighted=request.weighted,
                min_weight=request.min_weight,
                max_weight=request.max_weight,
                detected_type=detected_type,
                number_components=None,
                gamma=request.gamma,
                degrees=degrees,
                image_url=image_url,
            )
        )

    return GenerateGraphResponse(
        seed=base_seed,
        quantity=len(datasets),
        datasets=datasets,
        limits=None,
    )
