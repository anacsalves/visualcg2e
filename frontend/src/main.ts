import { checkHealth, generateGraphs, getLimits } from "./api.js";
import { exportAllDatasetsTxt, exportAllImagesPng, exportDatasetTxt, exportImagePng } from "./exports.js";
import type { AllocationFactor, DensityPreference, GeneratorType, GraphDataset, GraphRequest, GraphType } from "./types.js";

function getElement<T extends Element>(selector: string): T {
  const element = document.querySelector<T>(selector);
  if (!element) throw new Error(`Elemento não encontrado: ${selector}`);
  return element;
}
function getElements<T extends Element>(selector: string): T[] { return Array.from(document.querySelectorAll<T>(selector)); }

const controls = {
  generator: getElement<HTMLSelectElement>("#generatorType"), graphType: getElement<HTMLSelectElement>("#graphType"), vertices: getElement<HTMLInputElement>("#vertices"),
  components: getElement<HTMLInputElement>("#components"), densityButtons: getElements<HTMLButtonElement>("[data-density]"), allocationFactor: getElement<HTMLSelectElement>("#allocationFactor"),
  edges: getElement<HTMLInputElement>("#edges"), edgesLabel: getElement<HTMLLabelElement>("#edgesLabel"), gamma: getElement<HTMLInputElement>("#gamma"), unbalancedDirected: getElement<HTMLInputElement>("#unbalancedDirected"),
  weighted: getElement<HTMLInputElement>("#weighted"), minWeight: getElement<HTMLInputElement>("#minWeight"), maxWeight: getElement<HTMLInputElement>("#maxWeight"), seed: getElement<HTMLInputElement>("#seed"), datasets: getElement<HTMLInputElement>("#datasetCount"),
  conventionalFields: getElement<HTMLDivElement>("#conventionalFields"), powerlawFields: getElement<HTMLDivElement>("#powerlawFields"), factorField: getElement<HTMLDivElement>("#factorField"), unbalancedField: getElement<HTMLDivElement>("#unbalancedField"), weightFields: getElement<HTMLDivElement>("#weightFields"),
  generate: getElement<HTMLButtonElement>("#generateButton"), clear: getElement<HTMLButtonElement>("#clearButton"), message: getElement<HTMLParagraphElement>("#formMessage"), apiStatus: getElement<HTMLDivElement>("#apiStatus"),
};
const graphImage = getElement<HTMLImageElement>("#graphImage");
const edgesLayer = getElement<SVGGElement>("#edgesLayer"); const labelsLayer = getElement<SVGGElement>("#labelsLayer"); const nodesLayer = getElement<SVGGElement>("#nodesLayer");
const emptyState = getElement<HTMLDivElement>("#emptyState");
const infoPopover = getElement<HTMLDivElement>("#infoPopover");
const infoPopoverTitle = getElement<HTMLElement>("#infoPopoverTitle");
const infoPopoverText = getElement<HTMLParagraphElement>("#infoPopoverText");

const state: { density: DensityPreference; datasets: GraphDataset[]; currentIndex: number } = { density: 0, datasets: [], currentIndex: 0 };
let limitsRequestSequence = 0;
let activeInfoButton: HTMLButtonElement | null = null;

function currentDataset(): GraphDataset | null { return state.datasets[state.currentIndex] ?? null; }
function isDirectedType(type: GraphType): boolean { return [1, 21, 31].includes(type); }
function clamp(value: number, minimum: number, maximum: number): number { return Math.max(minimum, Math.min(maximum, value)); }

function hideInfoPopover(): void {
  if (activeInfoButton) activeInfoButton.setAttribute("aria-expanded", "false");
  activeInfoButton = null;
  infoPopover.classList.add("hidden");
  infoPopover.setAttribute("aria-hidden", "true");
}

