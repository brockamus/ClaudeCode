import { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { Campaign, ConnectionConfig, LeadWithMessage } from '../shared/types';
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
        </div>

        <div className="form-group">
          <label>GHL Location ID</label>
          <input
            type="text"
            value={config.ghl_location_id}
            onChange={(e) => setConfig({ ...config, ghl_location_id: e.target.value })}
            placeholder="GoHighLevel Location ID"
          />
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

      await api.createCampaign({
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
          dms_per_day: form.dms_per_day,
          delay_min: 60,
          delay_max: 180,
        },
      });

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

          <div className="form-group">
            <label>DMs Per Day</label>
            <input type="number" value={form.dms_per_day} onChange={(e) => setForm({ ...form, dms_per_day: parseInt(e.target.value) || 40 })} />
          </div>

          <div className="btn-group">
            <button className="btn btn-primary" onClick={handleCreate} disabled={!form.name || !form.target_account || !form.prompt_instruction}>
              Create Campaign
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

  const handleApprove = (index: number) => {
    chrome.runtime.sendMessage({ type: 'APPROVE_LEAD', index });
    setLeads((prev) => prev.filter((_, i) => i !== index));
  };

  const handleRegenerate = (index: number) => {
    chrome.runtime.sendMessage({ type: 'REGENERATE_DM', index });
  };

  const handleSkip = (index: number) => {
    chrome.runtime.sendMessage({ type: 'SKIP_LEAD', index });
    setLeads((prev) => prev.filter((_, i) => i !== index));
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
          {leads.map((lead, index) => (
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
                  <button className="btn btn-primary btn-sm" onClick={() => handleApprove(index)}>Approve</button>
                  <button className="btn btn-secondary btn-sm" onClick={() => handleRegenerate(index)}>Regen</button>
                  <button className="btn btn-danger btn-sm" onClick={() => handleSkip(index)}>Skip</button>
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

  useEffect(() => {
    loadActivity();
    const interval = setInterval(loadActivity, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadActivity = async () => {
    const queue = await getLeadQueue();
    setLeads(queue.filter((l) => l.status === 'sent' || l.status === 'failed' || l.status === 'skipped'));
    setLoading(false);
  };

  if (loading) {
    return <div className="empty-state">Loading activity...</div>;
  }

  if (leads.length === 0) {
    return <div className="empty-state">No activity yet. Approve some leads to start sending DMs.</div>;
  }

  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <table className="lead-table">
        <thead>
          <tr>
            <th>Handle</th>
            <th>Message Sent</th>
            <th>Status</th>
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
                <span className={`badge badge-${lead.status}`}>{lead.status}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

createRoot(document.getElementById('root')!).render(<Options />);
