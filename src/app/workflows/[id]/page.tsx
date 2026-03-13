"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ReactFlowProvider } from "@xyflow/react";

import { useWorkflowStore } from "@/hooks/useWorkflow";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";
import { api } from "@/lib/api";
import { WorkflowHeader } from "@/components/workflow/WorkflowHeader";
import { ToolPalette } from "@/components/toolbar/ToolPalette";
import { WorkflowCanvas } from "@/components/canvas/WorkflowCanvas";
import { NodeConfigPanel } from "@/components/canvas/NodeConfigPanel";
import { DataPreview } from "@/components/preview/DataPreview";

export default function WorkflowEditorPage() {
  const params = useParams();
  const workflowId = params.id as string;
  const [loading, setLoading] = useState(true);

  const { setWorkflowId, setWorkflowName, setNodes, setEdges } = useWorkflowStore();
  useKeyboardShortcuts();

  useEffect(() => {
    async function load() {
      try {
        const wf = await api.getWorkflow(workflowId);
        setWorkflowId(wf.id);
        setWorkflowName(wf.name);

        // Convert backend nodes to React Flow nodes
        const rfNodes = wf.definition.nodes.map((n) => ({
          id: n.id,
          type: "toolNode",
          position: n.position,
          data: {
            toolType: n.type,
            config: n.config,
            label: n.type,
          },
        }));
        setNodes(rfNodes);
        setEdges(wf.definition.edges);
      } catch (err) {
        console.error("Failed to load workflow:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [workflowId, setWorkflowId, setWorkflowName, setNodes, setEdges]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen text-gray-400">Loading workflow...</div>
    );
  }

  return (
    <ReactFlowProvider>
      <div className="h-screen flex flex-col">
        <WorkflowHeader />
        <div className="flex flex-1 overflow-hidden">
          <ToolPalette />
          <div className="flex-1 flex flex-col">
            <WorkflowCanvas />
            <DataPreview />
          </div>
          <NodeConfigPanel />
        </div>
      </div>
    </ReactFlowProvider>
  );
}
