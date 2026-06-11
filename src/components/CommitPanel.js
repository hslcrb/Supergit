import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './CommitPanel.css';

function CommitPanel({ repoPath }) {
  const { t } = useTranslation();
  const [commits, setCommits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCommit, setSelectedCommit] = useState(null);

  useEffect(() => {
    loadCommits();
  }, [repoPath]);

  const loadCommits = async () => {
    setLoading(true);
    setError(null);
    const result = await window.electron.git.log(repoPath, { maxCount: 50 });
    if (result.success) {
      setCommits(result.data.all);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const handleViewCommit = (commit) => {
    setSelectedCommit(selectedCommit?.hash === commit.hash ? null : commit);
  };

  if (loading) {
    return <div className="loading">{t('loading')}</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="commit-panel">
      <div className="commit-header">
        <h2>📝 {t('commitHistory')}</h2>
        <button onClick={loadCommits} className="btn-secondary">
          🔄 {t('refresh')}
        </button>
      </div>

      <div className="commit-list">
        {commits.map((commit, idx) => (
          <div key={idx} className="commit-item-container">
            <div 
              className={`commit-item ${selectedCommit?.hash === commit.hash ? 'selected' : ''}`}
              onClick={() => handleViewCommit(commit)}
            >
              <div className="commit-hash">{commit.hash.substring(0, 7)}</div>
              <div className="commit-details">
                <div className="commit-message">{commit.message}</div>
                <div className="commit-meta">
                  <span className="commit-author">👤 {commit.author_name}</span>
                  <span className="commit-date">🕐 {formatDate(commit.date)}</span>
                </div>
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
