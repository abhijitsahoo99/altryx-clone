import {
  Database,
  FileInput,
  FileOutput,
  Filter,
  Columns,
  Calculator,
  ArrowUpDown,
  Dice5,
  Fingerprint,
  BarChart3,
  Sparkles,
  GitMerge,
  Layers,
  type LucideIcon,
} from "lucide-react";

export interface ToolInfo {
  type: string;
  label: string;
  category: string;
  icon: LucideIcon;
  color: string;
  inputs: string[];
  outputs: string[];
}

export const TOOL_CATEGORIES = [
  { id: "IO", label: "Input / Output", color: "#3b82f6" },
  { id: "Preparation", label: "Preparation", color: "#8b5cf6" },
  { id: "Join", label: "Join", color: "#f59e0b" },
] as const;

export const TOOLS: ToolInfo[] = [
  // IO
  { type: "input_data", label: "Input Data", category: "IO", icon: FileInput, color: "#3b82f6", inputs: [], outputs: ["output"] },
  { type: "output_data", label: "Output Data", category: "IO", icon: FileOutput, color: "#3b82f6", inputs: ["input"], outputs: ["output"] },

  // Preparation
  { type: "filter", label: "Filter", category: "Preparation", icon: Filter, color: "#8b5cf6", inputs: ["input"], outputs: ["output"] },
  { type: "select", label: "Select", category: "Preparation", icon: Columns, color: "#8b5cf6", inputs: ["input"], outputs: ["output"] },
  { type: "formula", label: "Formula", category: "Preparation", icon: Calculator, color: "#8b5cf6", inputs: ["input"], outputs: ["output"] },
  { type: "sort", label: "Sort", category: "Preparation", icon: ArrowUpDown, color: "#8b5cf6", inputs: ["input"], outputs: ["output"] },
  { type: "sample", label: "Sample", category: "Preparation", icon: Dice5, color: "#8b5cf6", inputs: ["input"], outputs: ["output"] },
  { type: "unique", label: "Unique", category: "Preparation", icon: Fingerprint, color: "#8b5cf6", inputs: ["input"], outputs: ["output"] },
  { type: "summarize", label: "Summarize", category: "Preparation", icon: BarChart3, color: "#8b5cf6", inputs: ["input"], outputs: ["output"] },
  { type: "data_cleanse", label: "Data Cleanse", category: "Preparation", icon: Sparkles, color: "#8b5cf6", inputs: ["input"], outputs: ["output"] },

  // Join
  { type: "join", label: "Join", category: "Join", icon: GitMerge, color: "#f59e0b", inputs: ["left", "right"], outputs: ["output"] },
  { type: "union", label: "Union", category: "Join", icon: Layers, color: "#f59e0b", inputs: ["input"], outputs: ["output"] },
];

export function getToolInfo(toolType: string): ToolInfo | undefined {
  return TOOLS.find((t) => t.type === toolType);
}
