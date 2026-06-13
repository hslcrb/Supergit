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
    <div className="settings-panel" role="region" aria-label={t('settings')}>
      <h2>{t('settings')}</h2>
      
      <div className="settings-section">
        <h3>{t('language')}</h3>
        <div className="language-options" role="group" aria-label={t('language')}>
          <button
            className={`language-btn ${i18n.language === 'ko' ? 'active' : ''}`}
            onClick={() => handleLanguageChange('ko')}
            aria-pressed={i18n.language === 'ko'}
            aria-label={t('korean')}
          >
            {t('korean')}
          </button>
          <button
            className={`language-btn ${i18n.language === 'en' ? 'active' : ''}`}
            onClick={() => handleLanguageChange('en')}
            aria-pressed={i18n.language === 'en'}
            aria-label={t('english')}
          >
            {t('english')}
          </button>
        </div>
      </div>

      <div className="settings-section">
        <h3>About Supergit</h3>
        <div className="about-info">
          <p><strong>Version:</strong> 1.0.0</p>
          <p><strong>Description:</strong> Easy-to-use Git and GitHub CLI GUI</p>
          <p><strong>License:</strong> MIT</p>
          <div className="features-list">
            <h4>Features:</h4>
            <ul>
              <li>Git Status Management</li>
              <li>Branch Operations</li>
              <li>Commit History</li>
              <li>Pull Request Creation (with gh CLI)</li>
              <li>Integrated Terminal</li>
              <li>Multi-language Support (Korean/English)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPanel;
