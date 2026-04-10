import { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { Campaign, ConnectionConfig, LeadWithMessage, MessageVariant } from '../shared/types';
import { getConnection, setConnection, getLeadQueue } from '../shared/storage';
import { api } from '../shared/api';

type Tab = 'connection' | 'campaigns' | 'leads' | 'activity';

function Options() {
  const [activeTab, setActiveTab] = useState<Tab>('connection');

  return (
    <div className="options-container">
      <div className="page-header">
        <span className="logo">KONVERSLY</span>
        <span className="subtitle">Outbound Agent</span>
      </div>

      <div className="tabs">
        <button className={`tab ${activeTab === 'connection' ? 'active' : ''}`} onClick={() => setActiveTab('connection')}>Connection</button>
        <button className={`tab ${activeTab === 'campaigns' ? 'active' : ''}`} onClick={() => setActiveTab('campaigns')}>Campaigns</button>
        <button className={`tab ${activeTab === 'leads' ? 'active' : ''}`} onClick={() => setActiveTab('leads')}>Lead Queue</button>
        <button className={`tab ${activeTab === 'activity' ? 'active' : ''}`} onClick={() => setActiveTab('activity')}>Activity</button>
      </div>

      {activeTab === 'connection' && <ConnectionTab />}
      {activeTab === 'campaigns' && <CampaignsTab />}
      {activeTab === 'leads' && <LeadQueueTab />}
      {activeTab === 'activity' && <ActivityTab />}
    </div>
  );
}

/* ───────────────── Connection Tab ───────────────── */

function ConnectionTab() {
  const [config, setConfig] = useState<ConnectionConfig>({
    api_url: 'https://konversly-ai-setter-production.up.railway.app',
    api_key: '',
    account_id: '',
    ghl_location_id: '',
  });
  const [status, setStatus] = useState<'idle' | 'testing' | 'connected' | 'error'>('idle');
  const [message, setMessage] = useState('');

  useEffect(() => {
    getConnection().then((conn) => {
      if (conn) {
        setConfig(conn);
        setStatus('connected');
      }
    });
  }, []);

  const handleTest = async () => {
    setStatus('testing');
    setMessage('');
    try {
      // Temporarily save so the api client can use it
      await setConnection(config);
      await api.testConnection();
      setStatus('connected');
      setMessage('Connection successful');
    } catch (err) {
      setStatus('error');
      setMessage(err instanceof Error ? err.message : 'Connection failed');
    }
  };

  const handleSave = async () => {
    await setConnection(config);
    setMessage('Settings saved');
    setStatus('connected');
  };

  return (
    <>
      {message && (
        <div className={`message ${status === 'error' ? 'message-error' : 'message-success'}`}>
          {message}
        </div>
      )}

      <div className="card">
        <div className="card-title">API Connection</div>

        <div className="form-group">
          <label>API URL</label>
          <input
            type="text"
            value={config.api_url}
            onChange={(e) => setConfig({ ...config, api_url: e.target.value })}
            placeholder="https://konversly-ai-setter-production.up.railway.app"
          />
        </div>

        <div className="form-group">
          <label>Account ID</label>
          <input
            type="text"
            value={config.account_id}
            onChange={(e) => setConfig({ ...config, account_id: e.target.value })}
            placeholder="UUID of your Konversly account"
          />
          <small style={{ color: '#888', fontSize: 12, marginTop: 4, display: 'block' }}>
            Find this in the Konversly dashboard → Accounts → click your account. The Account ID is shown below the account name with a copy button.
          </small>
        </div>

        <div className="form-group">
          <label>GHL Location ID</label>
          <input
            type="text"
            value={config.ghl_location_id}
            onChange={(e) => setConfig({ ...config, ghl_location_id: e.target.value })}
            placeholder="GoHighLevel Location ID"
          />
          <small style={{ color: '#888', fontSize: 12, marginTop: 4, display: 'block' }}>
            Find this in the Konversly dashboard → Accounts → click your account. The GHL Location ID is shown in the account header.
          </small>
        </div>

        <div className="btn-group">
          <button className="btn btn-secondary" onClick={handleTest} disabled={status === 'testing'}>
            {status === 'testing' ? 'Testing...' : 'Test Connection'}
          </button>
          <button className="btn btn-primary" onClick={handleSave}>Save</button>
        </div>
      </div>

      <div className={`status-indicator ${status === 'connected' ? 'connected' : 'disconnected'}`}>
        <span className={`status-dot ${status === 'connected' ? 'connected' : 'disconnected'}`} />
        {status === 'connected' ? 'Connected' : status === 'error' ? 'Connection Failed' : 'Not Connected'}
      </div>
    </>
  );
}

/* ───────────────── Campaigns Tab ───────────────── */

function CampaignsTab() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [message, setMessage] = useState('');
  const [form, setForm] = useState({
    name: '',
    target_account: '',
    prompt_instruction: '',
    send_mode: 'review' as 'review' | 'autopilot',
    autopilot_threshold: 5,
    follower_min: 1000,
    follower_max: 100000,
    bio_keywords_include: '',
    bio_keywords_exclude: '',
    dms_per_day: 40,
    // Working hours + pacing
    working_hours_start: 9,
    working_hours_end: 17,
    pacing_enabled: true,
    // Daily limits (min/max)
    daily_limit_min: 20,
    daily_limit_max: 40,
    // Engagement warmup
    warmup_follow: false,
    warmup_like_post: false,
    warmup_like_story: false,
    // Message variants
    variants: [] as MessageVariant[],
    // Scheduling
    scheduled_at: '',
  });

  useEffect(() => {
    loadCampaigns();
  }, []);

  const loadCampaigns = async () => {
    setLoading(true);
    try {
      const conn = await getConnection();
      if (!conn) {
        setMessage('Not connected. Go to Connection tab first.');
        setLoading(false);
        return;
      }
      const result = await api.getCampaigns(conn.account_id);
      setCampaigns((result.campaigns || []) as Campaign[]);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Failed to load campaigns');
    }
    setLoading(false);
  };

  const handleCreate = async () => {
    try {
      const conn = await getConnection();
      if (!conn) return;

      const created = await api.createCampaign({
        account_id: conn.account_id,
        name: form.name,
        target_account: form.target_account,
        prompt_instruction: form.prompt_instruction,
        send_mode: form.send_mode,
        autopilot_threshold: form.autopilot_threshold,
        filters: {
          follower_min: form.follower_min,
          follower_max: form.follower_max,
          bio_keywords_include: form.bio_keywords_include.split(',').map(s => s.trim()).filter(Boolean),
          bio_keywords_exclude: form.bio_keywords_exclude.split(',').map(s => s.trim()).filter(Boolean),
          account_types: [],
        },
        rate_limits: {
          dms_per_day: form.daily_limit_max,
          delay_min: 60,
          delay_max: 180,
        },
        working_hours_start: form.working_hours_start,
        working_hours_end: form.working_hours_end,
        pacing_enabled: form.pacing_enabled,
        daily_limit_min: form.daily_limit_min,
        daily_limit_max: form.daily_limit_max,
        warmup_follow: form.warmup_follow,
        warmup_like_post: form.warmup_like_post,
        warmup_like_story: form.warmup_like_story,
        variants: form.variants.filter(v => v.name && v.prompt_instruction),
        ...(form.scheduled_at ? { scheduled_at: new Date(form.scheduled_at).toISOString(), status: 'scheduled' } : {}),
      }) as unknown as Campaign;

      // If scheduled, add to local campaign queue with the real ID from backend
      if (form.scheduled_at && created?.id) {
        chrome.runtime.sendMessage({
          type: 'SCHEDULE_CAMPAIGN',
          campaign: created,
          scheduled_at: new Date(form.scheduled_at).toISOString(),
        });
      }

      setShowForm(false);
      setForm({
        name: '',
        target_account: '',
        prompt_instruction: '',
        send_mode: 'review',
        autopilot_threshold: 5,
        follower_min: 1000,
        follower_max: 100000,
        bio_keywords_include: '',
        bio_keywords_exclude: '',
        dms_per_day: 40,
        working_hours_start: 9,
        working_hours_end: 17,
        pacing_enabled: true,
        daily_limit_min: 20,
        daily_limit_max: 40,
        warmup_follow: false,
        warmup_like_post: false,
        warmup_like_story: false,
        variants: [],
        scheduled_at: '',
      });
      await loadCampaigns();
      setMessage('Campaign created');
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Failed to create campaign');
    }
  };

  return (
    <>
      {message && <div className="message message-error">{message}</div>}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h3 style={{ fontSize: 16, fontWeight: 700 }}>Campaigns</h3>
        <button className="btn btn-primary btn-sm" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ New Campaign'}
        </button>
      </div>

      {showForm && (
        <div className="card">
          <div className="card-title">Create Campaign</div>

          <div className="form-row">
            <div className="form-group">
              <label>Campaign Name</label>
              <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Skincare Influencers Q2" />
            </div>
            <div className="form-group">
              <label>Target Account Handle</label>
              <input type="text" value={form.target_account} onChange={(e) => setForm({ ...form, target_account: e.target.value })} placeholder="@competitor_handle" />
            </div>
          </div>

          <div className="form-group">
            <label>Prompt Instruction</label>
            <textarea value={form.prompt_instruction} onChange={(e) => setForm({ ...form, prompt_instruction: e.target.value })} placeholder="Describe the tone and content of your outreach DMs..." />
          </div>

          <div className="form-group">
            <label>Send Mode</label>
            <div className="toggle-group">
              <button className={`toggle-option ${form.send_mode === 'review' ? 'active' : ''}`} onClick={() => setForm({ ...form, send_mode: 'review' })}>Review</button>
              <button className={`toggle-option ${form.send_mode === 'autopilot' ? 'active' : ''}`} onClick={() => setForm({ ...form, send_mode: 'autopilot' })}>Autopilot</button>
            </div>
          </div>

          {form.send_mode === 'autopilot' && (
            <div className="form-group">
              <label>Autopilot Threshold (approve first N manually)</label>
              <input type="number" value={form.autopilot_threshold} onChange={(e) => setForm({ ...form, autopilot_threshold: parseInt(e.target.value) || 5 })} />
            </div>
          )}

          <div className="form-row">
            <div className="form-group">
              <label>Follower Min</label>
              <input type="number" value={form.follower_min} onChange={(e) => setForm({ ...form, follower_min: parseInt(e.target.value) || 0 })} />
            </div>
            <div className="form-group">
              <label>Follower Max</label>
              <input type="number" value={form.follower_max} onChange={(e) => setForm({ ...form, follower_max: parseInt(e.target.value) || 100000 })} />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Bio Keywords Include (comma-separated)</label>
              <input type="text" value={form.bio_keywords_include} onChange={(e) => setForm({ ...form, bio_keywords_include: e.target.value })} placeholder="beauty, skincare, wellness" />
            </div>
            <div className="form-group">
              <label>Bio Keywords Exclude (comma-separated)</label>
              <input type="text" value={form.bio_keywords_exclude} onChange={(e) => setForm({ ...form, bio_keywords_exclude: e.target.value })} placeholder="spam, bot, giveaway" />
            </div>
          </div>

          {/* ── Working Hours & Pacing ── */}
          <div style={{ borderTop: '1px solid #333', paddingTop: 16, marginTop: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 10, color: '#aaa', textTransform: 'uppercase', letterSpacing: 1 }}>Working Hours & Pacing</div>
            <div className="form-row">
              <div className="form-group">
                <label>Start Hour (0-23)</label>
                <input type="number" min={0} max={23} value={form.working_hours_start} onChange={(e) => setForm({ ...form, working_hours_start: parseInt(e.target.value) || 9 })} />
              </div>
              <div className="form-group">
                <label>End Hour (0-23)</label>
                <input type="number" min={0} max={23} value={form.working_hours_end} onChange={(e) => setForm({ ...form, working_hours_end: parseInt(e.target.value) || 17 })} />
              </div>
            </div>
            <div className="form-group">
              <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <input type="checkbox" checked={form.pacing_enabled} onChange={(e) => setForm({ ...form, pacing_enabled: e.target.checked })} />
                Spread DMs evenly across working hours (pacing)
              </label>
            </div>
          </div>

          {/* ── Daily Limits ── */}
          <div style={{ borderTop: '1px solid #333', paddingTop: 16, marginTop: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 10, color: '#aaa', textTransform: 'uppercase', letterSpacing: 1 }}>Daily Limits</div>
            <div className="form-row">
              <div className="form-group">
                <label>Min DMs Per Day</label>
                <input type="number" value={form.daily_limit_min} onChange={(e) => setForm({ ...form, daily_limit_min: parseInt(e.target.value) || 20 })} />
              </div>
              <div className="form-group">
                <label>Max DMs Per Day</label>
                <input type="number" value={form.daily_limit_max} onChange={(e) => setForm({ ...form, daily_limit_max: parseInt(e.target.value) || 40 })} />
              </div>
            </div>
            <div style={{ fontSize: 12, color: '#888' }}>A random target between min and max is chosen each day to vary your sending pattern.</div>
          </div>

          {/* ── Engagement Warmup ── */}
          <div style={{ borderTop: '1px solid #333', paddingTop: 16, marginTop: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 10, color: '#aaa', textTransform: 'uppercase', letterSpacing: 1 }}>Engagement Warmup</div>
            <div style={{ fontSize: 12, color: '#888', marginBottom: 10 }}>Perform these actions before sending each DM to appear more organic.</div>
            <div className="form-group">
              <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <input type="checkbox" checked={form.warmup_follow} onChange={(e) => setForm({ ...form, warmup_follow: e.target.checked })} />
                Follow user before DMing
              </label>
            </div>
            <div className="form-group">
              <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <input type="checkbox" checked={form.warmup_like_post} onChange={(e) => setForm({ ...form, warmup_like_post: e.target.checked })} />
                Like a recent post before DMing
              </label>
            </div>
            <div className="form-group">
              <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <input type="checkbox" checked={form.warmup_like_story} onChange={(e) => setForm({ ...form, warmup_like_story: e.target.checked })} />
                Like a story before DMing
              </label>
            </div>
          </div>

          {/* ── Message Variants ── */}
          <div style={{ borderTop: '1px solid #333', paddingTop: 16, marginTop: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: '#aaa', textTransform: 'uppercase', letterSpacing: 1 }}>Message Variants</div>
              <button className="btn btn-secondary btn-sm" onClick={() => setForm({ ...form, variants: [...form.variants, { name: '', prompt_instruction: '', weight: 1 }] })}>
                + Add Variant
              </button>
            </div>
            {form.variants.length === 0 && (
              <div style={{ fontSize: 12, color: '#888' }}>No variants. The main prompt instruction above will be used for all DMs. Add variants to A/B test different outreach styles.</div>
            )}
            {form.variants.map((v, i) => (
              <div key={i} style={{ background: '#1a1a2e', borderRadius: 8, padding: 12, marginBottom: 10 }}>
                <div className="form-row">
                  <div className="form-group" style={{ flex: 2 }}>
                    <label>Variant Name</label>
                    <input type="text" value={v.name} placeholder={`Variant ${i + 1}`} onChange={(e) => {
                      const variants = [...form.variants];
                      variants[i] = { ...variants[i], name: e.target.value };
                      setForm({ ...form, variants });
                    }} />
                  </div>
                  <div className="form-group" style={{ flex: 1 }}>
                    <label>Weight (1-10)</label>
                    <input type="number" min={1} max={10} value={v.weight} onChange={(e) => {
                      const variants = [...form.variants];
                      variants[i] = { ...variants[i], weight: parseInt(e.target.value) || 1 };
                      setForm({ ...form, variants });
                    }} />
                  </div>
                  <button className="btn btn-secondary btn-sm" style={{ alignSelf: 'flex-end', marginBottom: 4 }} onClick={() => {
                    const variants = form.variants.filter((_, idx) => idx !== i);
                    setForm({ ...form, variants });
                  }}>Remove</button>
                </div>
                <div className="form-group">
                  <label>Prompt Instruction</label>
                  <textarea value={v.prompt_instruction} placeholder="Describe the tone/style for this variant..." onChange={(e) => {
                    const variants = [...form.variants];
                    variants[i] = { ...variants[i], prompt_instruction: e.target.value };
                    setForm({ ...form, variants });
                  }} />
                </div>
              </div>
            ))}
          </div>

          {/* ── Scheduling ── */}
          <div style={{ borderTop: '1px solid #333', paddingTop: 16, marginTop: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 10, color: '#aaa', textTransform: 'uppercase', letterSpacing: 1 }}>Schedule (Optional)</div>
            <div className="form-group">
              <label>Schedule start time</label>
              <input type="datetime-local" value={form.scheduled_at || ''} onChange={(e) => setForm({ ...form, scheduled_at: e.target.value })} />
              <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>Leave empty to start manually. Set a date/time to auto-start.</div>
            </div>
          </div>

          <div className="btn-group" style={{ marginTop: 16 }}>
            <button className="btn btn-primary" onClick={handleCreate} disabled={!form.name || !form.target_account || !form.prompt_instruction}>
              {form.scheduled_at ? 'Schedule Campaign' : 'Create Campaign'}
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="empty-state">Loading campaigns...</div>
      ) : campaigns.length === 0 ? (
        <div className="empty-state">No campaigns yet. Create one to get started.</div>
      ) : (
        campaigns.map((c) => (
          <div key={c.id} className="campaign-card">
            <div className="campaign-card-info">
              <div className="campaign-card-name">{c.name}</div>
              <div className="campaign-card-target">@{c.target_account}</div>
              <div className="campaign-card-stats">
                <span>Scraped: <strong>{c.leads_scraped}</strong></span>
                <span>Filtered: <strong>{c.leads_filtered}</strong></span>
                <span>Sent: <strong>{c.dms_sent}</strong></span>
              </div>
              {c.scheduled_at && c.status === 'scheduled' && (
                <div style={{ fontSize: 11, color: '#888', marginTop: 4 }}>
                  Scheduled: {new Date(c.scheduled_at).toLocaleString()}
                </div>
              )}
            </div>
            <span className={`badge badge-${c.status}`}>{c.status}</span>
          </div>
        ))
      )}
    </>
  );
}