function positionInfoPopover(button: HTMLButtonElement): void {
  const margin = 12;
  const gap = 14;
  const buttonRect = button.getBoundingClientRect();
  const popoverRect = infoPopover.getBoundingClientRect();
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;
  const buttonCenterX = buttonRect.left + buttonRect.width / 2;
  const buttonCenterY = buttonRect.top + buttonRect.height / 2;

  let placement: "top" | "bottom" | "right" | "left";
  let left: number;
  let top: number;

  if (buttonRect.top >= popoverRect.height + gap + margin) {
    placement = "top";
    left = clamp(buttonCenterX - popoverRect.width + 28, margin, viewportWidth - popoverRect.width - margin);
    top = buttonRect.top - popoverRect.height - gap;
    const arrowX = clamp(buttonCenterX - left - 9, 18, popoverRect.width - 36);
    infoPopover.style.setProperty("--arrow-x", `${arrowX}px`);
  } else if (viewportWidth - buttonRect.right >= popoverRect.width + gap + margin) {
    placement = "right";
    left = buttonRect.right + gap;
    top = clamp(buttonCenterY - popoverRect.height / 2, margin, viewportHeight - popoverRect.height - margin);
    const arrowY = clamp(buttonCenterY - top - 9, 18, popoverRect.height - 36);
    infoPopover.style.setProperty("--arrow-y", `${arrowY}px`);
  } else if (buttonRect.left >= popoverRect.width + gap + margin) {
    placement = "left";
    left = buttonRect.left - popoverRect.width - gap;
    top = clamp(buttonCenterY - popoverRect.height / 2, margin, viewportHeight - popoverRect.height - margin);
    const arrowY = clamp(buttonCenterY - top - 9, 18, popoverRect.height - 36);
    infoPopover.style.setProperty("--arrow-y", `${arrowY}px`);
  } else {
    placement = "bottom";
    left = clamp(buttonCenterX - popoverRect.width + 28, margin, viewportWidth - popoverRect.width - margin);
    top = buttonRect.bottom + gap;
    const arrowX = clamp(buttonCenterX - left - 9, 18, popoverRect.width - 36);
    infoPopover.style.setProperty("--arrow-x", `${arrowX}px`);
  }

  infoPopover.dataset.placement = placement;
  infoPopover.style.left = `${left}px`;
  infoPopover.style.top = `${top}px`;
  infoPopover.style.visibility = "visible";
}

function showInfoPopover(button: HTMLButtonElement): void {
  if (activeInfoButton === button) {
    hideInfoPopover();
    return;
  }

  if (activeInfoButton) activeInfoButton.setAttribute("aria-expanded", "false");
  activeInfoButton = button;
  button.setAttribute("aria-expanded", "true");

  infoPopoverTitle.textContent = button.dataset.tooltipTitle ?? "Informação";
  infoPopoverText.textContent = button.dataset.tooltipText ?? "";
  infoPopover.classList.remove("hidden");
  infoPopover.setAttribute("aria-hidden", "false");
  infoPopover.style.visibility = "hidden";

  positionInfoPopover(button);
}

async function updateApiStatus(): Promise<void> {
  const online = await checkHealth();
  controls.apiStatus.textContent = online ? "API conectada" : "API desconectada";
  controls.apiStatus.classList.toggle("offline", !online);
}

function updateConditionalFields(): void {
  const generator = controls.generator.value as GeneratorType;
  const conventional = generator === "conventional";
  controls.conventionalFields.classList.toggle("hidden", !conventional);
  controls.powerlawFields.classList.toggle("hidden", conventional);
  controls.factorField.classList.toggle("hidden", Number(controls.components.value) <= 1);
  controls.unbalancedField.classList.toggle("hidden", !isDirectedType(Number(controls.graphType.value) as GraphType));
  controls.weightFields.classList.toggle("hidden", !controls.weighted.checked);
}

async function updateLimits(): Promise<void> {
  if (controls.generator.value !== "conventional") return;
  const sequence = ++limitsRequestSequence;
  try {
    const vertices = Number(controls.vertices.value);
    const components = Number(controls.components.value);
    if (!Number.isInteger(vertices) || !Number.isInteger(components) || vertices < 2 || components < 0 || components > vertices) return;
    const limits = await getLimits({ graph_type: Number(controls.graphType.value) as GraphType, number_vertices: vertices, number_components: components, density_preference: state.density });
    if (sequence !== limitsRequestSequence) return;
    controls.edges.min = String(limits.minimum);
    controls.edges.max = limits.maximum === null ? "" : String(limits.maximum);
    controls.edgesLabel.textContent = limits.maximum === null ? `Número de arestas (m ≥ ${limits.minimum})` : `Número de arestas (${limits.minimum} ≤ m ≤ ${limits.maximum})`;
    const current = Number(controls.edges.value);
    if (!Number.isFinite(current) || current < limits.minimum || (limits.maximum !== null && current > limits.maximum)) controls.edges.value = String(limits.minimum);
    controls.message.textContent = "";
  } catch (error) {
    if (sequence === limitsRequestSequence) controls.message.textContent = error instanceof Error ? error.message : "Não foi possível calcular os limites.";
  }
}

