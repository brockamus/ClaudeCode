import { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { Campaign } from '../shared/types';
import { getConnection, getDmsToday, getLeadQueue, getAccountHealth, AccountHealth } from '../shared/storage';

function Popup() {
  const [connected, setConnected] = useState(false);
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [dmsToday, setDmsToday] = useState(0);
  const [queueSize, setQueueSize] = useState(0);
  const [pendingCount, setPendingCount] = useState(0);
  const [health, setHealth] = useState<AccountHealth | null>(null);

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const loadStatus = async () => {
    const conn = await getConnection();
    setConnected(!!conn);

    const today = await getDmsToday();
    setDmsToday(today);

    const queue = await getLeadQueue();
    setQueueSize(queue.length);
    setPendingCount(queue.filter(l => l.status === 'pending').length);

    const h = await getAccountHealth();
    setHealth(h);

    chrome.runtime.sendMessage({ type: 'GET_STATUS' }, (response) => {
      if (response) {
        setIsRunning(response.isRunning);
        setCampaign(response.campaign);
      }
    });
  };

  const handlePause = () => {
    chrome.runtime.sendMessage({ type: 'PAUSE_CAMPAIGN' });
    setIsRunning(false);
  };

  const handleResume = () => {
    if (campaign) {
      chrome.runtime.sendMessage({ type: 'START_CAMPAIGN', campaign });
      setIsRunning(true);
    }
  };

  const handleStop = () => {
    chrome.runtime.sendMessage({ type: 'STOP_CAMPAIGN' });
    setIsRunning(false);
    setCampaign(null);
  };

  const openOptions = () => {
    chrome.runtime.openOptionsPage();
  };

  const dailyLimit = campaign?.rate_limits?.dms_per_day || 40;
  const sentCount = campaign?.dms_sent || 0;
  const totalLeads = campaign?.leads_filtered || 0;
  const progress = totalLeads > 0 ? (sentCount / totalLeads) * 100 : 0;

  return (
    <div className="popup">
      <div className="header">
        <span className="logo">KONVERSLY</span>
        <span className={`status-dot ${connected ? 'connected' : 'disconnected'}`} />
        <span style={{ fontSize: 11, color: connected ? '#16a34a' : '#dc2626' }}>
          {connected ? 'Connected' : 'Not connected'}
        </span>
      </div>

      {!connected ? (
        <div className="empty">
          <p>Connect to Konversly to start</p>
          <br />
          <a className="link" onClick={openOptions}>Open Settings &rarr;</a>
        </div>
      ) : !campaign ? (
        <div className="empty">
          <p>No active campaign</p>
          <br />
          <a className="link" onClick={openOptions}>Create Campaign &rarr;</a>
        </div>
      ) : (
        <>
          <div style={{ marginBottom: 16 }}>
            <div className="campaign-name">{campaign.name}</div>
            <span className={`campaign-status ${campaign.status}`}>
              {isRunning ? 'Running' : campaign.status}
            </span>
          </div>

          <div className="stat-row">
            <span className="stat-label">Progress</span>
            <span className="stat-value">{sentCount} / {totalLeads}</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>

          <div className="stat-row">
            <span className="stat-label">DMs Today</span>
            <span className="stat-value">{dmsToday} / {dailyLimit}</span>
          </div>

          <div className="stat-row">
            <span className="stat-label">Pending Review</span>
            <span className="stat-value">{pendingCount}</span>
          </div>

          {health && (
            <div className="stat-row">
              <span className="stat-label">Account Health</span>
              <span className="stat-value" style={{
                color: health.status === 'healthy' ? '#16a34a' : health.status === 'warning' ? '#f59e0b' : '#dc2626',
              }}>
                {health.status === 'healthy' ? 'Healthy' : health.status === 'warning' ? 'Warning' : 'Blocked'}
                {health.total_failures_today > 0 && ` (${health.total_failures_today} fails)`}
              </span>
            </div>
          )}

          <div style={{ marginTop: 16 }}>
            {isRunning ? (
              <button className="btn btn-secondary" onClick={handlePause}>Pause</button>
            ) : (
              <button className="btn btn-primary" onClick={handleResume}>Resume</button>
            )}
            <button className="btn btn-danger" onClick={handleStop}>Stop Campaign</button>
          </div>

          <div style={{ textAlign: 'center', marginTop: 12 }}>
            <a className="link" onClick={openOptions}>Open Full Dashboard &rarr;</a>
          </div>
        </>
      )}
    </div>
  );
}

createRoot(document.getElementById('root')!).render(<Popup />);
