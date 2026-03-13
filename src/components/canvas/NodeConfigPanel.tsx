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

  const renderTextInput = (key: string, label: string, placeholder?: string, defaultVal?: string) => (
    <label key={key} className="block">
      <span className="text-xs font-medium text-gray-600">{label}</span>
      <input
        type="text"
        className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
        placeholder={placeholder}
        value={(config[key] as string) || defaultVal || ""}
        onChange={(e) => updateConfig(key, e.target.value)}
      />
    </label>
  );

  const renderNumberInput = (key: string, label: string, defaultVal?: number) => (
    <label key={key} className="block">
      <span className="text-xs font-medium text-gray-600">{label}</span>
      <input
        type="number"
        className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
        value={(config[key] as number) ?? defaultVal ?? 0}
        onChange={(e) => updateConfig(key, parseFloat(e.target.value))}
      />
    </label>
  );

  const renderSelect = (key: string, label: string, options: string[], defaultVal?: string) => (
    <label key={key} className="block">
      <span className="text-xs font-medium text-gray-600">{label}</span>
      <select
        className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
        value={(config[key] as string) || defaultVal || options[0]}
        onChange={(e) => updateConfig(key, e.target.value)}
      >
        {options.map((o) => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
    </label>
  );

  const renderCheckbox = (key: string, label: string, defaultVal?: boolean) => (
    <label key={key} className="flex items-center gap-2">
      <input
        type="checkbox"
        checked={(config[key] as boolean) ?? defaultVal ?? false}
        onChange={(e) => updateConfig(key, e.target.checked)}
      />
      <span className="text-xs font-medium text-gray-600">{label}</span>
    </label>
  );

  const renderColumnList = (key: string, label: string, placeholder?: string) => (
    <label key={key} className="block">
      <span className="text-xs font-medium text-gray-600">{label}</span>
      <input
        type="text"
        className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
        placeholder={placeholder || "col1, col2, col3"}
        value={Array.isArray(config[key]) ? (config[key] as string[]).join(", ") : ""}
        onChange={(e) =>
          updateConfig(key, e.target.value.split(",").map((s) => s.trim()).filter(Boolean))
        }
      />
    </label>
  );

  const renderJsonTextarea = (key: string, label: string, placeholder?: string, rows = 3) => (
    <label key={key} className="block">
      <span className="text-xs font-medium text-gray-600">{label}</span>
      <textarea
        className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm font-mono"
        rows={rows}
        placeholder={placeholder}
        value={config[key] ? JSON.stringify(config[key], null, 2) : ""}
        onChange={(e) => {
          try { updateConfig(key, JSON.parse(e.target.value)); } catch { /* ignore */ }
        }}
      />
    </label>
  );

  return (
    <div className="w-72 border-l border-gray-200 bg-white p-4 overflow-y-auto">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-800">{toolInfo.label}</h3>
        <button onClick={() => setSelectedNodeId(null)} className="text-gray-400 hover:text-gray-600">
          <X size={18} />
        </button>
      </div>

      <div className="space-y-3">
        {/* === IO === */}
        {toolType === "input_data" && (
          <>
            {renderSelect("source_type", "Source Type", ["file", "sql"], "file")}

            {(config.source_type || "file") === "file" && (
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
                      <option key={f.id} value={f.id}>{f.original_name}</option>
                    ))}
                  </select>
                </label>
                {renderTextInput("delimiter", "Delimiter", ",", ",")}
              </>
            )}

            {config.source_type === "sql" && (
              <>
                {renderTextInput("connection_string", "Connection String", "postgresql://user:pass@host:5432/db")}
                {renderTextInput("table_name", "Table Name (or use query)")}
                <label className="block">
                  <span className="text-xs font-medium text-gray-600">SQL Query</span>
                  <textarea
                    className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm font-mono"
                    rows={3}
                    placeholder="SELECT * FROM table LIMIT 1000"
                    value={(config.query as string) || ""}
                    onChange={(e) => updateConfig("query", e.target.value)}
                  />
                </label>
              </>
            )}
          </>
        )}

        {toolType === "output_data" && (
          <>
            {renderTextInput("filename", "Filename", "output", "output")}
            {renderSelect("format", "Format", ["csv", "xlsx", "json"], "csv")}
          </>
        )}

        {/* === Preparation === */}
        {toolType === "filter" && renderTextInput("expression", "Filter Expression", "e.g. age > 30")}

        {toolType === "select" && (
          <>
            {renderColumnList("columns", "Columns to keep")}
            {renderJsonTextarea("rename", "Rename map (JSON)", '{"old_name": "new_name"}')}
          </>
        )}

        {toolType === "formula" && (
          <>
            {renderTextInput("output_column", "Output Column", "", "new_column")}
            {renderTextInput("expression", "Expression", "e.g. price * quantity")}
          </>
        )}

        {toolType === "sort" && (
          <>
            {renderColumnList("columns", "Sort by columns")}
            {renderCheckbox("ascending", "Ascending", true)}
          </>
        )}

        {toolType === "sample" && (
          <>
            {renderSelect("method", "Method", ["first_n", "last_n", "random_n", "random_pct"], "first_n")}
            {renderNumberInput("n", "N rows", 100)}
            {(config.method === "random_pct") && renderNumberInput("percentage", "Percentage", 10)}
          </>
        )}

        {toolType === "unique" && (
          <>
            {renderColumnList("columns", "Deduplicate on columns", "Leave empty for all")}
            {renderSelect("keep", "Keep", ["first", "last"], "first")}
          </>
        )}

        {toolType === "summarize" && (
          <>
            {renderColumnList("group_by", "Group by")}
            {renderJsonTextarea("aggregations", "Aggregations (JSON)", '[{"column":"amount","function":"sum"}]')}
          </>
        )}

        {toolType === "data_cleanse" && (
          <>
            {renderCheckbox("trim_whitespace", "Trim whitespace")}
            {renderSelect("change_case", "Change case", ["", "upper", "lower", "title"])}
            {renderCheckbox("remove_nulls", "Remove null rows")}
            {renderCheckbox("remove_empty_strings", "Remove empty strings")}
          </>
        )}

        {toolType === "multi_row" && (
          <>
            {renderTextInput("source_column", "Source Column")}
            {renderTextInput("output_column", "Output Column", "", "multi_row_result")}
            {renderNumberInput("row_offset", "Row Offset (-1=prev, 1=next)", -1)}
            {renderSelect("operation", "Operation", ["value", "difference", "percent_change"], "value")}
            {renderColumnList("group_by", "Group By")}
          </>
        )}

        {toolType === "imputation" && (
          <>
            {renderColumnList("columns", "Columns to impute")}
            {renderSelect("method", "Method", ["mean", "median", "mode", "constant", "forward_fill", "backward_fill", "interpolate"], "mean")}
            {config.method === "constant" && renderTextInput("custom_value", "Custom Value")}
            {renderColumnList("group_by", "Group By")}
          </>
        )}

        {toolType === "transpose" && renderTextInput("header_column", "Use as header (optional)")}

        {toolType === "cross_tab" && (
          <>
            {renderTextInput("row_field", "Row Field")}
            {renderTextInput("column_field", "Column Field")}
            {renderTextInput("value_field", "Value Field (optional)")}
            {renderSelect("aggregation", "Aggregation", ["count", "sum", "mean", "min", "max"], "count")}
          </>
        )}

        {toolType === "find_replace" && (
          <>
            {renderTextInput("column", "Column")}
            {renderJsonTextarea("replacements", "Replacements (JSON)", '[{"find":"old","replace":"new"}]')}
            {renderCheckbox("use_regex", "Use Regex")}
            {renderCheckbox("case_sensitive", "Case Sensitive", true)}
          </>
        )}

        {/* === Parse === */}
        {toolType === "text_to_columns" && (
          <>
            {renderTextInput("column", "Column to split")}
            {renderTextInput("delimiter", "Delimiter", ",", ",")}
            {renderNumberInput("max_splits", "Max splits (0=unlimited)", 0)}
            {renderTextInput("output_prefix", "Output column prefix")}
            {renderCheckbox("keep_original", "Keep original column", true)}
          </>
        )}

        {toolType === "regex" && (
          <>
            {renderTextInput("column", "Column")}
            {renderTextInput("pattern", "Regex Pattern", String.raw`e.g. (\d+)-(\w+)`)}
            {renderSelect("mode", "Mode", ["extract", "replace", "match", "findall", "count"], "extract")}
            {config.mode === "replace" && renderTextInput("replacement", "Replacement")}
            {renderTextInput("output_column", "Output Column", "", "regex_result")}
          </>
        )}

        {/* === Join === */}
        {toolType === "join" && (
          <>
            {renderSelect("join_type", "Join Type", ["inner", "left", "right", "outer"], "inner")}
            {renderTextInput("left_key", "Left Key Column")}
            {renderTextInput("right_key", "Right Key Column")}
          </>
        )}

        {toolType === "union" && renderSelect("mode", "Mode", ["by_name", "by_position"], "by_name")}

        {toolType === "append" && (
          <p className="text-xs text-gray-500">
            Connect a Target (top) and Source (bottom) input. Each row in Target will be paired with all rows from Source.
          </p>
        )}

        {toolType === "fuzzy_match" && (
          <>
            {renderTextInput("left_key", "Left Match Column")}
            {renderTextInput("right_key", "Right Match Column")}
            {renderNumberInput("threshold", "Match Threshold (0-100)", 80)}
            {renderSelect("algorithm", "Algorithm", ["ratio", "partial_ratio", "token_sort_ratio", "token_set_ratio"], "ratio")}
          </>
        )}
      </div>
    </div>
  );
}
