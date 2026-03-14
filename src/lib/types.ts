export interface NodePosition {
  x: number;
  y: number;
}

export interface WorkflowNode {
  id: string;
  type: string;
  position: NodePosition;
  config: Record<string, unknown>;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle: string;
  targetHandle: string;
}

export interface WorkflowDefinition {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

export interface Workflow {
  id: string;
  name: string;
  definition: WorkflowDefinition;
  created_at: string;
  updated_at: string;
}

export interface NodeResult {
  node_id: string;
  status: "completed" | "error";
  row_count: number;
  columns: string[];
  preview: Record<string, unknown>[];
  error?: string;
}

export interface ExecutionResult {
  id: string;
  workflow_id: string;
  status: "pending" | "running" | "completed" | "failed";
  node_results: NodeResult[];
  error?: string;
  created_at: string;
}

export interface UploadedFile {
  id: string;
  filename: string;
  original_name: string;
  file_format: string;
  size_bytes: number;
  created_at: string;
}

export interface ToolDefinition {
  type: string;
  label: string;
  category: string;
  inputs: string[];
  outputs: string[];
  config_schema: Record<string, ToolConfigField>;
}

export interface ToolConfigField {
  type: string;
  label?: string;
  default?: unknown;
  options?: string[];
  placeholder?: string;
}
