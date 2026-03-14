"use client";

import { useEffect, useState, useMemo } from "react";
import { X, ChevronDown } from "lucide-react";
import { useWorkflowStore } from "@/hooks/useWorkflow";
import { getToolInfo } from "@/lib/toolRegistry";
import { api } from "@/lib/api";
import type { UploadedFile } from "@/lib/types";

/**
 * Walk edges backwards from a node to find all upstream columns.
 * For join/append tools with two inputs, returns columns per handle.
 */
function useUpstreamColumns(nodeId: string | null) {
  const { edges, nodeResults, nodes } = useWorkflowStore();

  return useMemo(() => {
    if (!nodeId) return { columns: [] as string[], leftColumns: [] as string[], rightColumns: [] as string[] };

    const incomingEdges = edges.filter((e) => e.target === nodeId);
    const allCols: string[] = [];
    let leftCols: string[] = [];
    let rightCols: string[] = [];

    for (const edge of incomingEdges) {
      const sourceResult = nodeResults[edge.source];
      const handle = edge.targetHandle || "input";

      if (sourceResult?.columns?.length) {
        allCols.push(...sourceResult.columns);
        if (handle === "left" || handle === "target") {
          leftCols = sourceResult.columns;
        } else if (handle === "right" || handle === "source") {
          rightCols = sourceResult.columns;
        }
      } else {
        // Fallback: try to walk further upstream recursively (one level)
        const parentEdges = edges.filter((e2) => e2.target === edge.source);
        for (const pe of parentEdges) {
          const parentResult = nodeResults[pe.source];
          if (parentResult?.columns?.length) {
            allCols.push(...parentResult.columns);
          }
        }
      }
    }

    // Deduplicate
    const unique = [...new Set(allCols)];
    return { columns: unique, leftColumns: leftCols, rightColumns: rightCols };
  }, [nodeId, edges, nodeResults, nodes]);
}