function parseRequest(): GraphRequest {
  const generator = controls.generator.value as GeneratorType;
  const graphType = Number(controls.graphType.value) as GraphType;
  const numberVertices = Number(controls.vertices.value); const numberComponents = Number(controls.components.value); const numberDatasets = Number(controls.datasets.value);
  const numberEdges = generator === "conventional" ? Number(controls.edges.value) : null;
  const seed = controls.seed.value.trim() === "" ? null : Number(controls.seed.value);
  const minWeight = Number(controls.minWeight.value); const maxWeight = Number(controls.maxWeight.value); const gamma = Number(controls.gamma.value);
  if (!Number.isInteger(numberVertices) || numberVertices < 2 || numberVertices > 300) throw new Error("Use de 2 a 300 vértices na interface visual.");
  if (!Number.isInteger(numberComponents) || numberComponents < 0 || numberComponents > numberVertices) throw new Error("Confira o número de componentes.");
  if (!Number.isInteger(numberDatasets) || numberDatasets < 1 || numberDatasets > 100) throw new Error("Use de 1 a 100 datasets.");
  if (generator === "conventional" && (!Number.isInteger(numberEdges) || (numberEdges ?? -1) < 0)) throw new Error("Informe um número válido de arestas.");
  if (controls.weighted.checked && minWeight > maxWeight) throw new Error("O peso mínimo não pode ser maior que o máximo.");
  if (generator === "powerlaw" && (gamma < 2 || gamma > 3)) throw new Error("O gamma deve estar entre 2 e 3.");
  return {
    generator, graph_type: graphType, number_vertices: numberVertices, number_components: numberComponents,
    density_preference: state.density, number_edges: numberEdges, allocation_factor: Number(controls.allocationFactor.value) as AllocationFactor,
    weighted: controls.weighted.checked, min_weight: minWeight, max_weight: maxWeight, seed, number_datasets: numberDatasets,
    gamma, unbalanced_directed_degrees: controls.unbalancedDirected.checked,
  };
}

function updateInfo(dataset: GraphDataset): void {
  getElement<HTMLSpanElement>("#infoVertices").textContent = String(dataset.number_vertices);
  getElement<HTMLSpanElement>("#infoEdges").textContent = String(dataset.number_edges);
  getElement<HTMLSpanElement>("#infoDensity").textContent = dataset.density.toFixed(3);
  getElement<HTMLSpanElement>("#infoComponents").textContent = dataset.number_components === null ? "—" : String(dataset.number_components);
  getElement<HTMLSpanElement>("#infoSeed").textContent = String(dataset.seed);
  getElement<HTMLSpanElement>("#infoType").textContent = dataset.type_description;
  getElement<HTMLSpanElement>("#infoWeighted").textContent = dataset.weighted ? "sim" : "não";
  getElement<HTMLSpanElement>("#infoGenerator").textContent = dataset.generator === "conventional" ? "Convencional" : `Power-law (γ=${dataset.gamma?.toFixed(2)})`;
  const warning = getElement<HTMLParagraphElement>("#datasetWarning"); warning.textContent = dataset.warning ?? ""; warning.classList.toggle("hidden", dataset.warning === null);
}

function showDataset(index: number): void {
  if (state.datasets.length === 0) return;
  state.currentIndex = (index + state.datasets.length) % state.datasets.length;
  const dataset = currentDataset(); if (!dataset) return;
  edgesLayer.replaceChildren(); labelsLayer.replaceChildren(); nodesLayer.replaceChildren();
  if (dataset.image_url) {
    graphImage.src = `${dataset.image_url}${dataset.image_url.includes("?") ? "&" : "?"}v=${Date.now()}`;
    graphImage.classList.remove("hidden");
  } else {
    graphImage.removeAttribute("src");
    graphImage.classList.add("hidden");
  }
  updateInfo(dataset);
  getElement<HTMLSpanElement>("#pageIndicator").textContent = `${state.currentIndex + 1}/${state.datasets.length}`;
  emptyState.classList.add("hidden");
}

