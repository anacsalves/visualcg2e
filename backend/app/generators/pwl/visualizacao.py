from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx


def save_graph_png(
    graph: nx.Graph,
    output_path: str | Path,
    directed: bool = False,
) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    number_nodes = graph.number_of_nodes()
    figure, axis = plt.subplots(figsize=(7, 7), dpi=120)

    if number_nodes <= 50:
        positions = nx.spring_layout(graph, seed=42)
    else:
        positions = nx.kamada_kawai_layout(graph)

    node_size = 260 if number_nodes <= 80 else 115
    font_size = 9 if number_nodes <= 80 else 7

    nx.draw_networkx_nodes(
        graph,
        positions,
        ax=axis,
        node_size=node_size,
        node_color="skyblue",
        edgecolors="black",
        linewidths=1.0,
    )
    nx.draw_networkx_labels(
        graph,
        positions,
        ax=axis,
        font_size=font_size,
    )
    nx.draw_networkx_edges(
        graph,
        positions,
        ax=axis,
        alpha=0.5,
        arrows=directed,
        arrowstyle="-|>",
        arrowsize=15,
        connectionstyle="arc3,rad=0.07",
    )

    edge_labels = {}
    for source, target, data in graph.edges(data=True):
        if "weight" in data and data["weight"] is not None:
            edge_labels[(source, target)] = str(data["weight"])

    if edge_labels:
        nx.draw_networkx_edge_labels(
            graph,
            positions,
            ax=axis,
            edge_labels=edge_labels,
            font_size=7,
        )

    axis.set_title("Visualização do Grafo Gerado", pad=14)
    axis.set_axis_off()
    axis.margins(0.18)
    figure.subplots_adjust(left=0.08, right=0.92, bottom=0.08, top=0.9)
    figure.savefig(path, format="png", facecolor="white")
    plt.close(figure)
    return str(path)
