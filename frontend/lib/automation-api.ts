const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ── Autopilot ───────────────────────────────────────────
export async function getAutopilotStatus() {
  const res = await fetch(`${API_BASE_URL}/api/v1/autopilot/status`);
  if (!res.ok) throw new Error('Failed to fetch autopilot status');
  return res.json();
}

export async function toggleAutopilot(enabled: boolean) {
  const res = await fetch(`${API_BASE_URL}/api/v1/autopilot/toggle`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ enabled }),
  });
  if (!res.ok) throw new Error('Failed to toggle autopilot');
  return res.json();
}

export async function getAutopilotConfig() {
  const res = await fetch(`${API_BASE_URL}/api/v1/autopilot/config`);
  if (!res.ok) throw new Error('Failed to fetch autopilot config');
  return res.json();
}

export async function updateAutopilotConfig(updates: Record<string, unknown>) {
  const res = await fetch(`${API_BASE_URL}/api/v1/autopilot/config`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || 'Failed to update config');
  }
  return res.json();
}

export async function triggerAutopilotPost(topic?: string) {
  const res = await fetch(`${API_BASE_URL}/api/v1/autopilot/trigger`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic: topic || null }),
  });
  if (!res.ok) throw new Error('Failed to trigger post');
  return res.json();
}

// ── Automation Dashboard ────────────────────────────────
export async function getAutomationDashboard() {
  const res = await fetch(`${API_BASE_URL}/api/v1/automation/dashboard`);
  if (!res.ok) throw new Error('Failed to fetch automation dashboard');
  return res.json();
}

export async function getAutomationHealth() {
  const res = await fetch(`${API_BASE_URL}/api/v1/automation/health`);
  if (!res.ok) throw new Error('Failed to fetch automation health');
  return res.json();
}

// ── DM Campaigns ────────────────────────────────────────
export async function listDMCampaigns() {
  const res = await fetch(`${API_BASE_URL}/api/v1/automation/direct-messages`);
  if (!res.ok) throw new Error('Failed to fetch DM campaigns');
  return res.json();
}

export async function getDMStats() {
  const res = await fetch(`${API_BASE_URL}/api/v1/automation/direct-messages/stats`);
  if (!res.ok) throw new Error('Failed to fetch DM stats');
  return res.json();
}

// ── Comment Management ──────────────────────────────────
export async function getCommentStats() {
  const res = await fetch(`${API_BASE_URL}/api/v1/automation/comments/stats`);
  if (!res.ok) throw new Error('Failed to fetch comment stats');
  return res.json();
}

// ── Moderation ──────────────────────────────────────────
export async function listModerationRules() {
  const res = await fetch(`${API_BASE_URL}/api/v1/automation/moderation/rules`);
  if (!res.ok) throw new Error('Failed to fetch moderation rules');
  return res.json();
}

export async function getModerationStats() {
  const res = await fetch(`${API_BASE_URL}/api/v1/automation/moderation/stats`);
  if (!res.ok) throw new Error('Failed to fetch moderation stats');
  return res.json();
}

export async function toggleAutomationFeature(feature: string) {
  const res = await fetch(`${API_BASE_URL}/api/v1/automation/toggle/${feature}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`Failed to toggle ${feature}`);
  return res.json();
}
