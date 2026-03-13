const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`API error ${res.status}: ${detail}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Workflows
export const api = {
  listWorkflows: () => request<import("./types").Workflow[]>("/api/workflows"),

  createWorkflow: (data: { name?: string; definition?: import("./types").WorkflowDefinition }) =>
    request<import("./types").Workflow>("/api/workflows", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getWorkflow: (id: string) => request<import("./types").Workflow>(`/api/workflows/${id}`),

  updateWorkflow: (id: string, data: { name?: string; definition?: import("./types").WorkflowDefinition }) =>
    request<import("./types").Workflow>(`/api/workflows/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  deleteWorkflow: (id: string) =>
    request<void>(`/api/workflows/${id}`, { method: "DELETE" }),

  // Executions
  executeWorkflow: (workflowId: string) =>
    request<import("./types").ExecutionResult>(`/api/workflows/${workflowId}/execute`, {
      method: "POST",
    }),

  getExecution: (id: string) => request<import("./types").ExecutionResult>(`/api/executions/${id}`),

  // Files
  uploadFile: async (file: File): Promise<import("./types").UploadedFile> => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/api/files/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);
    return res.json();
  },

  listFiles: () => request<import("./types").UploadedFile[]>("/api/files"),

  previewFile: (id: string, rows = 50) =>
    request<{ columns: string[]; row_count: number; data: Record<string, unknown>[] }>(
      `/api/files/${id}/preview?rows=${rows}`
    ),

  deleteFile: (id: string) => request<void>(`/api/files/${id}`, { method: "DELETE" }),

  // Tools
  listTools: () => request<import("./types").ToolDefinition[]>("/api/tools"),
};
