"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Plus, Trash2, FileText } from "lucide-react";
import { api } from "@/lib/api";
import type { Workflow } from "@/lib/types";

export function WorkflowList() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    api.listWorkflows().then(setWorkflows).catch(console.error).finally(() => setLoading(false));
  }, []);

  const handleCreate = async () => {
    const wf = await api.createWorkflow({ name: "Untitled Workflow" });
    router.push(`/workflows/${wf.id}`);
  };

  const handleDelete = async (id: string) => {
    await api.deleteWorkflow(id);
    setWorkflows((prev) => prev.filter((w) => w.id !== id));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">Loading...</div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto py-12 px-4">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-gray-800">Workflows</h1>
        <button
          onClick={handleCreate}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
        >
          <Plus size={18} />
          New Workflow
        </button>
      </div>

      {workflows.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <FileText size={48} className="mx-auto mb-4 opacity-50" />
          <p>No workflows yet. Create one to get started.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {workflows.map((wf) => (
            <div
              key={wf.id}
              className="flex items-center justify-between p-4 bg-white rounded-lg border border-gray-200 hover:border-blue-300 cursor-pointer transition-colors"
              onClick={() => router.push(`/workflows/${wf.id}`)}
            >
              <div>
                <div className="font-medium text-gray-800">{wf.name}</div>
                <div className="text-xs text-gray-400 mt-1">
                  Updated {new Date(wf.updated_at).toLocaleString()}
                </div>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(wf.id);
                }}
                className="text-gray-400 hover:text-red-500 p-1"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
