import type { GraphDataset, GraphEdge, GraphNode } from "./types.js";

const SVG_NS = "http://www.w3.org/2000/svg";
const WIDTH = 1000;
const HEIGHT = 650;
const MARGIN = 45;

interface Point { x: number; y: number }
interface EdgeGeometry { d: string; labelX: number; labelY: number }

function createSvgElement<K extends keyof SVGElementTagNameMap>(
  tagName: K,
  attributes: Record<string, string | number> = {},
): SVGElementTagNameMap[K] {
  const element = document.createElementNS(SVG_NS, tagName);
  for (const [name, value] of Object.entries(attributes)) {
    element.setAttribute(name, String(value));
  }
  return element;
}

function clamp(value: number, minimum: number, maximum: number): number {
  return Math.max(minimum, Math.min(maximum, value));
}

function mulberry32(seed: number): () => number {
  let value = seed >>> 0;
  return () => {
    value += 0x6d2b79f5;
    let temporary = value;
    temporary = Math.imul(temporary ^ (temporary >>> 15), temporary | 1);
    temporary ^= temporary + Math.imul(temporary ^ (temporary >>> 7), temporary | 61);
    return ((temporary ^ (temporary >>> 14)) >>> 0) / 4294967296;
  };
}

function initialCircularLayout(nodes: GraphNode[], seed: number): void {
  const random = mulberry32(seed);
  const centerX = WIDTH / 2;
  const centerY = HEIGHT / 2;
  const radius = Math.min(WIDTH, HEIGHT) * 0.38;
  nodes.forEach((node, index) => {
    const angle = (Math.PI * 2 * index) / Math.max(1, nodes.length);
    const jitter = (random() - 0.5) * 28;
    node.x = centerX + Math.cos(angle) * (radius + jitter);
    node.y = centerY + Math.sin(angle) * (radius + jitter);
  });
}

function forceLayout(nodes: GraphNode[], edges: GraphEdge[], seed: number): void {
  initialCircularLayout(nodes, seed);
  if (nodes.length > 260) return;

  const random = mulberry32(seed ^ 0xa5a5a5a5);
  const velocities: Point[] = nodes.map(() => ({ x: 0, y: 0 }));
  const iterations = nodes.length > 150 ? 90 : 160;

  for (let iteration = 0; iteration < iterations; iteration += 1) {
    const cooling = 1 - iteration / iterations;
    const forces: Point[] = nodes.map(() => ({ x: 0, y: 0 }));

    for (let i = 0; i < nodes.length; i += 1) {
      for (let j = i + 1; j < nodes.length; j += 1) {
        const a = nodes[i]; const b = nodes[j];
        const fa = forces[i]; const fb = forces[j];
        if (!a || !b || !fa || !fb) continue;
        let dx = (b.x ?? 0) - (a.x ?? 0);
        let dy = (b.y ?? 0) - (a.y ?? 0);
        let distanceSquared = dx * dx + dy * dy;
        if (distanceSquared < 1) {
          dx = (random() - 0.5) * 2;
          dy = (random() - 0.5) * 2;
          distanceSquared = dx * dx + dy * dy;
        }
        const distance = Math.sqrt(distanceSquared);
        const repulsion = 2600 / distanceSquared;
        const fx = (dx / distance) * repulsion;
        const fy = (dy / distance) * repulsion;
        fa.x -= fx; fa.y -= fy; fb.x += fx; fb.y += fy;
      }
    }

    for (const edge of edges) {
      if (edge.source === edge.target) continue;
      const a = nodes[edge.source]; const b = nodes[edge.target];
      const fa = forces[edge.source]; const fb = forces[edge.target];
      if (!a || !b || !fa || !fb) continue;
      const dx = (b.x ?? 0) - (a.x ?? 0);
      const dy = (b.y ?? 0) - (a.y ?? 0);
      const distance = Math.max(1, Math.hypot(dx, dy));
      const desired = nodes.length > 100 ? 48 : 70;
      const spring = (distance - desired) * 0.0055;
      const fx = (dx / distance) * spring;
      const fy = (dy / distance) * spring;
      fa.x += fx; fa.y += fy; fb.x -= fx; fb.y -= fy;
    }

    nodes.forEach((node, index) => {
      const force = forces[index]; const velocity = velocities[index];
      if (!force || !velocity) return;
      force.x += (WIDTH / 2 - (node.x ?? 0)) * 0.0008;
      force.y += (HEIGHT / 2 - (node.y ?? 0)) * 0.0008;
      velocity.x = (velocity.x + force.x) * 0.83;
      velocity.y = (velocity.y + force.y) * 0.83;
      node.x = clamp((node.x ?? 0) + velocity.x * cooling * 2, MARGIN, WIDTH - MARGIN);
      node.y = clamp((node.y ?? 0) + velocity.y * cooling * 2, MARGIN, HEIGHT - MARGIN);
    });
  }
}

