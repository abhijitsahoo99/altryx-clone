"use client";

import { create } from "zustand";
import type { Node, Edge, OnNodesChange, OnEdgesChange, OnConnect } from "@xyflow/react";
import { applyNodeChanges, applyEdgeChanges, addEdge } from "@xyflow/react";
import type { NodeResult } from "@/lib/types";

interface HistoryEntry {
  nodes: Node[];
  edges: Edge[];
}

const MAX_HISTORY = 50;

interface WorkflowState {
  workflowId: string | null;
  workflowName: string;
  nodes: Node[];
  edges: Edge[];
  selectedNodeId: string | null;
  nodeResults: Record<string, NodeResult>;
  isExecuting: boolean;
  clipboard: Node[];

  // History
  history: HistoryEntry[];
  historyIndex: number;

  setWorkflowId: (id: string | null) => void;
  setWorkflowName: (name: string) => void;
  setNodes: (nodes: Node[]) => void;
  setEdges: (edges: Edge[]) => void;
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
  addNode: (node: Node) => void;
  deleteSelectedNodes: () => void;
  setSelectedNodeId: (id: string | null) => void;
  updateNodeConfig: (nodeId: string, config: Record<string, unknown>) => void;
  setNodeResults: (results: Record<string, NodeResult>) => void;
  setIsExecuting: (v: boolean) => void;

  // Undo/Redo
  pushHistory: () => void;
  undo: () => void;
  redo: () => void;
  canUndo: () => boolean;
  canRedo: () => boolean;

  // Copy/Paste
  copySelectedNodes: () => void;
  pasteNodes: () => void;
}

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  workflowId: null,
  workflowName: "Untitled Workflow",
  nodes: [],
  edges: [],
  selectedNodeId: null,
  nodeResults: {},
  isExecuting: false,
  clipboard: [],
  history: [],
  historyIndex: -1,

  setWorkflowId: (id) => set({ workflowId: id }),
  setWorkflowName: (name) => set({ workflowName: name }),
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),

  onNodesChange: (changes) => {
    const prev = get().nodes;
    const next = applyNodeChanges(changes, prev);
    set({ nodes: next });
    // Push history for significant changes (add/remove, not just selection/position)
    const hasStructuralChange = changes.some(
      (c) => c.type === "remove" || c.type === "add"
    );
    if (hasStructuralChange) get().pushHistory();
  },
  onEdgesChange: (changes) => {
    const next = applyEdgeChanges(changes, get().edges);
    set({ edges: next });
    const hasStructuralChange = changes.some(
      (c) => c.type === "remove" || c.type === "add"
    );
    if (hasStructuralChange) get().pushHistory();
  },
  onConnect: (connection) => {
    set({ edges: addEdge(connection, get().edges) });
    get().pushHistory();
  },

  addNode: (node) => {
    set({ nodes: [...get().nodes, node] });
    get().pushHistory();
  },

  deleteSelectedNodes: () => {
    const { nodes, edges, selectedNodeId } = get();
    if (!selectedNodeId) return;
    const newNodes = nodes.filter((n) => n.id !== selectedNodeId);
    const newEdges = edges.filter(
      (e) => e.source !== selectedNodeId && e.target !== selectedNodeId
    );
    set({ nodes: newNodes, edges: newEdges, selectedNodeId: null });
    get().pushHistory();
  },

  setSelectedNodeId: (id) => set({ selectedNodeId: id }),

  updateNodeConfig: (nodeId, config) => {
    set({
      nodes: get().nodes.map((n) =>
        n.id === nodeId ? { ...n, data: { ...n.data, config } } : n
      ),
    });
  },

  setNodeResults: (results) => set({ nodeResults: results }),
  setIsExecuting: (v) => set({ isExecuting: v }),

  // History management
  pushHistory: () => {
    const { nodes, edges, history, historyIndex } = get();
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push({ nodes: structuredClone(nodes), edges: structuredClone(edges) });
    if (newHistory.length > MAX_HISTORY) newHistory.shift();
    set({ history: newHistory, historyIndex: newHistory.length - 1 });
  },

  undo: () => {
    const { historyIndex, history } = get();
    if (historyIndex <= 0) return;
    const prev = history[historyIndex - 1];
    set({
      nodes: structuredClone(prev.nodes),
      edges: structuredClone(prev.edges),
      historyIndex: historyIndex - 1,
    });
  },

  redo: () => {
    const { historyIndex, history } = get();
    if (historyIndex >= history.length - 1) return;
    const next = history[historyIndex + 1];
    set({
      nodes: structuredClone(next.nodes),
      edges: structuredClone(next.edges),
      historyIndex: historyIndex + 1,
    });
  },

  canUndo: () => get().historyIndex > 0,
  canRedo: () => get().historyIndex < get().history.length - 1,

  // Copy/Paste
  copySelectedNodes: () => {
    const { nodes, selectedNodeId } = get();
    const selected = nodes.filter(
      (n) => n.id === selectedNodeId || n.selected
    );
    set({ clipboard: structuredClone(selected) });
  },

  pasteNodes: () => {
    const { clipboard, nodes } = get();
    if (clipboard.length === 0) return;
    const newNodes = clipboard.map((n) => ({
      ...n,
      id: `node_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      position: { x: n.position.x + 50, y: n.position.y + 50 },
      selected: false,
    }));
    set({ nodes: [...nodes, ...newNodes] });
    get().pushHistory();
  },
}));
