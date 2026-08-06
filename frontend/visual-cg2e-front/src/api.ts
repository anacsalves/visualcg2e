import type {
  GraphLimits,
  GraphLimitsRequest,
  GraphRequest,
  GraphResponse,
} from "./types.js";

const API_URL = "/api";

interface ApiErrorBody {
  detail?: string | Array<{ msg?: string }>;
}

async function readError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as ApiErrorBody;
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail.map((item) => item.msg ?? "Parâmetro inválido").join("; ");
    }
  } catch {
    // resposta sem JSON
  }
  return `Erro HTTP ${response.status}.`;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

export async function getLimits(request: GraphLimitsRequest): Promise<GraphLimits> {
  const response = await fetch(`${API_URL}/graphs/limits`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw new Error(await readError(response));
  return response.json() as Promise<GraphLimits>;
}

export async function generateGraphs(request: GraphRequest): Promise<GraphResponse> {
  const response = await fetch(`${API_URL}/graphs/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw new Error(await readError(response));
  return response.json() as Promise<GraphResponse>;
}
