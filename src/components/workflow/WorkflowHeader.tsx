"use client";

import { Play, Save, Loader2, Undo2, Redo2, Copy, Clipboard, Moon, Sun } from "lucide-react";
import { useWorkflowStore } from "@/hooks/useWorkflow";
import { useExecution } from "@/hooks/useExecution";
import { useDarkMode } from "@/hooks/useDarkMode";
import { api } from "@/lib/api";

export function WorkflowHeader() {
  const {
    workflowId,
    workflowName,
    setWorkflowName,
    nodes,
    edges,
    isExecuting,
    undo,
    redo,
    canUndo,
    canRedo,
    copySelectedNodes,
    pasteNodes,
    selectedNodeId,
  } = useWorkflowStore();
  const { run } = useExecution();
  const { isDark, toggle: toggleDark } = useDarkMode();

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
      <div className="flex items-center gap-2">
        <input
          type="text"
          value={workflowName}
          onChange={(e) => setWorkflowName(e.target.value)}
          className="text-sm font-medium text-gray-800 border-none outline-none bg-transparent focus:ring-1 focus:ring-blue-300 rounded px-2 py-1"
        />

        <div className="h-5 w-px bg-gray-200 mx-1" />

        <button
          onClick={undo}
          disabled={!canUndo()}
          title="Undo (Ctrl+Z)"
          className="p-1.5 text-gray-500 hover:bg-gray-100 rounded disabled:opacity-30"
        >
          <Undo2 size={16} />
        </button>
        <button
          onClick={redo}
          disabled={!canRedo()}
          title="Redo (Ctrl+Shift+Z)"
          className="p-1.5 text-gray-500 hover:bg-gray-100 rounded disabled:opacity-30"
        >
          <Redo2 size={16} />
        </button>

        <div className="h-5 w-px bg-gray-200 mx-1" />

        <button
          onClick={copySelectedNodes}
          disabled={!selectedNodeId}
          title="Copy (Ctrl+C)"
          className="p-1.5 text-gray-500 hover:bg-gray-100 rounded disabled:opacity-30"
        >
          <Copy size={16} />
        </button>
        <button
          onClick={pasteNodes}
          title="Paste (Ctrl+V)"
          className="p-1.5 text-gray-500 hover:bg-gray-100 rounded disabled:opacity-30"
        >
          <Clipboard size={16} />
        </button>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={toggleDark}
          title="Toggle dark mode"
          className="p-1.5 text-gray-500 hover:bg-gray-100 rounded"
        >
          {isDark ? <Sun size={16} /> : <Moon size={16} />}
        </button>

        <span className="text-xs text-gray-400 mr-2">
          {nodes.length} node{nodes.length !== 1 ? "s" : ""}
        </span>
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