/* ───────────────── Lead Queue Tab ───────────────── */

function LeadQueueTab() {
  const [leads, setLeads] = useState<LeadWithMessage[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeads();
    const interval = setInterval(loadLeads, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadLeads = async () => {
    const queue = await getLeadQueue();
    setLeads(queue.filter((l) => l.status === 'pending'));
    setLoading(false);
  };

  const handleApprove = (handle: string) => {
    chrome.runtime.sendMessage({ type: 'APPROVE_LEAD', handle });
    setLeads((prev) => prev.filter((l) => l.instagram_handle !== handle));
  };

  const handleRegenerate = (handle: string) => {
    chrome.runtime.sendMessage({ type: 'REGENERATE_DM', handle });
  };

  const handleSkip = (handle: string) => {
    chrome.runtime.sendMessage({ type: 'SKIP_LEAD', handle });
    setLeads((prev) => prev.filter((l) => l.instagram_handle !== handle));
  };

  if (loading) {
    return <div className="empty-state">Loading lead queue...</div>;
  }

  if (leads.length === 0) {
    return <div className="empty-state">No leads pending review. Start a campaign to begin scraping.</div>;
  }

  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <table className="lead-table">
        <thead>
          <tr>
            <th></th>
            <th>Handle</th>
            <th>Followers</th>
            <th>Bio</th>
            <th>Generated DM</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr key={lead.instagram_handle} className="lead-row">
              <td>
                <div className="lead-avatar">
                  {lead.instagram_handle.charAt(0).toUpperCase()}
                </div>
              </td>
              <td>
                <span className="lead-handle">@{lead.instagram_handle}</span>
              </td>
              <td>{lead.follower_count.toLocaleString()}</td>
              <td>
                <span className="lead-bio" title={lead.bio}>{lead.bio}</span>
              </td>
              <td>
                <div className="dm-preview" title={lead.generated_message}>
                  {lead.generated_message}
                </div>
              </td>
              <td>
                <div className="actions">
                  <button className="btn btn-primary btn-sm" onClick={() => handleApprove(lead.instagram_handle)}>Approve</button>
                  <button className="btn btn-secondary btn-sm" onClick={() => handleRegenerate(lead.instagram_handle)}>Regen</button>
                  <button className="btn btn-danger btn-sm" onClick={() => handleSkip(lead.instagram_handle)}>Skip</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ───────────────── Activity Tab ───────────────── */

function ActivityTab() {
  const [leads, setLeads] = useState<LeadWithMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [replyData, setReplyData] = useState<{ replied_handles: string[]; total_contacted: number; total_replies: number; reply_rate: string } | null>(null);
  const [variantStats, setVariantStats] = useState<Array<{ variant_name: string; sent: number; replies: number; reply_rate: string }>>([]);
  const [healthData, setHealthData] = useState<{ status: string; consecutive_failures: number; total_successes_today: number; total_failures_today: number } | null>(null);

  useEffect(() => {
    loadActivity();
    const interval = setInterval(loadActivity, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadActivity = async () => {
    const queue = await getLeadQueue();
    setLeads(queue.filter((l) => l.status === 'sent' || l.status === 'failed' || l.status === 'skipped'));
    setLoading(false);

    // Load reply stats + variant analytics
    try {
      const conn = await getConnection();
      if (conn) {
        const replies = await api.getReplies(conn.account_id);
        setReplyData(replies);

        // Load variant stats for the active campaign
        const campaigns = (await api.getCampaigns(conn.account_id)).campaigns as Campaign[];
        const activeCampaign = campaigns.find(c => c.status === 'running' || c.status === 'paused') || campaigns[0];
        if (activeCampaign?.id && activeCampaign.variants?.length > 0) {
          const stats = await api.getVariantStats(activeCampaign.id);
          setVariantStats(stats.variant_stats);
        }
      }
    } catch { /* ignore */ }

    // Load health from service worker
    chrome.runtime.sendMessage({ type: 'GET_HEALTH' }, (h) => {
      if (h) setHealthData(h);
    });
  };

  const repliedSet = new Set(replyData?.replied_handles || []);

  return (
    <>
      {/* Stats Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
        <div className="card" style={{ textAlign: 'center', padding: 16 }}>
          <div style={{ fontSize: 24, fontWeight: 700 }}>{replyData?.total_contacted || 0}</div>
          <div style={{ fontSize: 12, color: '#888' }}>Total Contacted</div>
        </div>
        <div className="card" style={{ textAlign: 'center', padding: 16 }}>
          <div style={{ fontSize: 24, fontWeight: 700, color: '#16a34a' }}>{replyData?.total_replies || 0}</div>
          <div style={{ fontSize: 12, color: '#888' }}>Replies</div>
        </div>
        <div className="card" style={{ textAlign: 'center', padding: 16 }}>
          <div style={{ fontSize: 24, fontWeight: 700, color: '#3b82f6' }}>{replyData?.reply_rate || '0.0'}%</div>
          <div style={{ fontSize: 12, color: '#888' }}>Reply Rate</div>
        </div>
        <div className="card" style={{ textAlign: 'center', padding: 16 }}>
          <div style={{ fontSize: 24, fontWeight: 700, color: healthData?.status === 'healthy' ? '#16a34a' : healthData?.status === 'warning' ? '#f59e0b' : '#dc2626' }}>
            {healthData?.status === 'healthy' ? 'OK' : healthData?.status === 'warning' ? '!!' : 'X'}
          </div>
          <div style={{ fontSize: 12, color: '#888' }}>
            Health {healthData && healthData.total_failures_today > 0 ? `(${healthData.total_failures_today} fails)` : ''}
          </div>
        </div>
      </div>

      {/* Variant Analytics */}
      {variantStats.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="card-title">Variant Performance</div>
          <table className="lead-table">
            <thead>
              <tr>
                <th>Variant</th>
                <th>Sent</th>
                <th>Replies</th>
                <th>Reply Rate</th>
              </tr>
            </thead>
            <tbody>
              {variantStats.map((v) => (
                <tr key={v.variant_name} className="lead-row">
                  <td>{v.variant_name}</td>
                  <td>{v.sent}</td>
                  <td>{v.replies}</td>
                  <td>{v.reply_rate}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Activity Log */}
      {loading ? (
        <div className="empty-state">Loading activity...</div>
      ) : leads.length === 0 ? (
        <div className="empty-state">No activity yet. Approve some leads to start sending DMs.</div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="lead-table">
            <thead>
              <tr>
                <th>Handle</th>
                <th>Message Sent</th>
                <th>Variant</th>
                <th>Status</th>
                <th>Reply</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead) => (
                <tr key={lead.instagram_handle} className="lead-row">
                  <td>
                    <span className="lead-handle">@{lead.instagram_handle}</span>
                  </td>
                  <td>
                    <div className="dm-preview" title={lead.generated_message}>
                      {lead.generated_message}
                    </div>
                  </td>
                  <td>
                    <span style={{ fontSize: 11, color: '#888' }}>{lead.variant_name || '—'}</span>
                  </td>
                  <td>
                    <span className={`badge badge-${lead.status}`}>{lead.status}</span>
                  </td>
                  <td>
                    {lead.status === 'sent' && (
                      <span style={{ color: repliedSet.has(lead.instagram_handle) ? '#16a34a' : '#555', fontSize: 12 }}>
                        {repliedSet.has(lead.instagram_handle) ? 'Replied' : 'Waiting'}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

createRoot(document.getElementById('root')!).render(<Options />);
