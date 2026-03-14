"use client";

import { useMemo, useState } from "react";
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  createColumnHelper,
} from "@tanstack/react-table";
import { useWorkflowStore } from "@/hooks/useWorkflow";
import { BarChart3, Table } from "lucide-react";

function ColumnProfile({ data, column }: { data: Record<string, unknown>[]; column: string }) {
  const stats = useMemo(() => {
    const values = data.map((r) => r[column]);
    const nonNull = values.filter((v) => v !== null && v !== undefined && v !== "");
    const nullCount = values.length - nonNull.length;
    const uniqueCount = new Set(nonNull.map(String)).size;

    const numericValues = nonNull.map(Number).filter((n) => !isNaN(n));
    const isNumeric = numericValues.length > nonNull.length * 0.5;

    let min: string | undefined;
    let max: string | undefined;
    let mean: string | undefined;

    if (isNumeric && numericValues.length > 0) {
      min = Math.min(...numericValues).toFixed(2);
      max = Math.max(...numericValues).toFixed(2);
      mean = (numericValues.reduce((a, b) => a + b, 0) / numericValues.length).toFixed(2);
    }

    return { total: values.length, nullCount, uniqueCount, isNumeric, min, max, mean };
  }, [data, column]);

  return (
    <div className="text-xs space-y-0.5">
      <div className="flex justify-between">
        <span className="text-gray-500">Nulls:</span>
        <span className={stats.nullCount > 0 ? "text-orange-600" : "text-gray-700"}>
          {stats.nullCount} ({((stats.nullCount / stats.total) * 100).toFixed(0)}%)
        </span>
      </div>
      <div className="flex justify-between">
        <span className="text-gray-500">Unique:</span>
        <span className="text-gray-700">{stats.uniqueCount}</span>
      </div>
      {stats.isNumeric && (
        <>
          <div className="flex justify-between">
            <span className="text-gray-500">Min:</span>
            <span className="text-gray-700">{stats.min}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Max:</span>
            <span className="text-gray-700">{stats.max}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Mean:</span>
            <span className="text-gray-700">{stats.mean}</span>
          </div>
        </>
      )}
    </div>
  );
}

export function DataPreview() {
  const { selectedNodeId, nodeResults } = useWorkflowStore();
  const [viewMode, setViewMode] = useState<"table" | "profile">("table");
  const result = selectedNodeId ? nodeResults[selectedNodeId] : null;

  const columns = useMemo(() => {
    if (!result || !result.columns.length) return [];
    const helper = createColumnHelper<Record<string, unknown>>();
    return result.columns.map((col) =>
      helper.accessor(col, {
        header: col,
        cell: (info) => {
          const val = info.getValue();
          return val === null || val === undefined ? "" : String(val);
        },
      })
    );
  }, [result]);

  const data = useMemo(() => result?.preview || [], [result]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (!result) {
    return (
      <div className="h-52 border-t border-gray-200 bg-white flex items-center justify-center text-sm text-gray-400">
        Select a node and run the workflow to preview data.
      </div>
    );
  }

  if (result.status === "error") {
    return (
      <div className="h-52 border-t border-gray-200 bg-white p-4">
        <div className="text-sm text-red-600 font-medium">Error on node</div>
        <div className="text-sm text-red-500 mt-1 font-mono bg-red-50 p-2 rounded">{result.error}</div>
      </div>
    );
  }

  return (
    <div className="h-52 border-t border-gray-200 bg-white flex flex-col">
      <div className="px-4 py-2 border-b border-gray-100 flex items-center justify-between">
        <span className="text-xs font-medium text-gray-500">
          {result.row_count} rows x {result.columns.length} columns
        </span>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setViewMode("table")}
            className={`p-1 rounded ${viewMode === "table" ? "bg-blue-100 text-blue-600" : "text-gray-400 hover:text-gray-600"}`}
            title="Table view"
          >
            <Table size={14} />
          </button>
          <button
            onClick={() => setViewMode("profile")}
            className={`p-1 rounded ${viewMode === "profile" ? "bg-blue-100 text-blue-600" : "text-gray-400 hover:text-gray-600"}`}
            title="Profile view"
          >
            <BarChart3 size={14} />
          </button>
        </div>
      </div>

      {viewMode === "table" ? (
        <div className="flex-1 overflow-auto">
          <table className="w-full text-xs">
            <thead className="sticky top-0 bg-gray-50">
              {table.getHeaderGroups().map((hg) => (
                <tr key={hg.id}>
                  {hg.headers.map((h) => (
                    <th
                      key={h.id}
                      className="px-3 py-1.5 text-left font-semibold text-gray-600 border-b border-gray-200 whitespace-nowrap"
                    >
                      {flexRender(h.column.columnDef.header, h.getContext())}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map((row) => (
                <tr key={row.id} className="hover:bg-gray-50">
                  {row.getVisibleCells().map((cell) => (
                    <td
                      key={cell.id}
                      className="px-3 py-1 text-gray-700 border-b border-gray-100 whitespace-nowrap max-w-[200px] truncate"
                    >
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="flex-1 overflow-auto p-3">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {result.columns.map((col) => (
              <div key={col} className="border border-gray-200 rounded p-2">
                <div className="text-xs font-semibold text-gray-700 truncate mb-1" title={col}>
                  {col}
                </div>
                <ColumnProfile data={data} column={col} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