async function handleGenerate(): Promise<void> {
  try {
    controls.message.textContent = "Gerando grafos..."; controls.generate.disabled = true;
    const response = await generateGraphs(parseRequest());
    state.datasets = response.datasets; state.currentIndex = 0;
    if (state.datasets.length === 0) throw new Error("A API não retornou datasets.");
    showDataset(0); controls.message.textContent = `Foram gerados ${state.datasets.length} dataset(s).`;
  } catch (error) {
    controls.message.textContent = error instanceof Error ? error.message : "Não foi possível gerar o grafo.";
  } finally { controls.generate.disabled = false; }
}

function reset(): void {
  hideInfoPopover();
  controls.generator.value = "conventional"; controls.graphType.value = "0"; controls.vertices.value = "0"; controls.components.value = "0";
  controls.allocationFactor.value = "0"; controls.edges.value = "0"; controls.gamma.value = "2.5"; controls.unbalancedDirected.checked = false;
  controls.weighted.checked = false; controls.minWeight.value = "1"; controls.maxWeight.value = "10"; controls.seed.value = ""; controls.datasets.value = "1";
  state.density = 0; state.datasets = []; state.currentIndex = 0;
  controls.densityButtons.forEach((button) => button.classList.toggle("active", button.dataset.density === "0"));
  edgesLayer.replaceChildren(); labelsLayer.replaceChildren(); nodesLayer.replaceChildren(); graphImage.removeAttribute("src"); graphImage.classList.add("hidden"); emptyState.classList.remove("hidden"); getElement<HTMLSpanElement>("#pageIndicator").textContent = "0/0";
  controls.message.textContent = ""; updateConditionalFields(); void updateLimits();
}

getElements<HTMLButtonElement>("[data-step]").forEach((button) => button.addEventListener("click", () => {
  const id = button.dataset.step; if (!id) return; const input = document.getElementById(id); if (!(input instanceof HTMLInputElement)) return;
  const delta = Number(button.dataset.delta); const minimum = input.min ? Number(input.min) : -Infinity; const maximum = input.max ? Number(input.max) : Infinity; const current = input.value === "" ? 0 : Number(input.value);
  input.value = String(Math.max(minimum, Math.min(maximum, current + delta)));
  if (["vertices", "components"].includes(id)) { updateConditionalFields(); void updateLimits(); }
}));
controls.densityButtons.forEach((button) => button.addEventListener("click", () => {
  state.density = Number(button.dataset.density) as DensityPreference;
  controls.densityButtons.forEach((item) => item.classList.toggle("active", item === button)); void updateLimits();
}));
controls.generator.addEventListener("change", () => { updateConditionalFields(); void updateLimits(); });
controls.graphType.addEventListener("change", () => { updateConditionalFields(); void updateLimits(); });
controls.vertices.addEventListener("change", () => { controls.components.max = controls.vertices.value; updateConditionalFields(); void updateLimits(); });
controls.components.addEventListener("change", () => { updateConditionalFields(); void updateLimits(); });
controls.weighted.addEventListener("change", updateConditionalFields);
getElements<HTMLButtonElement>(".tooltip-trigger").forEach((button) => button.addEventListener("click", (event) => {
  event.stopPropagation();
  showInfoPopover(button);
}));
document.addEventListener("click", (event) => {
  const target = event.target;
  if (!(target instanceof Node) || infoPopover.contains(target)) return;
  hideInfoPopover();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") hideInfoPopover();
});
window.addEventListener("resize", hideInfoPopover);
window.addEventListener("scroll", hideInfoPopover, true);
controls.generate.addEventListener("click", () => void handleGenerate()); controls.clear.addEventListener("click", reset);
getElement<HTMLButtonElement>("#previousDataset").addEventListener("click", () => showDataset(state.currentIndex - 1));
getElement<HTMLButtonElement>("#nextDataset").addEventListener("click", () => showDataset(state.currentIndex + 1));
getElement<HTMLButtonElement>("#exportPng").addEventListener("click", () => { const dataset = currentDataset(); if (dataset?.image_url) void exportImagePng(dataset.image_url, dataset.name); });
getElement<HTMLButtonElement>("#exportTxt").addEventListener("click", () => { const dataset = currentDataset(); if (dataset) exportDatasetTxt(dataset); });
getElement<HTMLButtonElement>("#exportAllPng").addEventListener("click", () => { if (state.datasets.length) void exportAllImagesPng(state.datasets); });
getElement<HTMLButtonElement>("#exportAllTxt").addEventListener("click", () => { if (state.datasets.length) exportAllDatasetsTxt(state.datasets); });

updateConditionalFields(); void updateLimits(); void updateApiStatus();
