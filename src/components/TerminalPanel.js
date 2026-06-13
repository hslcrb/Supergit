import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './TerminalPanel.css';

function TerminalPanel({ repoPath }) {
  const { t } = useTranslation();
  const [command, setCommand] = useState('');
  const [history, setHistory] = useState([]);
  const [commandHistory, setCommandHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const inputRef = useRef(null);
  const historyEndRef = useRef(null);

  useEffect(() => {
    historyEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  const executeCommand = async (cmd) => {
    if (!cmd.trim()) return;

    const newEntry = { command: cmd, output: '', timestamp: new Date() };
    setHistory(prev => [...prev, newEntry]);
    setCommandHistory(prev => [...prev, cmd]);
    setCommand('');
    setHistoryIndex(-1);

    if (window.electron && window.electron.terminal) {
      const result = await window.electron.terminal.execute(repoPath, cmd);
      setHistory(prev => {
        const updated = [...prev];
        updated[updated.length - 1].output = result.success 
          ? result.output 
          : `Error: ${result.error}`;
        updated[updated.length - 1].error = !result.success;
        return updated;
      });
    } else {
      setHistory(prev => {
        const updated = [...prev];
        updated[updated.length - 1].output = 'Terminal not available';
        updated[updated.length - 1].error = true;
        return updated;
      });
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      executeCommand(command);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (commandHistory.length > 0) {
        const newIndex = historyIndex < commandHistory.length - 1 
          ? historyIndex + 1 
          : historyIndex;
        setHistoryIndex(newIndex);
        setCommand(commandHistory[commandHistory.length - 1 - newIndex]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setCommand(commandHistory[commandHistory.length - 1 - newIndex]);
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setCommand('');
      }
    }
  };

  const clearHistory = () => {
    setHistory([]);
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { hour12: false });
  };

  return (
    <div className="terminal-panel" role="region" aria-label={t('terminal')}>
      <div className="terminal-header">
        <h2>{t('terminal')}</h2>
        <button 
          onClick={clearHistory} 
          className="btn-secondary"
          aria-label={t('clear')}
        >
          {t('clear')}
        </button>
      </div>
      <div className="terminal-output" role="log" aria-live="polite" aria-atomic="false">
        {history.map((entry, idx) => (
          <div key={idx} className="terminal-entry">
            <div className="terminal-command">
              <span className="terminal-prompt" aria-hidden="true">$</span>
              <span className="terminal-time">[{formatTime(entry.timestamp)}]</span>
              <span className="command-text">{entry.command}</span>
            </div>
            {entry.output && (
              <pre 
                className={`terminal-result ${entry.error ? 'error' : ''}`}
                role={entry.error ? 'alert' : 'status'}
              >
                {entry.output}
              </pre>
            )}
          </div>
        ))}
        <div ref={historyEndRef} />
      </div>
      <div className="terminal-input-container">
        <label htmlFor="terminal-input" className="sr-only">
          {t('commandInput')}
        </label>
        <span className="terminal-prompt" aria-hidden="true">$</span>
        <input
          id="terminal-input"
          ref={inputRef}
          type="text"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          onKeyDown={handleKeyDown}
          className="terminal-input"
          placeholder={t('enterCommand')}
          aria-label={t('commandInput')}
          aria-describedby="terminal-help"
          autoComplete="off"
          spellCheck="false"
        />
      </div>
      <div id="terminal-help" className="sr-only">
        {t('terminalHelp')}
      </div>
    </div>
  );
}

export default TerminalPanel;