function prepareParallelEdges(edges: GraphEdge[]): void {
  const groups = new Map<string, GraphEdge[]>();
  for (const edge of edges) {
    const key = edge.source === edge.target
      ? `loop-${edge.source}`
      : [edge.source, edge.target].sort((a, b) => a - b).join("-");
    const group = groups.get(key) ?? [];
    group.push(edge);
    groups.set(key, group);
  }
  for (const group of groups.values()) {
    group.forEach((edge, index) => {
      edge.parallelIndex = index;
      edge.parallelTotal = group.length;
    });
  }
}

function edgeGeometry(edge: GraphEdge, nodes: GraphNode[]): EdgeGeometry | null {
  const a = nodes[edge.source]; const b = nodes[edge.target];
  if (!a || !b || a.x === undefined || a.y === undefined || b.x === undefined || b.y === undefined) return null;
  const radius = 10;

  if (edge.source === edge.target) {
    const offset = (edge.parallelIndex ?? 0) * 7;
    return {
      d: `M ${a.x + 5} ${a.y - 7} C ${a.x + 35 + offset} ${a.y - 45 - offset}, ${a.x - 35 - offset} ${a.y - 45 - offset}, ${a.x - 5} ${a.y - 7}`,
      labelX: a.x,
      labelY: a.y - 41 - offset,
    };
  }

  const dx = b.x - a.x; const dy = b.y - a.y;
  const distance = Math.max(1, Math.hypot(dx, dy));
  const ux = dx / distance; const uy = dy / distance;
  const startX = a.x + ux * radius; const startY = a.y + uy * radius;
  const endX = b.x - ux * (radius + 5); const endY = b.y - uy * (radius + 5);
  const index = (edge.parallelIndex ?? 0) - ((edge.parallelTotal ?? 1) - 1) / 2;
  const curve = index * 19;
  const controlX = (startX + endX) / 2 - uy * curve;
  const controlY = (startY + endY) / 2 + ux * curve;
  return {
    d: `M ${startX} ${startY} Q ${controlX} ${controlY} ${endX} ${endY}`,
    labelX: 0.25 * startX + 0.5 * controlX + 0.25 * endX,
    labelY: 0.25 * startY + 0.5 * controlY + 0.25 * endY - 4,
  };
}

export function renderGraph(
  dataset: GraphDataset,
  edgesLayer: SVGGElement,
  labelsLayer: SVGGElement,
  nodesLayer: SVGGElement,
): void {
  edgesLayer.replaceChildren(); labelsLayer.replaceChildren(); nodesLayer.replaceChildren();
  forceLayout(dataset.nodes, dataset.edges, dataset.seed);
  prepareParallelEdges(dataset.edges);

  for (const edge of dataset.edges) {
    const geometry = edgeGeometry(edge, dataset.nodes);
    if (!geometry) continue;
    edgesLayer.append(createSvgElement("path", {
      d: geometry.d,
      class: `edge${dataset.directed ? " directed" : ""}`,
    }));
    if (dataset.weighted && edge.weight !== null) {
      const label = createSvgElement("text", {
        x: geometry.labelX, y: geometry.labelY, class: "edge-label", "text-anchor": "middle",
      });
      label.textContent = String(edge.weight);
      labelsLayer.append(label);
    }
  }

  for (const node of dataset.nodes) {
    if (node.x === undefined || node.y === undefined) continue;
    const group = createSvgElement("g", { "data-node-id": node.id });
    const circle = createSvgElement("circle", { cx: node.x, cy: node.y, r: 10, class: "node" });
    const label = createSvgElement("text", { x: node.x, y: node.y + 0.5, class: "node-label" });
    label.textContent = String(node.id);
    group.append(circle, label); nodesLayer.append(group);
  }
}
