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
  Rows3,
  PaintBucket,
  FlipVertical,
  SplitSquareHorizontal,
  Regex,
  Table2,
  Replace,
  PanelRightOpen,
  Search,
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
  { id: "Parse", label: "Parse", color: "#06b6d4" },
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
  { type: "multi_row", label: "Multi-Row", category: "Preparation", icon: Rows3, color: "#8b5cf6", inputs: ["input"], outputs: ["output"] },
  { type: "imputation", label: "Imputation", category: "Preparation", icon: PaintBucket, color: "#8b5cf6", inputs: ["input"], outputs: ["output"] },
  { type: "transpose", label: "Transpose", category: "Preparation", icon: FlipVertical, color: "#8b5cf6", inputs: ["input"], outputs: ["output"] },
  { type: "cross_tab", label: "Cross Tab", category: "Preparation", icon: Table2, color: "#8b5cf6", inputs: ["input"], outputs: ["output"] },
  { type: "find_replace", label: "Find Replace", category: "Preparation", icon: Replace, color: "#8b5cf6", inputs: ["input"], outputs: ["output"] },

  // Parse
  { type: "text_to_columns", label: "Text to Columns", category: "Parse", icon: SplitSquareHorizontal, color: "#06b6d4", inputs: ["input"], outputs: ["output"] },
  { type: "regex", label: "Regex", category: "Parse", icon: Regex, color: "#06b6d4", inputs: ["input"], outputs: ["output"] },

  // Join
  { type: "join", label: "Join", category: "Join", icon: GitMerge, color: "#f59e0b", inputs: ["left", "right"], outputs: ["output"] },
  { type: "union", label: "Union", category: "Join", icon: Layers, color: "#f59e0b", inputs: ["input"], outputs: ["output"] },
  { type: "append", label: "Append Fields", category: "Join", icon: PanelRightOpen, color: "#f59e0b", inputs: ["target", "source"], outputs: ["output"] },
  { type: "fuzzy_match", label: "Fuzzy Match", category: "Join", icon: Search, color: "#f59e0b", inputs: ["left", "right"], outputs: ["output"] },
];

export function getToolInfo(toolType: string): ToolInfo | undefined {
  return TOOLS.find((t) => t.type === toolType);
}
