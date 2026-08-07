from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

GraphGenerator = Literal["conventional", "powerlaw"]
GraphType = Literal[0, 1, 20, 21, 30, 31]


class LimitsRequest(BaseModel):
    graph_type: GraphType
    number_vertices: int = Field(ge=2, le=5000)
    number_components: int = Field(default=0, ge=0)
    density_preference: Literal[0, 1, 2] = 0

    @model_validator(mode="after")
    def validate_components(self) -> "LimitsRequest":
        if self.number_components > self.number_vertices:
            raise ValueError(
                "O número de componentes não pode ser maior que o número de vértices."
            )
        return self


class GenerateGraphRequest(BaseModel):
    generator: GraphGenerator = "conventional"
    graph_type: GraphType = 31
    number_vertices: int = Field(default=30, ge=2, le=5000)
    number_components: int = Field(default=0, ge=0)
    density_preference: Literal[0, 1, 2] = 0
    number_edges: int | None = Field(default=None, ge=0)
    allocation_factor: Literal[0, 1, 2] = 0

    weighted: bool = False
    min_weight: int = 1
    max_weight: int = 10

    seed: int | None = None
    number_datasets: int = Field(default=1, ge=1, le=100)

    gamma: float = Field(default=2.5, ge=2.0, le=3.0)
    unbalanced_directed_degrees: bool = False

    @model_validator(mode="after")
    def validate_request(self) -> "GenerateGraphRequest":
        if self.number_components > self.number_vertices:
            raise ValueError(
                "O número de componentes não pode ser maior que o número de vértices."
            )

        if self.weighted and self.min_weight > self.max_weight:
            raise ValueError("O peso mínimo não pode ser maior que o peso máximo.")

        if self.generator == "conventional" and self.number_edges is None:
            raise ValueError("Informe o número de arestas para o gerador convencional.")

        return self


class EdgeResponse(BaseModel):
    id: int
    source: int
    target: int
    weight: int | None = None


class NodeResponse(BaseModel):
    id: int


class DatasetResponse(BaseModel):
    id: int
    name: str
    generator: GraphGenerator
    seed: int
    requested_type: int
    detected_type: int
    type_description: str
    directed: bool
    weighted: bool
    number_vertices: int
    number_edges: int
    number_components: int | None
    density: float
    gamma: float | None = None
    warning: str | None = None
    nodes: list[NodeResponse]
    edges: list[EdgeResponse]
    adjacency_matrix: list[list[Any]]
    adjacency_list: dict[str, list[dict[str, Any]]]
    degrees: list[int] | dict[str, list[int]] | None = None
    image_url: str | None = None


class LimitsResponse(BaseModel):
    minimum: int
    maximum: int | None
    normalized_maximum: int
    maximum_is_unbounded: bool


class GenerateGraphResponse(BaseModel):
    seed: int
    quantity: int
    datasets: list[DatasetResponse]
    limits: LimitsResponse | None = None