// Multi-select dropdown for picking columns
function ColumnMultiSelect({
  label,
  available,
  selected,
  onChange,
  placeholder,
}: {
  label: string;
  available: string[];
  selected: string[];
  onChange: (cols: string[]) => void;
  placeholder?: string;
}) {
  const [open, setOpen] = useState(false);

  const toggle = (col: string) => {
    if (selected.includes(col)) {
      onChange(selected.filter((c) => c !== col));
    } else {
      onChange([...selected, col]);
    }
  };

  if (available.length === 0) {
    return (
      <label className="block">
        <span className="text-xs font-medium text-gray-600">{label}</span>
        <input
          type="text"
          className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
          placeholder={placeholder || "col1, col2 (run workflow to auto-detect)"}
          value={selected.join(", ")}
          onChange={(e) =>
            onChange(e.target.value.split(",").map((s) => s.trim()).filter(Boolean))
          }
        />
      </label>
    );
  }

  return (
    <div className="block">
      <span className="text-xs font-medium text-gray-600">{label}</span>
      <div className="relative mt-1">
        <button
          type="button"
          className="w-full flex items-center justify-between rounded border border-gray-300 px-2 py-1.5 text-sm text-left bg-white hover:border-gray-400"
          onClick={() => setOpen(!open)}
        >
          <span className={selected.length ? "text-gray-800 truncate" : "text-gray-400"}>
            {selected.length ? selected.join(", ") : placeholder || "Select columns..."}
          </span>
          <ChevronDown size={14} className={`text-gray-400 transition-transform ${open ? "rotate-180" : ""}`} />
        </button>
        {open && (
          <div className="absolute z-50 mt-1 w-full max-h-48 overflow-y-auto bg-white border border-gray-200 rounded shadow-lg">
            {available.map((col) => (
              <label
                key={col}
                className="flex items-center gap-2 px-2 py-1.5 text-sm hover:bg-gray-50 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={selected.includes(col)}
                  onChange={() => toggle(col)}
                  className="rounded"
                />
                <span className="truncate">{col}</span>
              </label>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Single column selector dropdown
function ColumnSelect({
  label,
  available,
  value,
  onChange,
  placeholder,
}: {
  label: string;
  available: string[];
  value: string;
  onChange: (col: string) => void;
  placeholder?: string;
}) {
  if (available.length === 0) {
    return (
      <label className="block">
        <span className="text-xs font-medium text-gray-600">{label}</span>
        <input
          type="text"
          className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
          placeholder={placeholder || "Column name (run workflow to auto-detect)"}
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
      </label>
    );
  }

  return (
    <label className="block">
      <span className="text-xs font-medium text-gray-600">{label}</span>
      <select
        className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">{placeholder || "Select column..."}</option>
        {available.map((col) => (
          <option key={col} value={col}>{col}</option>
        ))}
      </select>
    </label>
  );
}

export function NodeConfigPanel() {
  const { nodes, selectedNodeId, updateNodeConfig, setSelectedNodeId } = useWorkflowStore();
  const [files, setFiles] = useState<UploadedFile[]>([]);

  const selectedNode = nodes.find((n) => n.id === selectedNodeId);
  const toolType = (selectedNode?.data as Record<string, unknown>)?.toolType as string | undefined;
  const config = ((selectedNode?.data as Record<string, unknown>)?.config || {}) as Record<string, unknown>;
  const toolInfo = toolType ? getToolInfo(toolType) : undefined;

  const { columns, leftColumns, rightColumns } = useUpstreamColumns(selectedNodeId);

  useEffect(() => {
    if (toolType === "input_data") {
      api.listFiles().then(setFiles).catch(console.error);
    }
  }, [toolType, selectedNodeId]);

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

  // Dynamic column multi-select (falls back to text input if no upstream data)
  const renderColumnMultiSelect = (key: string, label: string, availableCols?: string[], placeholder?: string) => (
    <ColumnMultiSelect
      key={key}
      label={label}
      available={availableCols ?? columns}
      selected={Array.isArray(config[key]) ? (config[key] as string[]) : []}
      onChange={(cols) => updateConfig(key, cols)}
      placeholder={placeholder}
    />
  );

  // Dynamic single column select (falls back to text input if no upstream data)
  const renderColumnSelect = (key: string, label: string, availableCols?: string[], placeholder?: string) => (
    <ColumnSelect
      key={key}
      label={label}
      available={availableCols ?? columns}
      value={(config[key] as string) || ""}
      onChange={(col) => updateConfig(key, col)}
      placeholder={placeholder}
    />
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

  // Hint banner when upstream columns are available
  const columnHint = columns.length > 0 ? (
    <div className="text-xs text-blue-600 bg-blue-50 border border-blue-100 rounded px-2 py-1.5 mb-1">
      {columns.length} column{columns.length !== 1 ? "s" : ""} detected from upstream
    </div>
  ) : null;

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
                      if (!selectedNodeId) return;
                      const file = files.find((f) => f.id === e.target.value);
                      updateNodeConfig(selectedNodeId, {
                        ...config,
                        file_id: e.target.value,
                        ...(file && { filename: file.filename, file_format: file.file_format }),
                      });
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
        {toolType === "filter" && (() => {
          const operators = ["==", "!=", ">", ">=", "<", "<=", "contains", "not contains", "startswith", "endswith", "isnull", "notnull"];
          const buildExpr = (col: string, op: string, val: string) => {
            if (!col) return "";
            if (op === "isnull") return `${col}.isnull()`;
            if (op === "notnull") return `${col}.notnull()`;
            if (!val) return "";
            const isNum = !isNaN(Number(val)) && val.trim() !== "";
            if (op === "contains") return `${col}.str.contains("${val}")`;
            if (op === "not contains") return `~${col}.str.contains("${val}")`;
            if (op === "startswith") return `${col}.str.startswith("${val}")`;
            if (op === "endswith") return `${col}.str.endswith("${val}")`;
            return isNum ? `${col} ${op} ${val}` : `${col} ${op} "${val}"`;
          };
          const curCol = (config.filter_column as string) || "";
          const curOp = (config.filter_operator as string) || "==";
          const curVal = (config.filter_value as string) || "";
          const needsValue = !["isnull", "notnull"].includes(curOp);

          return (
            <>
              {columnHint}
              {columns.length > 0 ? (
                <>
                  <label className="block">
                    <span className="text-xs font-medium text-gray-600">Column</span>
                    <select
                      className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
                      value={curCol}
                      onChange={(e) => {
                        updateConfig("filter_column", e.target.value);
                        const expr = buildExpr(e.target.value, curOp, curVal);
                        if (expr) updateConfig("expression", expr);
                      }}
                    >
                      <option value="">Select column...</option>
                      {columns.map((col) => (
                        <option key={col} value={col}>{col}</option>
                      ))}
                    </select>
                  </label>
                  <label className="block">
                    <span className="text-xs font-medium text-gray-600">Operator</span>
                    <select
                      className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
                      value={curOp}
                      onChange={(e) => {
                        updateConfig("filter_operator", e.target.value);
                        const expr = buildExpr(curCol, e.target.value, curVal);
                        if (expr) updateConfig("expression", expr);
                      }}
                    >
                      {operators.map((op) => (
                        <option key={op} value={op}>{op}</option>
                      ))}
                    </select>
                  </label>
                  {needsValue && (
                    <label className="block">
                      <span className="text-xs font-medium text-gray-600">Value</span>
                      <input
                        type="text"
                        className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
                        placeholder="e.g. 30 or NYC"
                        value={curVal}
                        onChange={(e) => {
                          updateConfig("filter_value", e.target.value);
                          const expr = buildExpr(curCol, curOp, e.target.value);
                          if (expr) updateConfig("expression", expr);
                        }}
                      />
                    </label>
                  )}
                  {(config.expression as string) && (
                    <div className="text-xs text-gray-500 bg-gray-50 rounded px-2 py-1.5 font-mono break-all">
                      {config.expression as string}
                    </div>
                  )}
                </>
              ) : (
                renderTextInput("expression", "Filter Expression", "e.g. age > 30")
              )}
            </>
          );
        })()}

        {toolType === "select" && (
          <>
            {columnHint}
            {renderColumnMultiSelect("columns", "Columns to keep")}
            {renderJsonTextarea("rename", "Rename map (JSON)", '{"old_name": "new_name"}')}
          </>
        )}

        {toolType === "formula" && (
          <>
            {columnHint}
            {renderTextInput("output_column", "Output Column", "", "new_column")}
            {renderTextInput("expression", "Expression", columns.length >= 2 ? `e.g. ${columns[0]} * ${columns[1]}` : "e.g. price * quantity")}
          </>
        )}

        {toolType === "sort" && (
          <>
            {columnHint}
            {renderColumnMultiSelect("columns", "Sort by columns")}
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
            {columnHint}
            {renderColumnMultiSelect("columns", "Deduplicate on columns", columns, "Leave empty for all")}
            {renderSelect("keep", "Keep", ["first", "last"], "first")}
          </>
        )}

        {toolType === "summarize" && (
          <>
            {columnHint}
            {renderColumnMultiSelect("group_by", "Group by")}
            {renderJsonTextarea("aggregations", "Aggregations (JSON)",
              columns.length > 0
                ? `[{"column":"${columns[0]}","function":"sum"}]`
                : '[{"column":"amount","function":"sum"}]'
            )}
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
            {columnHint}
            {renderColumnSelect("source_column", "Source Column")}
            {renderTextInput("output_column", "Output Column", "", "multi_row_result")}
            {renderNumberInput("row_offset", "Row Offset (-1=prev, 1=next)", -1)}
            {renderSelect("operation", "Operation", ["value", "difference", "percent_change"], "value")}
            {renderColumnMultiSelect("group_by", "Group By")}
          </>
        )}

        {toolType === "imputation" && (
          <>
            {columnHint}
            {renderColumnMultiSelect("columns", "Columns to impute")}
            {renderSelect("method", "Method", ["mean", "median", "mode", "constant", "forward_fill", "backward_fill", "interpolate"], "mean")}
            {config.method === "constant" && renderTextInput("custom_value", "Custom Value")}
            {renderColumnMultiSelect("group_by", "Group By")}
          </>
        )}

        {toolType === "transpose" && (
          <>
            {columnHint}
            {renderColumnSelect("header_column", "Use as header (optional)")}
          </>
        )}

        {toolType === "cross_tab" && (
          <>
            {columnHint}
            {renderColumnSelect("row_field", "Row Field")}
            {renderColumnSelect("column_field", "Column Field")}
            {renderColumnSelect("value_field", "Value Field (optional)")}
            {renderSelect("aggregation", "Aggregation", ["count", "sum", "mean", "min", "max"], "count")}
          </>
        )}

        {toolType === "find_replace" && (
          <>
            {columnHint}
            {renderColumnSelect("column", "Column")}
            {renderJsonTextarea("replacements", "Replacements (JSON)", '[{"find":"old","replace":"new"}]')}
            {renderCheckbox("use_regex", "Use Regex")}
            {renderCheckbox("case_sensitive", "Case Sensitive", true)}
          </>
        )}

        {/* === Parse === */}
        {toolType === "text_to_columns" && (
          <>
            {columnHint}
            {renderColumnSelect("column", "Column to split")}
            {renderTextInput("delimiter", "Delimiter", ",", ",")}
            {renderNumberInput("max_splits", "Max splits (0=unlimited)", 0)}
            {renderTextInput("output_prefix", "Output column prefix")}
            {renderCheckbox("keep_original", "Keep original column", true)}
          </>
        )}

        {toolType === "regex" && (
          <>
            {columnHint}
            {renderColumnSelect("column", "Column")}
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
            {leftColumns.length > 0 && (
              <div className="text-xs text-blue-600 bg-blue-50 border border-blue-100 rounded px-2 py-1.5">
                Left: {leftColumns.length} cols / Right: {rightColumns.length} cols
              </div>
            )}
            {renderColumnSelect("left_key", "Left Key Column", leftColumns)}
            {renderColumnSelect("right_key", "Right Key Column", rightColumns)}
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
            {leftColumns.length > 0 && (
              <div className="text-xs text-blue-600 bg-blue-50 border border-blue-100 rounded px-2 py-1.5">
                Left: {leftColumns.length} cols / Right: {rightColumns.length} cols
              </div>
            )}
            {renderColumnSelect("left_key", "Left Match Column", leftColumns)}
            {renderColumnSelect("right_key", "Right Match Column", rightColumns)}
            {renderNumberInput("threshold", "Match Threshold (0-100)", 80)}
            {renderSelect("algorithm", "Algorithm", ["ratio", "partial_ratio", "token_sort_ratio", "token_set_ratio"], "ratio")}
          </>
        )}
      </div>
    </div>
  );
}
