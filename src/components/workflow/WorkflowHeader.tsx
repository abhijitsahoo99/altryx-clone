"use client";

import { Play, Save, Loader2 } from "lucide-react";
import { useWorkflowStore } from "@/hooks/useWorkflow";
import { useExecution } from "@/hooks/useExecution";
import { api } from "@/lib/api";

export function WorkflowHeader() {
  const { workflowId, workflowName, setWorkflowName, nodes, edges, isExecuting } = useWorkflowStore();
  const { run } = useExecution();

  const handleSave = async () => {
    if (!workflowId) return;
    await api.updateWorkflow(workflowId, {
      name: workflowName,
      definition: {
        nodes: nodes.map((n) => ({
          id: n.id,
          type: n.type || "unknown",
          position: n.position,
          config: (n.data as Record<string, unknown>)?.config as Record<string, unknown> || {},
        })),
        edges: edges.map((e) => ({
          id: e.id,
          source: e.source,
          target: e.target,
          sourceHandle: e.sourceHandle || "output",
          targetHandle: e.targetHandle || "input",
        })),
      },
    });
  };

  return (
    <div className="h-12 border-b border-gray-200 bg-white flex items-center justify-between px-4">
      <input
        type="text"
        value={workflowName}
        onChange={(e) => setWorkflowName(e.target.value)}
        className="text-sm font-medium text-gray-800 border-none outline-none bg-transparent focus:ring-1 focus:ring-blue-300 rounded px-2 py-1"
      />

      <div className="flex items-center gap-2">
        <button
          onClick={handleSave}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded"
        >
          <Save size={16} />
          Save
        </button>
        <button
          onClick={run}
          disabled={isExecuting}
          className="flex items-center gap-1.5 px-4 py-1.5 text-sm text-white bg-green-600 hover:bg-green-700 rounded disabled:opacity-50"
        >
          {isExecuting ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
          {isExecuting ? "Running..." : "Run"}
        </button>
      </div>
    </div>
  );
}
