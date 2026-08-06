export type GeneratorType = "conventional" | "powerlaw";
export type GraphType = 0 | 1 | 20 | 21 | 30 | 31;
export type DensityPreference = 0 | 1 | 2;
export type AllocationFactor = 0 | 1 | 2;

export interface GraphRequest {
  generator: GeneratorType;
  graph_type: GraphType;
  number_vertices: number;
  number_components: number;
  density_preference: DensityPreference;
  number_edges: number | null;
  allocation_factor: AllocationFactor;
  weighted: boolean;
  min_weight: number;
  max_weight: number;
  seed: number | null;
  number_datasets: number;
  gamma: number;
  unbalanced_directed_degrees: boolean;
}

export interface GraphLimitsRequest {
  graph_type: GraphType;
  number_vertices: number;
  number_components: number;
  density_preference: DensityPreference;
}

export interface GraphLimits {
  minimum: number;
  maximum: number | null;
  normalized_maximum: number;
  maximum_is_unbounded: boolean;
}

export interface GraphNode {
  id: number;
  x?: number;
  y?: number;
}

export interface GraphEdge {
  id: number;
  source: number;
  target: number;
  weight: number | null;
  parallelIndex?: number;
  parallelTotal?: number;
}

export interface GraphDataset {
  id: number;
  name: string;
  generator: GeneratorType;
  seed: number;
  requested_type: GraphType;
  detected_type: GraphType;
  type_description: string;
  directed: boolean;
  weighted: boolean;
  number_vertices: number;
  number_edges: number;
  number_components: number | null;
  density: number;
  gamma: number | null;
  warning: string | null;
  nodes: GraphNode[];
  edges: GraphEdge[];
  adjacency_matrix: unknown[][];
  adjacency_list: Record<string, Array<{ target: number; weight: number | null }>>;
  degrees: number[] | Record<string, number[]> | null;
  image_url: string | null;
}

export interface GraphResponse {
  seed: number;
  quantity: number;
  datasets: GraphDataset[];
  limits: GraphLimits | null;
}
