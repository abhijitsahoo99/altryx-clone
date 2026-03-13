"use client";

import { useCallback, useRef, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  type NodeTypes,
  type ReactFlowInstance,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { useWorkflowStore } from "@/hooks/useWorkflow";
import { ToolNode } from "./ToolNode";
import { getToolInfo } from "@/lib/toolRegistry";

const nodeTypes: NodeTypes = {
  toolNode: ToolNode,
};

export function WorkflowCanvas() {
  const reactFlowRef = useRef<ReactFlowInstance | null>(null);
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    addNode,
    setSelectedNodeId,
  } = useWorkflowStore();

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      const toolType = event.dataTransfer.getData("application/tool-type");
      if (!toolType || !reactFlowRef.current) return;

      const position = reactFlowRef.current.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const toolInfo = getToolInfo(toolType);
      const nodeId = `node_${Date.now()}`;

      addNode({
        id: nodeId,
        type: "toolNode",
        position,
        data: {
          toolType,
          config: {},
          label: toolInfo?.label || toolType,
        },
      });
    },
    [addNode]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: { id: string }) => {
      setSelectedNodeId(node.id);
    },
    [setSelectedNodeId]
  );

  const onPaneClick = useCallback(() => {
    setSelectedNodeId(null);
  }, [setSelectedNodeId]);

  const defaultEdgeOptions = useMemo(
    () => ({
      style: { strokeWidth: 2, stroke: "#94a3b8" },
      type: "smoothstep" as const,
    }),
    []
  );

  return (
    <div className="flex-1 h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        onInit={(instance) => {
          reactFlowRef.current = instance;
        }}
        nodeTypes={nodeTypes}
        defaultEdgeOptions={defaultEdgeOptions}
        fitView
        className="bg-gray-50"
      >
        <Background gap={16} size={1} color="#e2e8f0" />
        <Controls />
        <MiniMap
          nodeColor={(n) => {
            const toolType = (n.data as Record<string, unknown>)?.toolType as string;
            return getToolInfo(toolType)?.color || "#6b7280";
          }}
          maskColor="rgb(240, 240, 240, 0.7)"
        />
      </ReactFlow>
    </div>
  );
}
