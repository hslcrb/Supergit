import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './BranchPanel.css';

function BranchPanel({ repoPath }) {
  const { t } = useTranslation();
  const [branches, setBranches] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newBranchName, setNewBranchName] = useState('');

  useEffect(() => {
    loadBranches();
  }, [repoPath]);

  const loadBranches = async () => {
    setLoading(true);
    setError(null);
    const result = await window.electron.git.branches(repoPath);
    if (result.success) {
      setBranches(result.data);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  const handleCheckout = async (branchName) => {
    const result = await window.electron.git.checkout(repoPath, branchName);
    if (result.success) {
      loadBranches();
    } else {
      setError(result.error);
    }
  };

  const handleCreateBranch = async () => {
    if (!newBranchName.trim()) {
      setError('Branch name is required');
      return;
    }
    const result = await window.electron.git.createBranch(repoPath, newBranchName);
    if (result.success) {
      setNewBranchName('');
      setShowCreateModal(false);
      loadBranches();
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

  if (!branches) {
    return <div className="error-message">{t('error')}</div>;
  }

  return (
    <div className="branch-panel">
      <div className="branch-header">
        <h2>🌿 {t('branches')}</h2>
        <button onClick={() => setShowCreateModal(true)} className="btn-success">
          ➕ {t('createBranch')}
        </button>
      </div>

      <div className="current-branch-display">
        <strong>{t('currentBranch')}:</strong>
        <span className="branch-tag current">{branches.current}</span>
      </div>

      <div className="branch-sections">
        <div className="branch-section">
          <h3>📍 Local Branches</h3>
          <div className="branch-list">
            {branches.all
              .filter(b => !b.startsWith('remotes/'))
              .map((branch, idx) => {
                const isCurrent = branch === branches.current;
                return (
                  <div key={idx} className={`branch-item ${isCurrent ? 'current' : ''}`}>
                    <span className="branch-icon">{isCurrent ? '●' : '○'}</span>
                    <span className="branch-name">{branch}</span>
                    {!isCurrent && (
                      <button
                        onClick={() => handleCheckout(branch)}
                        className="btn-checkout"
                      >
                        {t('checkout')}
                      </button>
                    )}
                  </div>
                );
              })}
          </div>
        </div>

        {branches.all.filter(b => b.startsWith('remotes/')).length > 0 && (
          <div className="branch-section">
            <h3>🌐 Remote Branches</h3>
            <div className="branch-list">
              {branches.all
                .filter(b => b.startsWith('remotes/'))
                .map((branch, idx) => (
                  <div key={idx} className="branch-item remote">
                    <span className="branch-icon">🔗</span>
                    <span className="branch-name">{branch}</span>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>{t('createBranch')}</h3>
            <input
              type="text"
              value={newBranchName}
              onChange={(e) => setNewBranchName(e.target.value)}
              placeholder={t('newBranchName')}
              className="branch-input"
              autoFocus
            />
            <div className="modal-actions">
              <button onClick={handleCreateBranch} className="btn-success">
                {t('create')}
              </button>
              <button onClick={() => setShowCreateModal(false)} className="btn-secondary">
                {t('cancel')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default BranchPanel;
