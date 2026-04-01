"use client";

import { useState, useEffect, useCallback } from "react";
import {
  PlayIcon,
  ClockIcon,
  ChatBubbleLeftRightIcon,
  ShieldCheckIcon,
  SparklesIcon,
  ArrowPathIcon,
  PhotoIcon,
  DocumentTextIcon,
  VideoCameraIcon,
  PlusIcon,
  TrashIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import {
  getAutopilotStatus,
  getAutopilotConfig,
  toggleAutopilot,
  updateAutopilotConfig,
  triggerAutopilotPost,
} from "@/lib/automation-api";

// ── Types ───────────────────────────────────────────────
interface PostingWindow {
  hour: number;
  minute: number;
  label: string;
}

interface AutopilotConfig {
  posts_per_day: number;
  posting_windows: PostingWindow[];
  daily_themes: Record<string, string[]>;
  styles: string[];
  format_weights: Record<string, number>;
  enabled: boolean;
}

interface AutopilotStatusData {
  running: boolean;
  enabled: boolean;
  posts_today: number;
  next_post_at: string | null;
  last_post_at: string | null;
}

type SubTab = "autopilot" | "comments" | "moderation";

const DAY_NAMES: Record<string, string> = {
  "0": "Monday",
  "1": "Tuesday",
  "2": "Wednesday",
  "3": "Thursday",
  "4": "Friday",
  "5": "Saturday",
  "6": "Sunday",
};

// ── Main Export ─────────────────────────────────────────
export function AutomationsPanel() {
  const [subTab, setSubTab] = useState<SubTab>("autopilot");
  const [status, setStatus] = useState<AutopilotStatusData | null>(null);
  const [config, setConfig] = useState<AutopilotConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<{ type: "success" | "error"; msg: string } | null>(null);
  const [triggerTopic, setTriggerTopic] = useState("");
  const [triggering, setTriggering] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [s, c] = await Promise.all([getAutopilotStatus(), getAutopilotConfig()]);
      setStatus(s);
      setConfig(c);
    } catch {
      setToast({ type: "error", msg: "Failed to load autopilot data — is the backend running?" });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(null), 4000);
      return () => clearTimeout(t);
    }
  }, [toast]);

  const handleToggle = async () => {
    if (!status) return;
    try {
      const res = await toggleAutopilot(!status.enabled);
      setStatus((prev) => (prev ? { ...prev, enabled: res.enabled } : prev));
      setToast({ type: "success", msg: res.enabled ? "Autopilot enabled" : "Autopilot paused" });
    } catch {
      setToast({ type: "error", msg: "Failed to toggle autopilot" });
    }
  };

  const handleSaveConfig = async (updates: Partial<AutopilotConfig>) => {
    setSaving(true);
    try {
      await updateAutopilotConfig(updates);
      await fetchData();
      setToast({ type: "success", msg: "Configuration saved" });
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Save failed";
      setToast({ type: "error", msg });
    } finally {
      setSaving(false);
    }
  };

  const handleTrigger = async () => {
    setTriggering(true);
    try {
      await triggerAutopilotPost(triggerTopic || undefined);
      setTriggerTopic("");
      setToast({ type: "success", msg: "Post triggered! Check your Facebook page." });
      setTimeout(fetchData, 5000);
    } catch {
      setToast({ type: "error", msg: "Failed to trigger post" });
    } finally {
      setTriggering(false);
    }
  };

  const subTabs = [
    { id: "autopilot" as SubTab, label: "Content Autopilot", icon: SparklesIcon },
    { id: "comments" as SubTab, label: "Comment Monitor", icon: ChatBubbleLeftRightIcon },
    { id: "moderation" as SubTab, label: "Moderation", icon: ShieldCheckIcon },
  ];

  return (
    <div className="space-y-6">
      {/* Sub-tab navigation */}
      <div className="flex space-x-4 overflow-x-auto">
        {subTabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = subTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setSubTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-colors whitespace-nowrap ${
                isActive
                  ? "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300"
                  : "bg-gray-100 text-gray-600 dark:bg-gray-700/50 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700"
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Toast */}
      {toast && (
        <div
          className={`flex items-center gap-2 p-4 rounded-xl text-sm font-medium ${
            toast.type === "success"
              ? "bg-green-50 text-green-800 dark:bg-green-900/30 dark:text-green-300"
              : "bg-red-50 text-red-800 dark:bg-red-900/30 dark:text-red-300"
          }`}
        >
          {toast.type === "success" ? (
            <CheckCircleIcon className="h-5 w-5 flex-shrink-0" />
          ) : (
            <ExclamationTriangleIcon className="h-5 w-5 flex-shrink-0" />
          )}
          {toast.msg}
        </div>
      )}

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <ArrowPathIcon className="h-8 w-8 animate-spin text-purple-500" />
        </div>
      ) : subTab === "autopilot" && config && status ? (
        <AutopilotSection
          status={status}
          config={config}
          saving={saving}
          onToggle={handleToggle}
          onSave={handleSaveConfig}
          onTrigger={handleTrigger}
          triggerTopic={triggerTopic}
          setTriggerTopic={setTriggerTopic}
          triggering={triggering}
        />
      ) : subTab === "comments" ? (
        <CommentMonitorSection />
      ) : subTab === "moderation" ? (
        <ModerationSection />
      ) : null}
    </div>
  );
}

