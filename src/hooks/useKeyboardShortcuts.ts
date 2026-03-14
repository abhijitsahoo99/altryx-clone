"use client";

import { useEffect } from "react";
import { useWorkflowStore } from "./useWorkflow";
import { useExecution } from "./useExecution";

export function useKeyboardShortcuts() {
  const {
    undo,
    redo,
    copySelectedNodes,
    pasteNodes,
    deleteSelectedNodes,
    selectedNodeId,
  } = useWorkflowStore();
  const { run } = useExecution();

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      // Don't intercept when typing in inputs
      if (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.tagName === "SELECT" ||
        target.isContentEditable
      ) {
        return;
      }

      const isMod = e.metaKey || e.ctrlKey;

      if (isMod && e.key === "z" && !e.shiftKey) {
        e.preventDefault();
        undo();
      } else if (isMod && e.key === "z" && e.shiftKey) {
        e.preventDefault();
        redo();
      } else if (isMod && e.key === "y") {
        e.preventDefault();
        redo();
      } else if (isMod && e.key === "c") {
        e.preventDefault();
        copySelectedNodes();
      } else if (isMod && e.key === "v") {
        e.preventDefault();
        pasteNodes();
      } else if ((e.key === "Delete" || e.key === "Backspace") && selectedNodeId) {
        e.preventDefault();
        deleteSelectedNodes();
      } else if (isMod && e.key === "Enter") {
        e.preventDefault();
        run();
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [undo, redo, copySelectedNodes, pasteNodes, deleteSelectedNodes, selectedNodeId, run]);
}
