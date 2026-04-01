"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ChatBubbleBottomCenterTextIcon,
  EnvelopeIcon,
  FlagIcon,
  FaceSmileIcon,
  ArrowPathIcon,
  PlusIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import { engagementApi, type EngagementConfig, type EngagementRule } from "@/lib/engagement-api";

export function EngagementDashboard() {
  const queryClient = useQueryClient();
  const [newKeyword, setNewKeyword] = useState("");
  const [newTemplate, setNewTemplate] = useState("");

  const { data: configData } = useQuery({
    queryKey: ["engagement-config"],
    queryFn: engagementApi.getConfig,
  });

  const { data: statsData } = useQuery({
    queryKey: ["engagement-stats"],
    queryFn: engagementApi.getStats,
  });

  const { data: rulesData } = useQuery({
    queryKey: ["engagement-rules"],
    queryFn: engagementApi.getRules,
  });

  const { data: historyData } = useQuery({
    queryKey: ["engagement-history"],
    queryFn: () => engagementApi.getHistory(20),
  });

  const { data: flaggedData } = useQuery({
    queryKey: ["engagement-flagged"],
    queryFn: () => engagementApi.getFlagged(20),
  });

  const updateConfig = useMutation({
    mutationFn: engagementApi.updateConfig,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["engagement-config"] }),
  });

  const addRule = useMutation({
    mutationFn: engagementApi.addRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["engagement-rules"] });
      setNewKeyword("");
      setNewTemplate("");
    },
  });

  const toggleRule = useMutation({
    mutationFn: engagementApi.toggleRule,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["engagement-rules"] }),
  });

  const deleteRule = useMutation({
    mutationFn: engagementApi.deleteRule,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["engagement-rules"] }),
  });

  const dismissFlag = useMutation({
    mutationFn: engagementApi.dismissFlagged,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["engagement-flagged"] }),
  });

  const config = configData?.config;
  const stats = statsData?.stats;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Engagement Autopilot</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">Auto-reply to comments, welcome new followers, and flag negativity.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiCard icon={ChatBubbleBottomCenterTextIcon} label="Replies Sent" value={String(stats?.total_replies || 0)} color="blue" />
        <KpiCard icon={EnvelopeIcon} label="Welcome DMs" value={String(stats?.total_dms || 0)} color="green" />
        <KpiCard icon={FlagIcon} label="Flagged" value={String(stats?.total_flagged || 0)} color="red" />
        <KpiCard icon={FaceSmileIcon} label="Avg Sentiment" value={stats?.avg_sentiment ? `${(stats.avg_sentiment * 100).toFixed(0)}%` : "—"} color="purple" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Config Toggles */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Autopilot Settings</h2>
          <div className="space-y-4">
            <ToggleRow
              label="Auto-Reply to Comments"
              enabled={config?.auto_reply_enabled || false}
              onChange={(v) => updateConfig.mutate({ auto_reply_enabled: v })}
            />
            <ToggleRow
              label="Welcome DM for New Followers"
              enabled={config?.auto_dm_enabled || false}
              onChange={(v) => updateConfig.mutate({ auto_dm_enabled: v })}
            />
            <ToggleRow
              label="Auto-Like Positive Comments"
              enabled={config?.auto_like_enabled || false}
              onChange={(v) => updateConfig.mutate({ auto_like_enabled: v })}
            />
          </div>
        </div>

        {/* Custom Rules */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Custom Rules</h2>
          <div className="space-y-3 mb-4 max-h-52 overflow-y-auto">
            {(rulesData?.rules || []).map((rule) => (
              <RuleItem
                key={rule.id}
                rule={rule}
                onToggle={() => toggleRule.mutate(rule.id)}
                onDelete={() => deleteRule.mutate(rule.id)}
              />
            ))}
            {(rulesData?.rules || []).length === 0 && (
              <p className="text-sm text-gray-400">No custom rules yet.</p>
            )}
          </div>
          <div className="border-t border-gray-200 dark:border-gray-700 pt-4 space-y-2">
            <input
              value={newKeyword}
              onChange={(e) => setNewKeyword(e.target.value)}
              className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white"
              placeholder="Keyword trigger (e.g., pricing, hours)"
            />
            <input
              value={newTemplate}
              onChange={(e) => setNewTemplate(e.target.value)}
              className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white"
              placeholder="Response template"
            />
            <button
              onClick={() => newKeyword && newTemplate && addRule.mutate({ keyword: newKeyword, response_template: newTemplate })}
              disabled={!newKeyword || !newTemplate || addRule.isPending}
              className="w-full py-2 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-cyan-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <PlusIcon className="h-4 w-4" /> Add Rule
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Flagged Comments */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <FlagIcon className="h-5 w-5 text-red-500" /> Flagged Comments
          </h2>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {(flaggedData?.flagged || []).map((item) => (
              <div key={item.id} className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                <p className="text-sm text-gray-900 dark:text-white">{item.text}</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-red-600 dark:text-red-400">{item.reason}</span>
                  <button
                    onClick={() => dismissFlag.mutate(item.id)}
                    className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            ))}
            {(flaggedData?.flagged || []).length === 0 && <p className="text-sm text-gray-400">No flagged comments.</p>}
          </div>
        </div>

        {/* Recent History */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Recent Activity</h2>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {(historyData?.history || []).map((item) => (
              <div key={item.id} className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full">{item.type}</span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">{new Date(item.timestamp).toLocaleDateString()}</span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-300 truncate">{item.comment_text}</p>
                <p className="text-sm text-green-600 dark:text-green-400 truncate mt-1">→ {item.reply_text}</p>
              </div>
            ))}
            {(historyData?.history || []).length === 0 && <p className="text-sm text-gray-400">No activity yet.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

function ToggleRow({ label, enabled, onChange }: { label: string; enabled: boolean; onChange: (v: boolean) => void }) {
  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
      <span className="text-sm font-medium text-gray-900 dark:text-white">{label}</span>
      <button
        onClick={() => onChange(!enabled)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${enabled ? "bg-green-500" : "bg-gray-300 dark:bg-gray-600"}`}
      >
        <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${enabled ? "translate-x-6" : "translate-x-1"}`} />
      </button>
    </div>
  );
}

function RuleItem({ rule, onToggle, onDelete }: { rule: EngagementRule; onToggle: () => void; onDelete: () => void }) {
  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
      <button
        onClick={onToggle}
        className={`flex-shrink-0 h-5 w-5 rounded border-2 ${rule.enabled ? "bg-green-500 border-green-500" : "border-gray-300 dark:border-gray-600"}`}
      />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">"{rule.keyword}"</p>
        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{rule.response_template}</p>
      </div>
      <button onClick={onDelete} className="flex-shrink-0 p-1 text-gray-400 hover:text-red-500">
        <TrashIcon className="h-4 w-4" />
      </button>
    </div>
  );
}

function KpiCard({ icon: Icon, label, value, color }: { icon: React.ComponentType<{ className?: string }>; label: string; value: string; color: "blue" | "green" | "red" | "purple" }) {
  const colors = {
    blue: "from-blue-600 to-blue-400",
    green: "from-green-600 to-green-400",
    red: "from-red-600 to-red-400",
    purple: "from-purple-600 to-purple-400",
  };
  return (
    <div className={`bg-gradient-to-br ${colors[color]} rounded-2xl p-5 text-white shadow-lg`}>
      <Icon className="h-7 w-7 mb-2 opacity-80" />
      <p className="text-xs opacity-80">{label}</p>
      <p className="text-xl font-bold mt-1">{value}</p>
    </div>
  );
}
