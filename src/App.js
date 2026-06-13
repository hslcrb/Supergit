import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './App.css';
import StatusPanel from './components/StatusPanel';
import BranchPanel from './components/BranchPanel';
import CommitPanel from './components/CommitPanel';
import PRPanel from './components/PRPanel';
import TerminalPanel from './components/TerminalPanel';
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

  const tabs = [
    { id: 'status', label: t('status'), key: 'Alt+1' },
    { id: 'branches', label: t('branches'), key: 'Alt+2' },
    { id: 'commits', label: t('commits'), key: 'Alt+3' },
    { id: 'prs', label: t('pullRequests'), key: 'Alt+4', warning: !ghInstalled },
    { id: 'terminal', label: t('terminal'), key: 'Alt+5' },
    { id: 'settings', label: t('settings'), key: 'Alt+6' }
  ];

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.altKey && e.key >= '1' && e.key <= '6') {
        e.preventDefault();
        const index = parseInt(e.key) - 1;
        if (tabs[index]) {
          setActiveTab(tabs[index].id);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const renderTabContent = () => {
    if (!repoPath && activeTab !== 'settings') {
      return (
        <div className="no-repo" role="main" aria-live="polite">
          <h2>{t('noRepoSelected')}</h2>
          <p>{t('selectRepoPrompt')}</p>
          <button 
            onClick={handleSelectRepo} 
            className="btn-primary"
            aria-label={t('selectRepo')}
          >
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
      case 'terminal':
        return <TerminalPanel repoPath={repoPath} />;
      case 'settings':
        return <SettingsPanel />;
      default:
        return <StatusPanel repoPath={repoPath} />;
    }
  };

  return (
    <div className="App">
      <header className="app-header" role="banner">
        <h1 className="app-title">{t('appName')}</h1>
        {repoPath && (
          <div className="repo-path">
            <span className="repo-label" title={repoPath}>{repoPath}</span>
            <button 
              onClick={handleSelectRepo} 
              className="btn-change"
              aria-label={t('changeRepo')}
            >
              {t('change')}
            </button>
          </div>
        )}
      </header>
      <nav className="tab-nav" role="navigation" aria-label={t('mainNavigation')}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
            role="tab"
            aria-selected={activeTab === tab.id}
            aria-controls={`panel-${tab.id}`}
            aria-label={`${tab.label} (${tab.key})`}
            title={`${tab.label} (${tab.key})`}
          >
            {tab.label}
            {tab.warning && <span className="warning-dot" aria-label={t('warning')}></span>}
          </button>
        ))}
      </nav>
      <main 
        className="content" 
        role="main"
        id={`panel-${activeTab}`}
        aria-labelledby={`tab-${activeTab}`}
      >
        {renderTabContent()}
      </main>
    </div>
  );
}

export default App;
