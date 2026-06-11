import React from 'react';
import { useTranslation } from 'react-i18next';
import './SettingsPanel.css';

function SettingsPanel() {
  const { t, i18n } = useTranslation();

  const handleLanguageChange = (lang) => {
    i18n.changeLanguage(lang);
    localStorage.setItem('supergit-language', lang);
  };

  return (
    <div className="settings-panel">
      <h2>⚙️ {t('settings')}</h2>
      
      <div className="settings-section">
        <h3>🌐 {t('language')}</h3>
        <div className="language-options">
          <button
            className={`language-btn ${i18n.language === 'ko' ? 'active' : ''}`}
            onClick={() => handleLanguageChange('ko')}
          >
            🇰🇷 {t('korean')}
          </button>
          <button
            className={`language-btn ${i18n.language === 'en' ? 'active' : ''}`}
            onClick={() => handleLanguageChange('en')}
          >
            🇺🇸 {t('english')}
          </button>
        </div>
      </div>

      <div className="settings-section">
        <h3>ℹ️ About Supergit</h3>
        <div className="about-info">
          <p><strong>Version:</strong> 1.0.0</p>
          <p><strong>Description:</strong> Easy-to-use Git and GitHub CLI GUI</p>
          <p><strong>License:</strong> MIT</p>
          <div className="features-list">
            <h4>✨ Features:</h4>
            <ul>
              <li>📊 Git Status Management</li>
              <li>🌿 Branch Operations</li>
              <li>📝 Commit History</li>
              <li>🔀 Pull Request Creation (with gh CLI)</li>
              <li>🌐 Multi-language Support (Korean/English)</li>
              <li>🎨 Beautiful Dark Theme</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPanel;
