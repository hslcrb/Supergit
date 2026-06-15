import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './StatusPanel.css';

function StatusPanel({ repoPath }) {
  const { t } = useTranslation();
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [commitMessage, setCommitMessage] = useState('');

  useEffect(() => {
    loadStatus();
  }, [repoPath]);

  const loadStatus = async () => {
    setLoading(true);
    setError(null);
    const result = await window.electron.git.status(repoPath);
    if (result.success) {
      setStatus(result.data);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  const handleStage = async (file) => {
    const result = await window.electron.git.add(repoPath, file);
    if (result.success) {
      loadStatus();
    } else {
      setError(result.error);
    }
  };

  const handleStageAll = async () => {
    const result = await window.electron.git.add(repoPath, '.');
    if (result.success) {
      loadStatus();
    } else {
      setError(result.error);
    }
  };

  const handleCommit = async () => {
    if (!commitMessage.trim()) {
      setError(t('commitMessage') + ' is required');
      return;
    }
    const result = await window.electron.git.commit(repoPath, commitMessage);
    if (result.success) {
      setCommitMessage('');
      loadStatus();
    } else {
      setError(result.error);
    }
  };

  const handlePush = async () => {
    if (!status) return;
    const result = await window.electron.git.push(repoPath, 'origin', status.current, {});
    if (result.success) {
      loadStatus();
    } else {
      setError(result.error);
    }
  };

  const handlePull = async () => {
    const result = await window.electron.git.pull(repoPath);
    if (result.success) {
      loadStatus();
    } else {
      setError(result.error);
    }
  };

  const handleFetch = async () => {
    const result = await window.electron.git.fetch(repoPath, 'origin');
    if (result.success) {
      loadStatus();
    } else {
      setError(result.error);
    }
  };

  if (loading) {
    return <div className="loading">{t('loading')}</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!status) {
    return <div className="error-message">{t('error')}</div>;
  }

  return (
    <div className="status-panel" role="region" aria-label={t('status')}>
      <div className="status-header">
        <h2>{t('status')}</h2>
        <div className="status-actions">
          <button onClick={handleFetch} className="btn-secondary" aria-label={t('fetch')}>
            {t('fetch')}
          </button>
          <button onClick={handlePull} className="btn-secondary" aria-label={t('pull')}>
            {t('pull')}
          </button>
          <button onClick={handlePush} className="btn-primary" aria-label={t('push')}>
            {t('push')}
          </button>
          <button onClick={loadStatus} className="btn-secondary" aria-label={t('refresh')}>
            {t('refresh')}
          </button>
        </div>
      </div>

      <div className="current-branch">
        <strong>{t('currentBranch')}:</strong>
        <span className="branch-name">{status.current}</span>
      </div>

      {status.staged && status.staged.length > 0 && (
        <div className="file-section">
          <h3>{t('stagedChanges')} ({status.staged.length})</h3>
          <div className="file-list">
            {status.staged.map((file, idx) => (
              <div key={idx} className="file-item staged">
                <span className="file-path">{file}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {(status.modified.length > 0 || status.not_added.length > 0) && (
        <div className="file-section">
          <h3>
            {t('unstagedChanges')} ({status.modified.length + status.not_added.length})
            <button onClick={handleStageAll} className="btn-success btn-sm" aria-label={t('stageAll')}>
              {t('stageAll')}
            </button>
          </h3>
          <div className="file-list">
            {status.modified.map((file, idx) => (
              <div key={idx} className="file-item modified">
                <span className="file-status">M</span>
                <span className="file-path">{file}</span>
                <button onClick={() => handleStage(file)} className="btn-stage">
                  {t('stage')}
                </button>
              </div>
            ))}
            {status.not_added.map((file, idx) => (
              <div key={idx} className="file-item new">
                <span className="file-status">A</span>
                <span className="file-path">{file}</span>
                <button onClick={() => handleStage(file)} className="btn-stage">
                  {t('stage')}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {status.staged && status.staged.length > 0 && (
        <div className="commit-section">
          <h3>{t('commit')}</h3>
          <textarea
            value={commitMessage}
            onChange={(e) => setCommitMessage(e.target.value)}
            placeholder={t('commitMessage')}
            className="commit-input"
          />
          <button onClick={handleCommit} className="btn-success" aria-label={t('commit')}>
            {t('commit')}
          </button>
        </div>
      )}

      {status.modified.length === 0 && 
       status.not_added.length === 0 && 
       status.staged.length === 0 && (
        <div className="clean-status">
          <p>✨ Working tree is clean!</p>
        </div>
      )}
    </div>
  );
}

export default StatusPanel;
