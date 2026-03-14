"use client";

import { useCallback } from "react";
import { api } from "@/lib/api";
import { useWorkflowStore } from "./useWorkflow";
import type { NodeResult, WorkflowDefinition } from "@/lib/types";

export function useExecution() {
  const run = useCallback(async () => {
    // Read fresh state from the store at execution time
    const { workflowId, nodes, edges, setNodeResults, setIsExecuting } =
      useWorkflowStore.getState();

    if (!workflowId) {
      console.warn("Cannot run: no workflow ID (save the workflow first)");
      return;
    }

    if (nodes.length === 0) {
      console.warn("Cannot run: no nodes on canvas");
      return;
    }

    setIsExecuting(true);
    setNodeResults({});

    try {
      // Save the current workflow state first
      const definition: WorkflowDefinition = {
        nodes: nodes.map((n) => ({
          id: n.id,
          type: ((n.data as Record<string, unknown>)?.toolType as string) || "unknown",
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
      };

      await api.updateWorkflow(workflowId, { definition });

      // Execute
      const result = await api.executeWorkflow(workflowId);

      // Convert to map
      const resultMap: Record<string, NodeResult> = {};
      for (const nr of result.node_results) {
        resultMap[nr.node_id] = nr;
      }
      setNodeResults(resultMap);
    } catch (err) {
      console.error("Execution failed:", err);
    } finally {
      useWorkflowStore.getState().setIsExecuting(false);
    }
  }, []);

  return { run };
}
