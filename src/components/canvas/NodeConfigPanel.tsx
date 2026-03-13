"use client";

import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { useWorkflowStore } from "@/hooks/useWorkflow";
import { getToolInfo } from "@/lib/toolRegistry";
import { api } from "@/lib/api";
import type { UploadedFile } from "@/lib/types";

export function NodeConfigPanel() {
  const { nodes, selectedNodeId, updateNodeConfig, setSelectedNodeId } = useWorkflowStore();
  const [files, setFiles] = useState<UploadedFile[]>([]);

  const selectedNode = nodes.find((n) => n.id === selectedNodeId);
  const toolType = (selectedNode?.data as Record<string, unknown>)?.toolType as string | undefined;
  const config = ((selectedNode?.data as Record<string, unknown>)?.config || {}) as Record<string, unknown>;
  const toolInfo = toolType ? getToolInfo(toolType) : undefined;

  useEffect(() => {
    if (toolType === "input_data") {
      api.listFiles().then(setFiles).catch(console.error);
    }
  }, [toolType]);

  if (!selectedNode || !toolInfo) return null;

  const updateConfig = (key: string, value: unknown) => {
    if (!selectedNodeId) return;
    updateNodeConfig(selectedNodeId, { ...config, [key]: value });
  };

  return (
    <div className="w-72 border-l border-gray-200 bg-white p-4 overflow-y-auto">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-800">{toolInfo.label}</h3>
        <button onClick={() => setSelectedNodeId(null)} className="text-gray-400 hover:text-gray-600">
          <X size={18} />
        </button>
      </div>

      <div className="space-y-3">
        {toolType === "input_data" && (
          <>
            <label className="block">
              <span className="text-xs font-medium text-gray-600">File</span>
              <select
                className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
                value={(config.file_id as string) || ""}
                onChange={(e) => {
                  const file = files.find((f) => f.id === e.target.value);
                  updateConfig("file_id", e.target.value);
                  if (file) {
                    updateConfig("filename", file.filename);
                    updateConfig("file_format", file.file_format);
                  }
                }}
              >
                <option value="">Select a file...</option>
                {files.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.original_name}
                  </option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="text-xs font-medium text-gray-600">Delimiter</span>
              <input
                type="text"
                className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
                value={(config.delimiter as string) || ","}
                onChange={(e) => updateConfig("delimiter", e.target.value)}
              />
            </label>
          </>
        )}

        {toolType === "filter" && (
          <label className="block">
            <span className="text-xs font-medium text-gray-600">Filter Expression</span>
            <input
              type="text"
              className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
              placeholder="e.g. age > 30"
              value={(config.expression as string) || ""}
              onChange={(e) => updateConfig("expression", e.target.value)}
            />
          </label>
        )}

        {toolType === "select" && (
          <label className="block">
            <span className="text-xs font-medium text-gray-600">Columns (comma-separated)</span>
            <input
              type="text"
              className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
              placeholder="col1, col2, col3"
              value={Array.isArray(config.columns) ? (config.columns as string[]).join(", ") : ""}
              onChange={(e) =>
                updateConfig(
                  "columns",
                  e.target.value.split(",").map((s) => s.trim()).filter(Boolean)
                )
              }
            />
          </label>
        )}

        {toolType === "formula" && (
          <>
            <label className="block">
              <span className="text-xs font-medium text-gray-600">Output Column</span>
              <input
                type="text"
                className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
                value={(config.output_column as string) || "new_column"}
                onChange={(e) => updateConfig("output_column", e.target.value)}
              />
            </label>
            <label className="block">
              <span className="text-xs font-medium text-gray-600">Expression</span>
              <input
                type="text"
                className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
                placeholder="e.g. price * quantity"
                value={(config.expression as string) || ""}
                onChange={(e) => updateConfig("expression", e.target.value)}
              />
            </label>
          </>
        )}

        {toolType === "sort" && (
          <>
            <label className="block">
              <span className="text-xs font-medium text-gray-600">Sort Columns (comma-separated)</span>
              <input
                type="text"
                className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
                placeholder="col1, col2"
                value={Array.isArray(config.columns) ? (config.columns as string[]).join(", ") : ""}
                onChange={(e) =>
                  updateConfig(
                    "columns",
                    e.target.value.split(",").map((s) => s.trim()).filter(Boolean)
                  )
                }
              />
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={(config.ascending as boolean) !== false}
                onChange={(e) => updateConfig("ascending", e.target.checked)}
              />
              <span className="text-xs font-medium text-gray-600">Ascending</span>
            </label>
          </>
        )}

        {toolType === "sample" && (
          <>
            <label className="block">
              <span className="text-xs font-medium text-gray-600">Method</span>
              <select
                className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
                value={(config.method as string) || "first_n"}
                onChange={(e) => updateConfig("method", e.target.value)}
              >
                <option value="first_n">First N</option>
                <option value="last_n">Last N</option>
                <option value="random_n">Random N</option>
                <option value="random_pct">Random %</option>
              </select>
            </label>
            <label className="block">
              <span className="text-xs font-medium text-gray-600">N</span>
              <input
                type="number"
                className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
                value={(config.n as number) || 100}
                onChange={(e) => updateConfig("n", parseInt(e.target.value))}
              />
            </label>
          </>
        )}

        {toolType === "unique" && (
          <label className="block">
            <span className="text-xs font-medium text-gray-600">Deduplicate on (comma-separated)</span>
            <input
              type="text"
              className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
              placeholder="Leave empty for all columns"
              value={Array.isArray(config.columns) ? (config.columns as string[]).join(", ") : ""}
              onChange={(e) =>
                updateConfig(
                  "columns",
                  e.target.value.split(",").map((s) => s.trim()).filter(Boolean)
                )
              }
            />
          </label>
        )}

        {toolType === "summarize" && (
          <>
            <label className="block">
              <span className="text-xs font-medium text-gray-600">Group By (comma-separated)</span>
              <input
                type="text"
                className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
                placeholder="col1, col2"
                value={Array.isArray(config.group_by) ? (config.group_by as string[]).join(", ") : ""}
                onChange={(e) =>
                  updateConfig(
                    "group_by",
                    e.target.value.split(",").map((s) => s.trim()).filter(Boolean)
                  )
                }
              />
            </label>
            <label className="block">
              <span className="text-xs font-medium text-gray-600">Aggregations (JSON)</span>
              <textarea
                className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm font-mono"
                rows={3}
                placeholder={`[{"column":"amount","function":"sum"}]`}
                value={
                  config.aggregations
                    ? JSON.stringify(config.aggregations, null, 2)
                    : ""
                }
                onChange={(e) => {
                  try {
                    updateConfig("aggregations", JSON.parse(e.target.value));
                  } catch { /* ignore parse errors while typing */ }
                }}
              />
            </label>
          </>
        )}

        {toolType === "data_cleanse" && (
          <>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={(config.trim_whitespace as boolean) || false}
                onChange={(e) => updateConfig("trim_whitespace", e.target.checked)}
              />
              <span className="text-xs font-medium text-gray-600">Trim whitespace</span>
            </label>
            <label className="block">
              <span className="text-xs font-medium text-gray-600">Change case</span>
              <select
                className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
                value={(config.change_case as string) || ""}
                onChange={(e) => updateConfig("change_case", e.target.value || null)}
              >
                <option value="">None</option>
                <option value="upper">UPPER</option>
                <option value="lower">lower</option>
                <option value="title">Title Case</option>
              </select>
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={(config.remove_nulls as boolean) || false}
                onChange={(e) => updateConfig("remove_nulls", e.target.checked)}
              />
              <span className="text-xs font-medium text-gray-600">Remove null rows</span>
            </label>
          </>
        )}

        {toolType === "join" && (
          <>
            <label className="block">
              <span className="text-xs font-medium text-gray-600">Join Type</span>
              <select
                className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
                value={(config.join_type as string) || "inner"}
                onChange={(e) => updateConfig("join_type", e.target.value)}
              >
                <option value="inner">Inner</option>
                <option value="left">Left</option>
                <option value="right">Right</option>
                <option value="outer">Outer</option>
              </select>
            </label>
            <label className="block">
              <span className="text-xs font-medium text-gray-600">Left Key</span>
              <input
                type="text"
                className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
                value={(config.left_key as string) || ""}
                onChange={(e) => updateConfig("left_key", e.target.value)}
              />
            </label>
            <label className="block">
              <span className="text-xs font-medium text-gray-600">Right Key</span>
              <input
                type="text"
                className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
                value={(config.right_key as string) || ""}
                onChange={(e) => updateConfig("right_key", e.target.value)}
              />
            </label>
          </>
        )}

        {toolType === "union" && (
          <label className="block">
            <span className="text-xs font-medium text-gray-600">Mode</span>
            <select
              className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
              value={(config.mode as string) || "by_name"}
              onChange={(e) => updateConfig("mode", e.target.value)}
            >
              <option value="by_name">By Column Name</option>
              <option value="by_position">By Position</option>
            </select>
          </label>
        )}

        {toolType === "output_data" && (
          <>
            <label className="block">
              <span className="text-xs font-medium text-gray-600">Filename</span>
              <input
                type="text"
                className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
                value={(config.filename as string) || "output"}
                onChange={(e) => updateConfig("filename", e.target.value)}
              />
            </label>
            <label className="block">
              <span className="text-xs font-medium text-gray-600">Format</span>
              <select
                className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
                value={(config.format as string) || "csv"}
                onChange={(e) => updateConfig("format", e.target.value)}
              >
                <option value="csv">CSV</option>
                <option value="xlsx">Excel</option>
                <option value="json">JSON</option>
              </select>
            </label>
          </>
        )}
      </div>
    </div>
  );
}
