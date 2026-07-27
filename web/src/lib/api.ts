import type {
  ApiFailure,
  ChallengeRoute,
  CodeResponse,
  ModelStatus,
  NetworkContract,
  NetworkTrace,
  RouteId,
} from "./types";

export class LabApiError extends Error {
  readonly stage: string;
  readonly detail: string;

  constructor(payload: ApiFailure["error"]) {
    super(payload.message);
    this.name = "LabApiError";
    this.stage = payload.stage;
    this.detail = payload.detail;
  }
}

async function requestJson<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(path, init);
  const payload: unknown = await response.json();
  if (!response.ok) {
    const failure = payload as Partial<ApiFailure>;
    if (failure.error !== undefined) {
      throw new LabApiError(failure.error);
    }
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return payload as T;
}

export const api = {
  contract: () => requestJson<NetworkContract>("/api/contract"),
  referenceTrace: () =>
    requestJson<NetworkTrace>("/api/reference-trace"),
  routes: () => requestJson<ChallengeRoute[]>("/api/routes"),
  code: (route: RouteId) =>
    requestJson<CodeResponse>(`/api/code/${route}`),
  modelStatus: () =>
    requestJson<ModelStatus>("/api/models/status"),
  loadModel: (route: RouteId) =>
    requestJson<ModelStatus>(`/api/models/${route}/load`, {
      method: "POST",
    }),
  infer: (pixels: number[]) =>
    requestJson<NetworkTrace>("/api/infer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pixels }),
    }),
};
