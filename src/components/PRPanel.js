import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './PRPanel.css';

function PRPanel({ repoPath, ghInstalled }) {
  const { t } = useTranslation();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [prs, setPrs] = useState([]);
  const [branches, setBranches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [prTitle, setPrTitle] = useState('');
  const [prBody, setPrBody] = useState('');
  const [baseBranch, setBaseBranch] = useState('main');
  const [headBranch, setHeadBranch] = useState('');

  useEffect(() => {
    if (ghInstalled) {
      loadPRs();
      loadBranches();
    } else {
      setLoading(false);
    }
  }, [repoPath, ghInstalled]);

  const loadPRs = async () => {
    setLoading(true);
    setError(null);
    const result = await window.electron.gh.listPRs(repoPath);
    if (result.success) {
      setPrs(result.data);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  const loadBranches = async () => {
    const result = await window.electron.git.branches(repoPath);
    if (result.success) {
      const localBranches = result.data.all.filter(b => !b.startsWith('remotes/'));
      setBranches(localBranches);
      setHeadBranch(result.data.current);
    }
  };

  const handleCreatePR = async (e) => {
    e.preventDefault();
    if (!prTitle.trim()) {
      setError('PR title is required');
      return;
    }
    
    const result = await window.electron.gh.createPR(
      repoPath, 
      prTitle, 
      prBody, 
      baseBranch, 
      headBranch
    );
    
    if (result.success) {
      setPrTitle('');
      setPrBody('');
      setShowCreateForm(false);
      loadPRs();
    } else {
      setError(result.error);
    }
  };

  if (!ghInstalled) {
    return (
      <div className="pr-panel">
        <div className="gh-not-installed">
          <h2>⚠️ {t('ghNotInstalled')}</h2>
          <p>{t('ghInstallPrompt')}</p>
          <a 
            href="https://cli.github.com/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="btn-primary"
          >
            Install GitHub CLI
          </a>
        </div>
      </div>
    );
  }

  if (loading) {
    return <div className="loading">{t('loading')}</div>;
  }

  return (
    <div className="pr-panel">
      <div className="pr-header">
        <h2>🔀 {t('pullRequests')}</h2>
        <button 
          onClick={() => setShowCreateForm(!showCreateForm)} 
          className="btn-success"
        >
          {showCreateForm ? '❌ ' + t('cancel') : '➕ ' + t('createPR')}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showCreateForm && (
        <div className="pr-create-form">
          <h3>✨ {t('createPR')}</h3>
          <form onSubmit={handleCreatePR}>
            <div className="form-group">
              <label>{t('prTitle')}</label>
              <input
                type="text"
                value={prTitle}
                onChange={(e) => setPrTitle(e.target.value)}
                placeholder={t('prTitle')}
                required
              />
            </div>

            <div className="form-group">
              <label>{t('prBody')}</label>
              <textarea
                value={prBody}
                onChange={(e) => setPrBody(e.target.value)}
                placeholder={t('prBody')}
                rows={6}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>{t('baseBranch')}</label>
                <select value={baseBranch} onChange={(e) => setBaseBranch(e.target.value)}>
                  {branches.map((branch, idx) => (
                    <option key={idx} value={branch}>{branch}</option>
                  ))}
                </select>
              </div>
              
              <div className="form-group">
                <label>{t('headBranch')}</label>
                <select value={headBranch} onChange={(e) => setHeadBranch(e.target.value)}>
                  {branches.map((branch, idx) => (
                    <option key={idx} value={branch}>{branch}</option>
                  ))}
                </select>
              </div>
            </div>

            <button type="submit" className="btn-success">
              🚀 {t('submit')}
            </button>
          </form>
        </div>
      )}

      <div className="pr-list-section">
        <h3>📋 {t('prList')}</h3>
        {prs.length === 0 ? (
          <div className="no-prs">No pull requests found</div>
        ) : (
          <div className="pr-list">
            {prs.map((pr, idx) => (
              <div key={idx} className="pr-item">
                <div className="pr-number">#{pr.number}</div>
                <div className="pr-content">
                  <div className="pr-title">{pr.title}</div>
                  <div className="pr-meta">
                    <span className={`pr-state ${pr.state}`}>{pr.state}</span>
                    <span className="pr-author">by {pr.author.login}</span>
                    <span className="pr-date">{new Date(pr.createdAt).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default PRPanel;
