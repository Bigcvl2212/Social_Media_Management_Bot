"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  RocketLaunchIcon,
  ArrowTrendingUpIcon,
  EyeIcon,
  TrophyIcon,
  UserGroupIcon,
  PlusIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  BoltIcon,
  ChartBarIcon,
} from "@heroicons/react/24/outline";
import {
  growthTrackerApi,
  competitorSpyApi,
  type Milestone,
  type Competitor,
} from "@/lib/growth-spy-api";

export function GrowthSpyDashboard() {
  const queryClient = useQueryClient();
  const [activeSection, setActiveSection] = useState<"growth" | "spy">("growth");
  const [newCompName, setNewCompName] = useState("");
  const [newCompUrl, setNewCompUrl] = useState("");

  // Growth queries
  const { data: dashData } = useQuery({
    queryKey: ["growth-dashboard"],
    queryFn: growthTrackerApi.getDashboard,
  });

  const { data: reportData } = useQuery({
    queryKey: ["growth-report"],
    queryFn: growthTrackerApi.getReport,
  });

  const { data: milestonesData } = useQuery({
    queryKey: ["growth-milestones"],
    queryFn: growthTrackerApi.getMilestones,
  });

  const { data: trendData } = useQuery({
    queryKey: ["growth-trend"],
    queryFn: () => growthTrackerApi.getTrend(30),
  });

  const recordSnapshot = useMutation({
    mutationFn: growthTrackerApi.recordSnapshot,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["growth-dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["growth-milestones"] });
      queryClient.invalidateQueries({ queryKey: ["growth-trend"] });
    },
  });

  // Competitor queries
  const { data: competitorsData } = useQuery({
    queryKey: ["competitors"],
    queryFn: competitorSpyApi.listCompetitors,
  });

  const { data: spyDashData } = useQuery({
    queryKey: ["spy-dashboard"],
    queryFn: competitorSpyApi.getDashboard,
  });

  const addCompetitor = useMutation({
    mutationFn: competitorSpyApi.addCompetitor,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["competitors"] });
      queryClient.invalidateQueries({ queryKey: ["spy-dashboard"] });
      setNewCompName("");
      setNewCompUrl("");
    },
  });

  const deleteCompetitor = useMutation({
    mutationFn: competitorSpyApi.deleteCompetitor,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["competitors"] });
      queryClient.invalidateQueries({ queryKey: ["spy-dashboard"] });
    },
  });

  const scanCompetitor = useMutation({
    mutationFn: ({ id, posts }: { id: string; posts: Array<{ text: string; engagement?: number }> }) =>
      competitorSpyApi.scanCompetitor(id, posts),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["competitors"] }),
  });

  const counterPost = useMutation({
    mutationFn: (id: string) => competitorSpyApi.generateCounterPost(id),
  });

  const dashboard = dashData;
  const milestones = milestonesData?.milestones || [];
  const report = reportData?.report;
  const competitors = competitorsData?.competitors || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Growth & Competitor Intel</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Track your growth, hit milestones, and spy on competitors.</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setActiveSection("growth")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeSection === "growth" ? "bg-purple-600 text-white" : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
            }`}
          >
            Growth
          </button>
          <button
            onClick={() => setActiveSection("spy")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeSection === "spy" ? "bg-purple-600 text-white" : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
            }`}
          >
            Competitor Spy
          </button>
        </div>
      </div>

      {activeSection === "growth" ? (
        <>
          {/* Growth KPIs */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <KpiCard icon={UserGroupIcon} label="Followers" value={String(dashboard?.latest?.followers || 0)} color="blue" />
            <KpiCard icon={ArrowTrendingUpIcon} label="Engagement" value={dashboard?.latest?.engagement_rate ? `${(dashboard.latest.engagement_rate * 100).toFixed(1)}%` : "—"} color="green" />
            <KpiCard icon={EyeIcon} label="Reach" value={String(dashboard?.latest?.reach || 0)} color="purple" />
            <KpiCard icon={TrophyIcon} label="Milestones" value={String(dashboard?.milestones_hit || 0)} color="yellow" />
          </div>

          {/* Record Snapshot */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-3">Record Today&apos;s Metrics</h2>
            <button
              onClick={() => recordSnapshot.mutate({ followers: 0, engagement_rate: 0, reach: 0, impressions: 0 })}
              disabled={recordSnapshot.isPending}
              className="px-6 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-cyan-700 disabled:opacity-50"
            >
              {recordSnapshot.isPending ? "Recording..." : "Snapshot Now"}
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Milestones */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <TrophyIcon className="h-5 w-5 text-yellow-500" /> Milestone Wall
              </h2>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {milestones.map((ms) => (
                  <div
                    key={ms.id}
                    className={`p-3 rounded-lg border ${
                      ms.achieved
                        ? "border-yellow-300 bg-yellow-50 dark:bg-yellow-900/20 dark:border-yellow-700"
                        : "border-gray-200 dark:border-gray-700"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {ms.achieved ? "🏆" : "🎯"} {ms.metric}: {ms.target.toLocaleString()}
                      </span>
                      {ms.achieved && (
                        <span className="text-xs text-yellow-600 dark:text-yellow-400">
                          {ms.achieved_at ? new Date(ms.achieved_at).toLocaleDateString() : "Achieved"}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
                {milestones.length === 0 && <p className="text-sm text-gray-400">No milestones tracked yet.</p>}
              </div>
            </div>

            {/* Weekly Report */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <ChartBarIcon className="h-5 w-5" /> Weekly Report
              </h2>
              {report ? (
                <div className="space-y-3">
                  <p className="text-xs text-gray-500 dark:text-gray-400">{report.period}</p>
                  {Object.entries(report.changes || {}).map(([key, val]) => (
                    <div key={key} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                      <span className="text-sm text-gray-700 dark:text-gray-300 capitalize">{key.replace(/_/g, " ")}</span>
                      <span className={`text-sm font-bold ${Number(val) >= 0 ? "text-green-600" : "text-red-600"}`}>
                        {Number(val) >= 0 ? "+" : ""}{String(val)}
                      </span>
                    </div>
                  ))}
                  {(report.highlights || []).length > 0 && (
                    <div className="mt-3 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                      <p className="text-xs font-medium text-purple-700 dark:text-purple-300 mb-1">Highlights</p>
                      {report.highlights.map((h, i) => (
                        <p key={i} className="text-sm text-gray-700 dark:text-gray-300">• {h}</p>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-sm text-gray-400">No report data yet. Record snapshots to generate reports.</p>
              )}
            </div>
          </div>

          {/* Trend Chart Placeholder */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">30-Day Trend</h2>
            <div className="h-48 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
              {(trendData?.trend || []).length > 0 ? (
                <div className="w-full h-full p-4 flex items-end gap-1">
                  {trendData!.trend.map((point, i) => (
                    <div
                      key={i}
                      className="flex-1 bg-gradient-to-t from-purple-600 to-purple-400 rounded-t"
                      style={{ height: `${Math.max(10, (point.followers / Math.max(...trendData!.trend.map(t => t.followers), 1)) * 100)}%` }}
                      title={`${point.date}: ${point.followers} followers`}
                    />
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 dark:text-gray-400">Record daily snapshots to see trends here</p>
              )}
            </div>
          </div>
        </>
      ) : (
        <>
          {/* Spy Section */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <KpiCard icon={MagnifyingGlassIcon} label="Competitors" value={String(competitors.length)} color="blue" />
            <KpiCard icon={BoltIcon} label="Recent Scans" value={String((spyDashData as Record<string, unknown>)?.recent_scans || 0)} color="purple" />
            <KpiCard icon={RocketLaunchIcon} label="Counter Posts" value="—" color="green" />
          </div>

          {/* Add Competitor */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-3">Add Competitor</h2>
            <div className="flex flex-col sm:flex-row gap-3">
              <input
                value={newCompName}
                onChange={(e) => setNewCompName(e.target.value)}
                className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white"
                placeholder="Competitor name"
              />
              <input
                value={newCompUrl}
                onChange={(e) => setNewCompUrl(e.target.value)}
                className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white"
                placeholder="Platform URL (optional)"
              />
              <button
                onClick={() => newCompName && addCompetitor.mutate({ name: newCompName, platform_url: newCompUrl || undefined })}
                disabled={!newCompName || addCompetitor.isPending}
                className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 flex items-center gap-2"
              >
                <PlusIcon className="h-4 w-4" /> Add
              </button>
            </div>
          </div>

          {/* Competitor Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {competitors.map((comp) => (
              <CompetitorCard
                key={comp.id}
                competitor={comp}
                onScan={() => scanCompetitor.mutate({ id: comp.id, posts: [] })}
                onCounterPost={() => counterPost.mutate(comp.id)}
                onDelete={() => deleteCompetitor.mutate(comp.id)}
                isScanning={scanCompetitor.isPending}
                counterPostResult={counterPost.data}
              />
            ))}
            {competitors.length === 0 && (
              <div className="col-span-full text-center py-12 text-gray-500 dark:text-gray-400">
                No competitors added yet. Add one to start spying!
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

function CompetitorCard({
  competitor,
  onScan,
  onCounterPost,
  onDelete,
  isScanning,
  counterPostResult
}: {
  competitor: Competitor;
  onScan: () => void;
  onCounterPost: () => void;
  onDelete: () => void;
  isScanning: boolean;
  counterPostResult: unknown;
}) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-bold text-gray-900 dark:text-white">{competitor.name}</h3>
          {competitor.platform_url && (
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{competitor.platform_url}</p>
          )}
        </div>
        <button onClick={onDelete} className="p-1 text-gray-400 hover:text-red-500">
          <TrashIcon className="h-5 w-5" />
        </button>
      </div>
      {competitor.notes && (
        <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">{competitor.notes}</p>
      )}
      <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 mb-4">
        <span>{competitor.scans?.length || 0} scans</span>
        <span>•</span>
        <span>Added {new Date(competitor.added_at).toLocaleDateString()}</span>
      </div>
      <div className="flex gap-2">
        <button
          onClick={onScan}
          disabled={isScanning}
          className="flex-1 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {isScanning ? "Scanning..." : "Scan"}
        </button>
        <button
          onClick={onCounterPost}
          className="flex-1 py-2 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          Counter Post
        </button>
      </div>
    </div>
  );
}

function KpiCard({ icon: Icon, label, value, color }: { icon: React.ComponentType<{ className?: string }>; label: string; value: string; color: "blue" | "green" | "purple" | "yellow" }) {
  const colors = {
    blue: "from-blue-600 to-blue-400",
    green: "from-green-600 to-green-400",
    purple: "from-purple-600 to-purple-400",
    yellow: "from-yellow-600 to-yellow-400",
  };
  return (
    <div className={`bg-gradient-to-br ${colors[color]} rounded-2xl p-5 text-white shadow-lg`}>
      <Icon className="h-7 w-7 mb-2 opacity-80" />
      <p className="text-xs opacity-80">{label}</p>
      <p className="text-xl font-bold mt-1">{value}</p>
    </div>
  );
}