// ════════════════════════════════════════════════════════
//  AUTOPILOT SECTION
// ════════════════════════════════════════════════════════

function AutopilotSection({
  status,
  config,
  saving,
  onToggle,
  onSave,
  onTrigger,
  triggerTopic,
  setTriggerTopic,
  triggering,
}: {
  status: AutopilotStatusData;
  config: AutopilotConfig;
  saving: boolean;
  onToggle: () => void;
  onSave: (updates: Partial<AutopilotConfig>) => void;
  onTrigger: () => void;
  triggerTopic: string;
  setTriggerTopic: (v: string) => void;
  triggering: boolean;
}) {
  const [localWeights, setLocalWeights] = useState(config.format_weights);
  const [localWindows, setLocalWindows] = useState(config.posting_windows);
  const [editDay, setEditDay] = useState<string | null>(null);
  const [editThemes, setEditThemes] = useState<string[]>([]);

  useEffect(() => {
    setLocalWeights(config.format_weights);
    setLocalWindows(config.posting_windows);
  }, [config]);

  const formatIcons: Record<string, React.ElementType> = {
    image: PhotoIcon,
    text: DocumentTextIcon,
    video: VideoCameraIcon,
  };

  return (
    <div className="space-y-6">
      {/* Status + Toggle */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Master Toggle */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900 dark:text-white">Autopilot</h3>
            <button
              onClick={onToggle}
              className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
                status.enabled ? "bg-purple-600" : "bg-gray-300 dark:bg-gray-600"
              }`}
            >
              <span
                className={`inline-block h-6 w-6 transform rounded-full bg-white shadow transition-transform ${
                  status.enabled ? "translate-x-7" : "translate-x-1"
                }`}
              />
            </button>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {status.enabled ? (
              <span className="text-green-600 dark:text-green-400 font-medium">Active — posting automatically</span>
            ) : (
              <span className="text-gray-500 font-medium">Paused</span>
            )}
          </p>
        </div>

        {/* Posts Today */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Posts Today</h3>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {status.posts_today} <span className="text-sm font-normal text-gray-400">/ {config.posts_per_day}</span>
          </p>
          {status.next_post_at && (
            <p className="text-xs text-gray-400 mt-2">
              Next: {new Date(status.next_post_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </p>
          )}
        </div>

        {/* Quick Trigger */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Manual Post</h3>
          <div className="flex gap-2">
            <input
              type="text"
              value={triggerTopic}
              onChange={(e) => setTriggerTopic(e.target.value)}
              placeholder="Topic (optional)"
              className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white placeholder:text-gray-400"
            />
            <button
              onClick={onTrigger}
              disabled={triggering}
              className="flex items-center gap-1 rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50"
            >
              {triggering ? <ArrowPathIcon className="h-4 w-4 animate-spin" /> : <PlayIcon className="h-4 w-4" />}
              Post
            </button>
          </div>
        </div>
      </div>

      {/* Posting Schedule */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <ClockIcon className="h-5 w-5 text-purple-500" />
            Posting Schedule
          </h3>
          <span className="text-sm text-gray-400">{localWindows.length} posts/day</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
          {localWindows.map((w, i) => (
            <div key={i} className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-3 text-center">
              <p className="text-lg font-bold text-gray-900 dark:text-white">
                {String(w.hour).padStart(2, "0")}:{String(w.minute).padStart(2, "0")}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{w.label}</p>
              <div className="flex gap-1 mt-2 justify-center">
                <input
                  type="number"
                  min={0}
                  max={23}
                  value={w.hour}
                  onChange={(e) => {
                    const updated = [...localWindows];
                    updated[i] = { ...updated[i], hour: parseInt(e.target.value) || 0 };
                    setLocalWindows(updated);
                  }}
                  className="w-12 px-1 py-0.5 text-xs rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-center text-gray-900 dark:text-white"
                />
                <span className="text-gray-400 text-xs self-center">:</span>
                <input
                  type="number"
                  min={0}
                  max={59}
                  value={w.minute}
                  onChange={(e) => {
                    const updated = [...localWindows];
                    updated[i] = { ...updated[i], minute: parseInt(e.target.value) || 0 };
                    setLocalWindows(updated);
                  }}
                  className="w-12 px-1 py-0.5 text-xs rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-center text-gray-900 dark:text-white"
                />
              </div>
            </div>
          ))}
        </div>
        <div className="flex gap-2 mt-4">
          <button
            onClick={() => setLocalWindows([...localWindows, { hour: 12, minute: 0, label: "custom" }])}
            className="flex items-center gap-1 text-sm text-purple-600 hover:text-purple-800 font-medium"
          >
            <PlusIcon className="h-4 w-4" /> Add slot
          </button>
          {localWindows.length > 1 && (
            <button
              onClick={() => setLocalWindows(localWindows.slice(0, -1))}
              className="flex items-center gap-1 text-sm text-red-500 hover:text-red-700 font-medium"
            >
              <TrashIcon className="h-4 w-4" /> Remove last
            </button>
          )}
          <div className="flex-1" />
          <button
            onClick={() => onSave({ posting_windows: localWindows, posts_per_day: localWindows.length })}
            disabled={saving}
            className="rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Schedule"}
          </button>
        </div>
      </div>

      {/* Format Weights */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Content Format Mix</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
          Control what type of content gets auto-generated. Weights must add up to 100%.
          <br />
          <span className="text-yellow-600 dark:text-yellow-400 font-medium">
            ⚠ Video = ~$2 per 30s clip. Keep at 0% unless you have budget.
          </span>
        </p>
        <div className="space-y-4">
          {Object.entries(localWeights).map(([format, weight]) => {
            const Icon = formatIcons[format] || DocumentTextIcon;
            return (
              <div key={format} className="flex items-center gap-4">
                <Icon className="h-5 w-5 text-gray-500 flex-shrink-0" />
                <span className="w-16 text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">{format}</span>
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={Math.round(weight * 100)}
                  onChange={(e) => {
                    const newVal = parseInt(e.target.value) / 100;
                    setLocalWeights((prev) => ({ ...prev, [format]: newVal }));
                  }}
                  className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-600"
                />
                <span className="w-12 text-right text-sm font-bold text-gray-900 dark:text-white">
                  {Math.round(weight * 100)}%
                </span>
              </div>
            );
          })}
        </div>
        <div className="flex items-center justify-between mt-4">
          <p className="text-xs text-gray-400">
            Total: {Math.round(Object.values(localWeights).reduce((a, b) => a + b, 0) * 100)}%
            {Math.abs(Object.values(localWeights).reduce((a, b) => a + b, 0) - 1.0) > 0.05 && (
              <span className="text-red-500 ml-2">Must equal 100%</span>
            )}
          </p>
          <button
            onClick={() => onSave({ format_weights: localWeights })}
            disabled={saving || Math.abs(Object.values(localWeights).reduce((a, b) => a + b, 0) - 1.0) > 0.05}
            className="rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Weights"}
          </button>
        </div>
      </div>

      {/* Daily Themes */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Daily Content Themes</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
          Each day has a pool of themes. The autopilot randomly picks one for each post.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {Object.entries(config.daily_themes).map(([day, themes]) => (
            <button
              key={day}
              onClick={() => {
                setEditDay(day);
                setEditThemes([...themes]);
              }}
              className="text-left bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4 hover:ring-2 hover:ring-purple-400 transition-all"
            >
              <p className="font-medium text-gray-900 dark:text-white">{DAY_NAMES[day] || `Day ${day}`}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{themes.length} themes</p>
              <p className="text-xs text-gray-400 mt-2 line-clamp-2">{themes[0]?.slice(0, 80)}...</p>
            </button>
          ))}
        </div>

        {/* Theme Editor Modal */}
        {editDay !== null && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] overflow-auto p-6 m-4">
              <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                {DAY_NAMES[editDay]} Themes
              </h4>
              <div className="space-y-3">
                {editThemes.map((theme, i) => (
                  <div key={i} className="flex gap-2">
                    <textarea
                      value={theme}
                      onChange={(e) => {
                        const updated = [...editThemes];
                        updated[i] = e.target.value;
                        setEditThemes(updated);
                      }}
                      rows={2}
                      className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white"
                    />
                    <button
                      onClick={() => setEditThemes(editThemes.filter((_, j) => j !== i))}
                      className="text-red-500 hover:text-red-700 p-2"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
              <button
                onClick={() => setEditThemes([...editThemes, ""])}
                className="flex items-center gap-1 text-sm text-purple-600 hover:text-purple-800 font-medium mt-3"
              >
                <PlusIcon className="h-4 w-4" /> Add theme
              </button>
              <div className="flex justify-end gap-3 mt-6 border-t border-gray-200 dark:border-gray-700 pt-4">
                <button
                  onClick={() => setEditDay(null)}
                  className="rounded-lg border border-gray-300 dark:border-gray-600 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    const nonEmpty = editThemes.filter((t) => t.trim());
                    onSave({ daily_themes: { ...config.daily_themes, [editDay!]: nonEmpty } });
                    setEditDay(null);
                  }}
                  disabled={saving}
                  className="rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50"
                >
                  {saving ? "Saving..." : "Save Themes"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════════════
//  COMMENT MONITOR SECTION
// ════════════════════════════════════════════════════════

function CommentMonitorSection() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-3 mb-4">
        <ChatBubbleLeftRightIcon className="h-8 w-8 text-blue-500" />
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Comment Monitor</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Automatically monitors your Facebook posts for new comments and replies using AI.
          </p>
        </div>
      </div>
      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 mt-4">
        <p className="text-sm text-blue-800 dark:text-blue-300">
          <strong>Status: Active</strong> — Checking for new comments every 5 minutes.
          AI auto-replies are enabled for questions about pricing, hours, and programs.
        </p>
      </div>
      <div className="mt-4 text-sm text-gray-500 dark:text-gray-400">
        The comment monitor runs automatically in the background. It scans your recent Facebook posts,
        classifies incoming comments (questions, compliments, spam, complaints), and replies appropriately
        using your gym&apos;s real pricing and program data.
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════════════
//  MODERATION SECTION
// ════════════════════════════════════════════════════════

function ModerationSection() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-3 mb-4">
        <ShieldCheckIcon className="h-8 w-8 text-green-500" />
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Content Moderation</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Automated rules to filter spam, hide inappropriate comments, and flag content for review.
          </p>
        </div>
      </div>
      <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-4 mt-4">
        <p className="text-sm text-green-800 dark:text-green-300">
          <strong>Status: Active</strong> — Default moderation rules are enforced. Spam and toxic
          comments are automatically hidden.
        </p>
      </div>
      <div className="mt-4 text-sm text-gray-500 dark:text-gray-400">
        Moderation runs alongside the comment monitor. Comments flagged as spam, toxic, or off-topic
        are automatically handled based on severity. Complaints and sensitive topics are escalated
        for human review.
      </div>
    </div>
  );
}
