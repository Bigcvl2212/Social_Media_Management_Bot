"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowPathIcon,
  BoltIcon,
  DocumentTextIcon,
  TrashIcon,
  PlusIcon,
  SparklesIcon,
  CheckIcon,
  ClipboardDocumentIcon,
} from "@heroicons/react/24/outline";
import { remixApi, type OriginalPost, type RemixFormat, type Remix } from "@/lib/remix-api";

export function RemixDashboard() {
  const queryClient = useQueryClient();
  const [selectedOriginal, setSelectedOriginal] = useState<string | null>(null);
  const [selectedFormats, setSelectedFormats] = useState<string[]>([]);
  const [newPostText, setNewPostText] = useState("");
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const { data: formatsData } = useQuery({
    queryKey: ["remix-formats"],
    queryFn: remixApi.getFormats,
  });

  const { data: originalsData } = useQuery({
    queryKey: ["remix-originals"],
    queryFn: remixApi.listOriginals,
  });

  const { data: remixesData } = useQuery({
    queryKey: ["remix-remixes"],
    queryFn: () => remixApi.listRemixes(),
  });

  const addOriginal = useMutation({
    mutationFn: remixApi.addOriginal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["remix-originals"] });
      setNewPostText("");
    },
  });

  const deleteOriginal = useMutation({
    mutationFn: remixApi.deleteOriginal,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["remix-originals"] }),
  });

  const remixSingle = useMutation({
    mutationFn: remixApi.remix,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["remix-remixes"] }),
  });

  const batchRemix = useMutation({
    mutationFn: remixApi.batchRemix,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["remix-remixes"] }),
  });

  const deleteRemix = useMutation({
    mutationFn: remixApi.deleteRemix,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["remix-remixes"] }),
  });

  function toggleFormat(formatId: string) {
    setSelectedFormats(prev =>
      prev.includes(formatId) ? prev.filter(f => f !== formatId) : [...prev, formatId]
    );
  }

  function handleBatchRemix() {
    if (selectedFormats.length === 0) return;
    batchRemix.mutate({ formats: selectedFormats, top_n: 5 });
  }

  function handleSingleRemix(originalId: string, format: string) {
    remixSingle.mutate({ original_id: originalId, target_format: format });
  }

  function handleCopy(id: string, text: string) {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  }

  const originals = originalsData?.originals || [];
  const formats = formatsData?.formats || [];
  const remixes = remixesData?.remixes || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Remix Studio</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">Turn your top-performing posts into new formats. One hit becomes many.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <KpiCard icon={DocumentTextIcon} label="Top Posts" value={String(originals.length)} color="blue" />
        <KpiCard icon={ArrowPathIcon} label="Remixes Created" value={String(remixes.length)} color="purple" />
        <KpiCard icon={BoltIcon} label="Formats Available" value={String(formats.length)} color="green" />
      </div>

      {/* Add Original Post */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-3">Add Top-Performing Post</h2>
        <div className="flex gap-3">
          <textarea
            value={newPostText}
            onChange={(e) => setNewPostText(e.target.value)}
            className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white"
            rows={3}
            placeholder="Paste your top post text here..."
          />
          <button
            onClick={() => newPostText && addOriginal.mutate({ post_text: newPostText })}
            disabled={!newPostText || addOriginal.isPending}
            className="self-end px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-cyan-700 disabled:opacity-50 flex items-center gap-2"
          >
            <PlusIcon className="h-4 w-4" /> Add
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Originals Library */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Your Top Posts</h2>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {originals.map((post) => (
              <div
                key={post.id}
                onClick={() => setSelectedOriginal(post.id)}
                className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                  selectedOriginal === post.id
                    ? "border-purple-500 bg-purple-50 dark:bg-purple-900/20"
                    : "border-gray-200 dark:border-gray-700 hover:border-purple-300"
                }`}
              >
                <p className="text-sm text-gray-900 dark:text-white line-clamp-2">{post.post_text}</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-gray-500 dark:text-gray-400">{post.platform || "unknown"}</span>
                  <button
                    onClick={(e) => { e.stopPropagation(); deleteOriginal.mutate(post.id); }}
                    className="text-gray-400 hover:text-red-500"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
            {originals.length === 0 && <p className="text-sm text-gray-400">Add your top posts to start remixing.</p>}
          </div>
        </div>

        {/* Format Selector */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Remix Formats</h2>
          <div className="grid grid-cols-3 gap-3 mb-4">
            {formats.map((fmt) => (
              <button
                key={fmt.id}
                onClick={() => toggleFormat(fmt.id)}
                className={`p-3 rounded-xl border text-center transition-all ${
                  selectedFormats.includes(fmt.id)
                    ? "border-purple-500 bg-purple-50 dark:bg-purple-900/20 ring-2 ring-purple-500"
                    : "border-gray-200 dark:border-gray-700 hover:border-purple-300"
                }`}
              >
                <span className="text-2xl">{fmt.icon || "🔄"}</span>
                <p className="text-xs font-medium text-gray-900 dark:text-white mt-1">{fmt.name}</p>
              </button>
            ))}
          </div>
          <button
            onClick={handleBatchRemix}
            disabled={selectedFormats.length === 0 || batchRemix.isPending}
            className="w-full py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <SparklesIcon className="h-5 w-5" />
            {batchRemix.isPending ? "Remixing..." : `Batch Remix (${selectedFormats.length} formats)`}
          </button>
        </div>
      </div>

      {/* Generated Remixes */}
      {remixes.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Generated Remixes</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {remixes.map((remix) => (
              <div key={remix.id} className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium px-2 py-0.5 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-full">
                    {remix.target_format}
                  </span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleCopy(remix.id, remix.remixed_text)}
                      className="p-1 text-gray-400 hover:text-blue-500"
                    >
                      {copiedId === remix.id ? <CheckIcon className="h-4 w-4 text-green-500" /> : <ClipboardDocumentIcon className="h-4 w-4" />}
                    </button>
                    <button
                      onClick={() => deleteRemix.mutate(remix.id)}
                      className="p-1 text-gray-400 hover:text-red-500"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                <p className="text-sm text-gray-900 dark:text-white whitespace-pre-wrap">{remix.remixed_text}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function KpiCard({ icon: Icon, label, value, color }: { icon: React.ComponentType<{ className?: string }>; label: string; value: string; color: "blue" | "purple" | "green" }) {
  const colors = {
    blue: "from-blue-600 to-blue-400",
    purple: "from-purple-600 to-purple-400",
    green: "from-green-600 to-green-400",
  };
  return (
    <div className={`bg-gradient-to-br ${colors[color]} rounded-2xl p-5 text-white shadow-lg`}>
      <Icon className="h-7 w-7 mb-2 opacity-80" />
      <p className="text-xs opacity-80">{label}</p>
      <p className="text-xl font-bold mt-1">{value}</p>
    </div>
  );
}
