"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  BeakerIcon,
  SparklesIcon,
  ChatBubbleLeftRightIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  PaperAirplaneIcon,
} from "@heroicons/react/24/outline";
import { brandDnaApi, type BrandProfile, type BrandBriefUpdate } from "@/lib/brand-dna-api";

export function BrandDnaDashboard() {
  const queryClient = useQueryClient();
  const [chatMessage, setChatMessage] = useState("");
  const [chatHistory, setChatHistory] = useState<Array<{ role: string; text: string }>>([]);

  const { data: profileData, isLoading } = useQuery({
    queryKey: ["brand-dna-profile"],
    queryFn: brandDnaApi.getProfile,
  });

  const profile = profileData?.profile;

  const [brief, setBrief] = useState<BrandBriefUpdate>({
    voice: "",
    pillars: [],
    dos: [],
    donts: [],
  });

  // Sync brief state when profile loads
  const briefLoaded = profile && brief.voice === "";
  if (briefLoaded) {
    setBrief({
      voice: profile.voice || "",
      pillars: profile.pillars || [],
      dos: profile.dos || [],
      donts: profile.donts || [],
    });
  }

  const saveBrief = useMutation({
    mutationFn: brandDnaApi.updateBrief,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["brand-dna-profile"] }),
  });

  const analyze = useMutation({
    mutationFn: brandDnaApi.analyzePosts,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["brand-dna-profile"] }),
  });

  const chatMutation = useMutation({
    mutationFn: brandDnaApi.chat,
    onSuccess: (data) => {
      setChatHistory(prev => [...prev, { role: "assistant", text: data.response || data.message || JSON.stringify(data) }]);
    },
  });

  const resetMutation = useMutation({
    mutationFn: brandDnaApi.reset,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["brand-dna-profile"] });
      setBrief({ voice: "", pillars: [], dos: [], donts: [] });
    },
  });

  function handleSendChat() {
    if (!chatMessage.trim()) return;
    setChatHistory(prev => [...prev, { role: "user", text: chatMessage }]);
    chatMutation.mutate({ message: chatMessage });
    setChatMessage("");
  }

  function handlePillarChange(index: number, value: string) {
    const updated = [...brief.pillars];
    updated[index] = value;
    setBrief({ ...brief, pillars: updated });
  }

  function handleListChange(field: "dos" | "donts", index: number, value: string) {
    const updated = [...brief[field]];
    updated[index] = value;
    setBrief({ ...brief, [field]: updated });
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <ArrowPathIcon className="h-8 w-8 animate-spin text-purple-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Brand DNA Engine</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Learn your style. Lock your brand. Every post sounds like you.</p>
        </div>
        <button
          onClick={() => resetMutation.mutate()}
          className="px-4 py-2 text-sm text-red-600 border border-red-300 rounded-lg hover:bg-red-50 dark:text-red-400 dark:border-red-700 dark:hover:bg-red-900/20"
        >
          Reset Profile
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <KpiCard
          icon={BeakerIcon}
          label="Confidence"
          value={`${Math.round((profile?.confidence || 0) * 100)}%`}
          color="purple"
        />
        <KpiCard
          icon={SparklesIcon}
          label="Brand Pillars"
          value={String(profile?.pillars?.length || 0)}
          color="blue"
        />
        <KpiCard
          icon={CheckCircleIcon}
          label="Style Lock"
          value={(profile?.confidence || 0) >= 0.8 ? "Active" : "Learning"}
          color="green"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Brand Brief Editor */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Brand Brief</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Brand Voice</label>
              <textarea
                value={brief.voice}
                onChange={(e) => setBrief({ ...brief, voice: e.target.value })}
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500"
                rows={3}
                placeholder="Describe your brand voice (e.g., motivational, raw, high-energy gym culture...)"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Content Pillars</label>
              {(brief.pillars.length > 0 ? brief.pillars : [""]).map((p, i) => (
                <input
                  key={i}
                  value={p}
                  onChange={(e) => handlePillarChange(i, e.target.value)}
                  className="w-full mb-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white"
                  placeholder={`Pillar ${i + 1}`}
                />
              ))}
              <button
                onClick={() => setBrief({ ...brief, pillars: [...brief.pillars, ""] })}
                className="text-xs text-purple-600 dark:text-purple-400 hover:underline"
              >
                + Add pillar
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-green-700 dark:text-green-400 mb-1">Do&apos;s</label>
                {(brief.dos.length > 0 ? brief.dos : [""]).map((d, i) => (
                  <input
                    key={i}
                    value={d}
                    onChange={(e) => handleListChange("dos", i, e.target.value)}
                    className="w-full mb-2 rounded-lg border border-green-300 dark:border-green-700 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white"
                    placeholder={`Do ${i + 1}`}
                  />
                ))}
                <button
                  onClick={() => setBrief({ ...brief, dos: [...brief.dos, ""] })}
                  className="text-xs text-green-600 dark:text-green-400 hover:underline"
                >
                  + Add
                </button>
              </div>
              <div>
                <label className="block text-sm font-medium text-red-700 dark:text-red-400 mb-1">Don&apos;ts</label>
                {(brief.donts.length > 0 ? brief.donts : [""]).map((d, i) => (
                  <input
                    key={i}
                    value={d}
                    onChange={(e) => handleListChange("donts", i, e.target.value)}
                    className="w-full mb-2 rounded-lg border border-red-300 dark:border-red-700 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white"
                    placeholder={`Don't ${i + 1}`}
                  />
                ))}
                <button
                  onClick={() => setBrief({ ...brief, donts: [...brief.donts, ""] })}
                  className="text-xs text-red-600 dark:text-red-400 hover:underline"
                >
                  + Add
                </button>
              </div>
            </div>

            <button
              onClick={() => saveBrief.mutate(brief)}
              disabled={saveBrief.isPending}
              className="w-full py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 disabled:opacity-50"
            >
              {saveBrief.isPending ? "Saving..." : "Save Brand Brief"}
            </button>
          </div>
        </div>

        {/* AI Chat & Analyzer */}
        <div className="space-y-6">
          {/* Analyzer */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-3">AI Style Analyzer</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Feed your existing posts to the AI and it will learn your unique style.
            </p>
            <button
              onClick={() => analyze.mutate({ posts: [{ text: "Sample post for analysis", engagement: 100, platform: "facebook" }] })}
              disabled={analyze.isPending}
              className="w-full py-2 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-cyan-700 disabled:opacity-50"
            >
              {analyze.isPending ? "Analyzing..." : "Analyze My Posts"}
            </button>
            {analyze.isSuccess && (
              <p className="mt-2 text-sm text-green-600 dark:text-green-400">Analysis complete — profile updated!</p>
            )}
          </div>

          {/* Brand Direction Chat */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 flex flex-col" style={{ minHeight: "320px" }}>
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <ChatBubbleLeftRightIcon className="h-5 w-5" /> Brand Direction Chat
            </h2>
            <div className="flex-1 overflow-y-auto space-y-3 mb-4 max-h-48">
              {chatHistory.length === 0 && (
                <p className="text-sm text-gray-400">Ask the AI to refine your brand direction...</p>
              )}
              {chatHistory.map((msg, i) => (
                <div key={i} className={`text-sm p-3 rounded-lg ${msg.role === "user" ? "bg-purple-100 dark:bg-purple-900/30 ml-8" : "bg-gray-100 dark:bg-gray-700 mr-8"}`}>
                  <span className="font-medium text-xs text-gray-500 dark:text-gray-400">{msg.role === "user" ? "You" : "AI"}</span>
                  <p className="text-gray-900 dark:text-white mt-1">{msg.text}</p>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSendChat()}
                className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white"
                placeholder="e.g. Make my voice more aggressive and motivational"
              />
              <button
                onClick={handleSendChat}
                disabled={chatMutation.isPending}
                className="p-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
              >
                <PaperAirplaneIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function KpiCard({ icon: Icon, label, value, color }: { icon: React.ComponentType<{ className?: string }>; label: string; value: string; color: "purple" | "blue" | "green" }) {
  const colors = {
    purple: "from-purple-600 to-purple-400",
    blue: "from-blue-600 to-blue-400",
    green: "from-green-600 to-green-400",
  };
  return (
    <div className={`bg-gradient-to-br ${colors[color]} rounded-2xl p-6 text-white shadow-lg`}>
      <Icon className="h-8 w-8 mb-2 opacity-80" />
      <p className="text-sm opacity-80">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  );
}
