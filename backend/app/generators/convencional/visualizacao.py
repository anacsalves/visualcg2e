from __future__ import annotations

from pathlib import Path
from typing import Any


def _detect_directed(matriz: list[list[Any]]) -> bool:
    n = len(matriz)
    for i in range(n):
        for j in range(n):
            c_ij = matriz[i][j]
            c_ji = matriz[j][i]
            cnt_ij = len(c_ij) if isinstance(c_ij, list) else c_ij
            cnt_ji = len(c_ji) if isinstance(c_ji, list) else c_ji
            if cnt_ij != cnt_ji:
                return True
    return False


def _extract_edges_and_weights(
    matriz: list[list[Any]],
) -> tuple[list[tuple[int, int]], list[int]]:
    edges: list[tuple[int, int]] = []
    weights: list[int] = []
    n = len(matriz)

    for i in range(n):
        for j in range(n):
            cell = matriz[i][j]
            if isinstance(cell, list):
                for peso in cell:
                    edges.append((i, j))
                    weights.append(int(peso))
            elif cell > 0:
                edges.append((i, j))
                weights.append(int(cell))

    return edges, weights


def save_graph_png(matriz: list[list[Any]], output_path: str | Path) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from igraph import Graph, plot
    except Exception as error:
        raise RuntimeError(
            "Não foi possível importar python-igraph. Verifique a instalação do backend."
        ) from error

    directed = _detect_directed(matriz)
    edges, weights = _extract_edges_and_weights(matriz)
    number_vertices = len(matriz)

    graph = Graph(directed=directed)
    graph.add_vertices(number_vertices)
    graph.add_edges(edges)
    graph.es["weight"] = weights
    graph.es["label"] = weights
    graph.vs["label"] = graph.vs.indices

    layout = graph.layout("kk")

    vertex_size = 22 if number_vertices <= 40 else 15
    vertex_label_size = 12 if number_vertices <= 40 else 9
    edge_label_size = 9 if number_vertices <= 40 else 7

    try:
        plot(
            graph,
            bbox=(800, 800),
            margin=80,
            layout=layout,
            background="white",
            edge_arrow_size=0.75,
            edge_width=1.0,
            edge_curved=0.08,
            edge_label=graph.es["label"],
            edge_label_size=edge_label_size,
            vertex_size=vertex_size,
            vertex_label_size=vertex_label_size,
            target=str(path),
        )
    except Exception as error:
        raise RuntimeError(
            "A renderização da imagem pelo igraph falhou. Instale pycairo ou cairocffi no ambiente virtual do backend."
        ) from error

    return str(path)
