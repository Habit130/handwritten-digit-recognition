export type Workspace = "walkthrough" | "routes" | "live";
export type RouteId = "direct" | "practical" | "challenge";

export interface LayerContract {
  id: string;
  name: string;
  term: string;
  operation: string;
  output_shape: number[];
  summary: string;
  code_anchor: string;
}

export interface NetworkContract {
  schema_version: string;
  architecture_version: string;
  input: {
    shape: number[];
    pixel_range: [number, number];
    normalization: { mean: number; std: number };
  };
  classes: string[];
  layers: LayerContract[];
}

export interface LayerTrace {
  id: string;
  shape: number[];
  values: number[];
  min: number;
  max: number;
  summary: string;
}

export interface NetworkTrace {
  schema_version: string;
  architecture_version: string;
  source: "reference" | "live";
  model_route: "reference" | RouteId;
  predicted_digit: number;
  probabilities: number[];
  input_pixels: number[];
  layers: LayerTrace[];
}

export interface ChallengeRoute {
  id: RouteId;
  level: string;
  name: string;
  term: string;
  tagline: string;
  responsibilities: string[];
  model_path: string;
  commands: string[];
  code_files: string[];
}

export interface CodeFile {
  path: string;
  content: string;
}

export interface CodeResponse {
  route: RouteId;
  files: CodeFile[];
}

export interface ModelStatus {
  loaded: boolean;
  route: RouteId | null;
  model_path: string | null;
}

export interface ApiFailure {
  error: {
    stage: string;
    message: string;
    detail: string;
  };
}
