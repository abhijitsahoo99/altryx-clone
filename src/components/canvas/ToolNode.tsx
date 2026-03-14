"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import { getToolInfo } from "@/lib/toolRegistry";
import { useWorkflowStore } from "@/hooks/useWorkflow";

function ToolNodeComponent({ id, data, selected }: NodeProps) {
  const toolType = (data as Record<string, unknown>).toolType as string;
  const toolInfo = getToolInfo(toolType);
  const nodeResult = useWorkflowStore((s) => s.nodeResults[id]);

  const label = toolInfo?.label || toolType;
  const Icon = toolInfo?.icon;
  const color = toolInfo?.color || "#6b7280";
  const inputs = toolInfo?.inputs || ["input"];
  const outputs = toolInfo?.outputs || ["output"];

  let statusColor = "border-gray-300";
  if (nodeResult?.status === "completed") statusColor = "border-green-500";
  if (nodeResult?.status === "error") statusColor = "border-red-500";

  return (
    <div
      className={`bg-white rounded-lg shadow-md border-2 ${statusColor} min-w-[140px] ${selected ? "ring-2 ring-blue-500" : ""}`}
    >
      {/* Input handles */}
      {inputs.map((handle, i) => (
        <Handle
          key={handle}
          type="target"
          position={Position.Left}
          id={handle}
          style={{
            top: inputs.length === 1 ? "50%" : `${((i + 1) / (inputs.length + 1)) * 100}%`,
            background: color,
            width: 10,
            height: 10,
          }}
        />
      ))}

      {/* Node body */}
      <div className="flex items-center gap-2 px-3 py-2">
        <div
          className="w-8 h-8 rounded flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: `${color}20`, color }}
        >
          {Icon && <Icon size={18} />}
        </div>
        <div className="min-w-0">
          <div className="text-sm font-medium text-gray-800 truncate">{label}</div>
          {nodeResult && (
            <div className="text-xs text-gray-500">
              {nodeResult.status === "completed"
                ? `${nodeResult.row_count} rows`
                : nodeResult.error?.slice(0, 30)}
            </div>
          )}
        </div>
      </div>

      {/* Input handle labels for multi-input nodes */}
      {inputs.length > 1 && (
        <div className="absolute left-0 top-0 h-full flex flex-col justify-around pl-0 pointer-events-none">
          {inputs.map((handle) => (
            <span key={handle} className="text-[10px] text-gray-400 -ml-8">
              {handle}
            </span>
          ))}
        </div>
      )}

      {/* Output handles */}
      {outputs.map((handle, i) => (
        <Handle
          key={handle}
          type="source"
          position={Position.Right}
          id={handle}
          style={{
            top: outputs.length === 1 ? "50%" : `${((i + 1) / (outputs.length + 1)) * 100}%`,
            background: handle === "true" ? "#22c55e" : handle === "false" ? "#ef4444" : color,
            width: 10,
            height: 10,
          }}
        />
      ))}

      {/* Output handle labels for multi-output nodes */}
      {outputs.length > 1 && (
        <div className="absolute right-0 top-0 h-full flex flex-col justify-around pr-0 pointer-events-none">
          {outputs.map((handle) => (
            <span key={handle} className="text-[10px] text-gray-400 -mr-4" style={{ marginRight: "-1.5rem" }}>
              {handle === "true" ? "T" : handle === "false" ? "F" : handle}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export const ToolNode = memo(ToolNodeComponent);
