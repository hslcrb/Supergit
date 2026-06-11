import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './App.css';
import StatusPanel from './components/StatusPanel';
import BranchPanel from './components/BranchPanel';
import CommitPanel from './components/CommitPanel';
import PRPanel from './components/PRPanel';
import SettingsPanel from './components/SettingsPanel';

function App() {
  const { t } = useTranslation();
  const [repoPath, setRepoPath] = useState(null);
  const [activeTab, setActiveTab] = useState('status');
  const [ghInstalled, setGhInstalled] = useState(false);

  useEffect(() => {
    checkGhInstalled();
  }, []);

  const checkGhInstalled = async () => {
    if (window.electron) {
      const result = await window.electron.gh.checkInstalled();
      if (result.success) {
        setGhInstalled(result.installed);
      }
    }
  };

  const handleSelectRepo = async () => {
    if (window.electron) {
      const result = await window.electron.fs.selectDirectory();
      if (result.success) {
        setRepoPath(result.path);
      }
    }
  };

  const renderTabContent = () => {
    if (!repoPath) {
      return (
        <div className="no-repo">
          <h2>{t('noRepoSelected')}</h2>
          <p>{t('selectRepoPrompt')}</p>
          <button onClick={handleSelectRepo} className="btn-primary">
            {t('selectRepo')}
          </button>
        </div>
      );
    }

    switch (activeTab) {
      case 'status':
        return <StatusPanel repoPath={repoPath} />;
      case 'branches':
        return <BranchPanel repoPath={repoPath} />;
      case 'commits':
        return <CommitPanel repoPath={repoPath} />;
      case 'prs':
        return <PRPanel repoPath={repoPath} ghInstalled={ghInstalled} />;
      case 'settings':
        return <SettingsPanel />;
      default:
        return <StatusPanel repoPath={repoPath} />;
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🚀 {t('appName')}</h1>
        {repoPath && (
          <div className="repo-path">
            <span className="repo-label">{repoPath}</span>
            <button onClick={handleSelectRepo} className="btn-change">
              {t('selectRepo')}
            </button>
          </div>
        )}
      </header>
      <div className="app-body">
        <nav className="sidebar">
          <button
            className={`nav-button ${activeTab === 'status' ? 'active' : ''}`}
            onClick={() => setActiveTab('status')}
          >
            📊 {t('status')}
          </button>
          <button
            className={`nav-button ${activeTab === 'branches' ? 'active' : ''}`}
            onClick={() => setActiveTab('branches')}
          >
            🌿 {t('branches')}
          </button>
          <button
            className={`nav-button ${activeTab === 'commits' ? 'active' : ''}`}
            onClick={() => setActiveTab('commits')}
          >
            📝 {t('commits')}
          </button>
          <button
            className={`nav-button ${activeTab === 'prs' ? 'active' : ''}`}
            onClick={() => setActiveTab('prs')}
          >
            🔀 {t('pullRequests')}
            {!ghInstalled && <span className="warning-badge">!</span>}
          </button>
          <button
            className={`nav-button ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            ⚙️ {t('settings')}
          </button>
        </nav>
        <main className="content">
          {renderTabContent()}
        </main>
      </div>
    </div>
  );
}

export default App;
