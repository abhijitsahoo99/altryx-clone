"use client";

import { useMemo } from "react";
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  createColumnHelper,
} from "@tanstack/react-table";
import { useWorkflowStore } from "@/hooks/useWorkflow";

export function DataPreview() {
  const { selectedNodeId, nodeResults } = useWorkflowStore();
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
      <div className="h-48 border-t border-gray-200 bg-white flex items-center justify-center text-sm text-gray-400">
        Select a node to preview its data. Run the workflow first.
      </div>
    );
  }

  if (result.status === "error") {
    return (
      <div className="h-48 border-t border-gray-200 bg-white p-4">
        <div className="text-sm text-red-600 font-medium">Error</div>
        <div className="text-sm text-red-500 mt-1">{result.error}</div>
      </div>
    );
  }

  return (
    <div className="h-48 border-t border-gray-200 bg-white flex flex-col">
      <div className="px-4 py-2 border-b border-gray-100 flex items-center justify-between">
        <span className="text-xs font-medium text-gray-500">
          {result.row_count} rows x {result.columns.length} columns
        </span>
      </div>
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
    </div>
  );
}
