"use client";

import { useState, useCallback, useRef } from "react";
import { ChevronDown, ChevronRight, Upload } from "lucide-react";
import { TOOLS, TOOL_CATEGORIES } from "@/lib/toolRegistry";
import { api } from "@/lib/api";

export function ToolPalette() {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(TOOL_CATEGORIES.map((c) => c.id))
  );
  const fileInputRef = useRef<HTMLInputElement>(null);

  const toggleCategory = (id: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleUpload = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      await api.uploadFile(file);
      alert(`Uploaded: ${file.name}`);
    } catch (err) {
      alert(`Upload failed: ${err}`);
    }
    if (fileInputRef.current) fileInputRef.current.value = "";
  }, []);

  return (
    <div className="w-56 border-r border-gray-200 bg-white flex flex-col h-full">
      <div className="p-3 border-b border-gray-200">
        <h2 className="text-sm font-semibold text-gray-700">Tools</h2>
      </div>

      {/* File upload */}
      <div className="p-2 border-b border-gray-200">
        <button
          onClick={() => fileInputRef.current?.click()}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded"
        >
          <Upload size={16} />
          Upload Data File
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls,.json"
          className="hidden"
          onChange={handleUpload}
        />
      </div>

      {/* Tool categories */}
      <div className="flex-1 overflow-y-auto p-2">
        {TOOL_CATEGORIES.map((category) => {
          const categoryTools = TOOLS.filter((t) => t.category === category.id);
          const isExpanded = expandedCategories.has(category.id);

          return (
            <div key={category.id} className="mb-1">
              <button
                onClick={() => toggleCategory(category.id)}
                className="w-full flex items-center gap-1 px-2 py-1.5 text-xs font-semibold text-gray-500 uppercase hover:bg-gray-100 rounded"
              >
                {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                {category.label}
              </button>

              {isExpanded && (
                <div className="ml-2">
                  {categoryTools.map((tool) => (
                    <div
                      key={tool.type}
                      draggable
                      onDragStart={(e) => {
                        e.dataTransfer.setData("application/tool-type", tool.type);
                        e.dataTransfer.effectAllowed = "move";
                      }}
                      className="flex items-center gap-2 px-2 py-1.5 text-sm text-gray-700 hover:bg-gray-100 rounded cursor-grab active:cursor-grabbing"
                    >
                      <div
                        className="w-5 h-5 rounded flex items-center justify-center flex-shrink-0"
                        style={{ backgroundColor: `${tool.color}20`, color: tool.color }}
                      >
                        <tool.icon size={13} />
                      </div>
                      {tool.label}
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
