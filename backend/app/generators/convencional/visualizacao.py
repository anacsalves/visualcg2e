from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx


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


def _plot_with_igraph(matriz: list[list[Any]], output_path: Path) -> bool:
    try:
        from igraph import Graph, plot
    except Exception:
        return False

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

    # A margem maior impede que vértices, laços, setas e rótulos
    # encostem ou sejam cortados nas bordas da imagem.
    vertex_size = 22 if number_vertices <= 40 else 15
    vertex_label_size = 12 if number_vertices <= 40 else 9
    edge_label_size = 9 if number_vertices <= 40 else 7

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
        target=str(output_path),
    )
    return True


def _plot_with_networkx(matriz: list[list[Any]], output_path: Path) -> None:
    directed = _detect_directed(matriz)
    number_vertices = len(matriz)

    graph: nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph
    graph = nx.MultiDiGraph() if directed else nx.MultiGraph()
    graph.add_nodes_from(range(number_vertices))

    edges, weights = _extract_edges_and_weights(matriz)
    for edge, weight in zip(edges, weights):
        graph.add_edge(edge[0], edge[1], weight=weight)

    figure, axis = plt.subplots(figsize=(7, 7), dpi=120)
    positions = nx.kamada_kawai_layout(graph)

    node_size = 300 if number_vertices <= 40 else 150
    node_font_size = 9 if number_vertices <= 40 else 7

    nx.draw_networkx_nodes(
        graph,
        positions,
        ax=axis,
        node_size=node_size,
        node_color="white",
        edgecolors="black",
        linewidths=1.1,
    )
    nx.draw_networkx_labels(
        graph,
        positions,
        ax=axis,
        font_size=node_font_size,
    )
    nx.draw_networkx_edges(
        graph,
        positions,
        ax=axis,
        arrows=directed,
        arrowstyle="-|>",
        arrowsize=16,
        width=1.1,
        alpha=0.82,
        connectionstyle="arc3,rad=0.07",
    )

    edge_labels: dict[tuple[int, int], str] = {}
    for source, target, data in graph.edges(data=True):
        label = str(data.get("weight", ""))
        key = (source, target)
        if key in edge_labels:
            edge_labels[key] = f"{edge_labels[key]}, {label}"
        else:
            edge_labels[key] = label

    if edge_labels:
        nx.draw_networkx_edge_labels(
            graph,
            positions,
            ax=axis,
            edge_labels=edge_labels,
            font_size=7,
            label_pos=0.55,
        )

    axis.set_axis_off()
    axis.margins(0.18)
    figure.subplots_adjust(left=0.08, right=0.92, bottom=0.08, top=0.92)
    figure.savefig(output_path, format="png", facecolor="white")
    plt.close(figure)


def save_graph_png(matriz: list[list[Any]], output_path: str | Path) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if _plot_with_igraph(matriz, path):
        return str(path)

    _plot_with_networkx(matriz, path)
    return str(path)
