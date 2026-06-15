import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './CommitPanel.css';

function CommitPanel({ repoPath }) {
  const { t } = useTranslation();
  const [commits, setCommits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [selectedCommit, setSelectedCommit] = useState(null);
  const [currentBranch, setCurrentBranch] = useState('main');

  useEffect(() => {
    loadCommits();
    loadCurrentBranch();
  }, [repoPath]);

  const loadCommits = async () => {
    setLoading(true);
    setError(null);
    const result = await window.electron.git.log(repoPath, { maxCount: 100 });
    if (result.success) {
      setCommits(result.data.all);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  const loadCurrentBranch = async () => {
    const result = await window.electron.git.status(repoPath);
    if (result.success) {
      setCurrentBranch(result.data.current);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const handleViewCommit = (commit) => {
    setSelectedCommit(selectedCommit?.hash === commit.hash ? null : commit);
  };

  const handlePushCommit = async (commitHash) => {
    setError(null);
    setSuccess(null);
    const result = await window.electron.git.pushCommit(repoPath, 'origin', commitHash);
    if (result.success) {
      setSuccess(t('commitPushedSuccess'));
    } else {
      setError(result.error);
    }
    setTimeout(() => setSuccess(null), 3000);
  };

  const handlePullCommit = async (commitHash) => {
    setError(null);
    setSuccess(null);
    const result = await window.electron.git.pullCommit(repoPath, commitHash);
    if (result.success) {
      setSuccess(t('commitPulledSuccess'));
      loadCommits();
    } else {
      setError(result.error);
    }
    setTimeout(() => setSuccess(null), 3000);
  };

  const handlePushAll = async () => {
    setError(null);
    setSuccess(null);
    const result = await window.electron.git.push(repoPath, 'origin', currentBranch);
    if (result.success) {
      setSuccess(t('pushSuccess'));
    } else {
      setError(result.error);
    }
    setTimeout(() => setSuccess(null), 3000);
  };

  const handlePullAll = async () => {
    setError(null);
    setSuccess(null);
    const result = await window.electron.git.pull(repoPath);
    if (result.success) {
      setSuccess(t('pullSuccess'));
      loadCommits();
    } else {
      setError(result.error);
    }
    setTimeout(() => setSuccess(null), 3000);
  };

  const handleFetch = async () => {
    setError(null);
    setSuccess(null);
    const result = await window.electron.git.fetch(repoPath, 'origin');
    if (result.success) {
      setSuccess(t('fetchSuccess'));
      loadCommits();
    } else {
      setError(result.error);
    }
    setTimeout(() => setSuccess(null), 3000);
  };

  if (loading) {
    return <div className="loading">{t('loading')}</div>;
  }

  return (
    <div className="commit-panel" role="region" aria-label={t('commitHistory')}>
      <div className="commit-header">
        <h2>{t('commitHistory')}</h2>
        <div className="commit-actions">
          <button onClick={handleFetch} className="btn-secondary" aria-label={t('fetch')}>
            {t('fetch')}
          </button>
          <button onClick={handlePullAll} className="btn-secondary" aria-label={t('pullAll')}>
            {t('pullAll')}
          </button>
          <button onClick={handlePushAll} className="btn-primary" aria-label={t('pushAll')}>
            {t('pushAll')}
          </button>
          <button onClick={loadCommits} className="btn-secondary" aria-label={t('refresh')}>
            {t('refresh')}
          </button>
        </div>
      </div>

      {error && <div className="error-message" role="alert">{error}</div>}
      {success && <div className="success-message" role="status">{success}</div>}

      <div className="commit-list">
        {commits.map((commit, idx) => (
          <div key={idx} className="commit-item-container">
            <div 
              className={`commit-item ${selectedCommit?.hash === commit.hash ? 'selected' : ''}`}
              onClick={() => handleViewCommit(commit)}
              role="button"
              tabIndex={0}
              aria-expanded={selectedCommit?.hash === commit.hash}
              aria-label={`${commit.message} by ${commit.author_name}`}
            >
              <div className="commit-hash">{commit.hash.substring(0, 7)}</div>
              <div className="commit-details">
                <div className="commit-message">{commit.message}</div>
                <div className="commit-meta">
                  <span className="commit-author">{commit.author_name}</span>
                  <span className="commit-date">{formatDate(commit.date)}</span>
                </div>
              </div>
              <div className="commit-actions-inline">
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    handlePushCommit(commit.hash);
                  }}
                  className="btn-sm btn-primary"
                  aria-label={`${t('push')} ${commit.hash.substring(0, 7)}`}
                  title={t('pushThisCommit')}
                >
                  {t('push')}
                </button>
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    handlePullCommit(commit.hash);
                  }}
                  className="btn-sm btn-secondary"
                  aria-label={`${t('cherryPick')} ${commit.hash.substring(0, 7)}`}
                  title={t('cherryPickCommit')}
                >
                  {t('cherryPick')}
                </button>
              </div>
            </div>
            {selectedCommit?.hash === commit.hash && (
              <div className="commit-expanded">
                <div className="commit-info-grid">
                  <div className="info-row">
                    <strong>{t('hash')}:</strong>
                    <code>{commit.hash}</code>
                  </div>
                  <div className="info-row">
                    <strong>{t('author')}:</strong>
                    <span>{commit.author_name} &lt;{commit.author_email}&gt;</span>
                  </div>
                  <div className="info-row">
                    <strong>{t('date')}:</strong>
                    <span>{formatDate(commit.date)}</span>
                  </div>
                </div>
                {commit.body && (
                  <div className="commit-body">
                    <strong>{t('message')}:</strong>
                    <pre>{commit.body}</pre>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default CommitPanel;
