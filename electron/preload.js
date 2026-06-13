const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  git: {
    status: (repoPath) => ipcRenderer.invoke('git:status', repoPath),
    log: (repoPath, options) => ipcRenderer.invoke('git:log', repoPath, options),
    branches: (repoPath) => ipcRenderer.invoke('git:branches', repoPath),
    checkout: (repoPath, branchName) => ipcRenderer.invoke('git:checkout', repoPath, branchName),
    createBranch: (repoPath, branchName) => ipcRenderer.invoke('git:createBranch', repoPath, branchName),
    add: (repoPath, files) => ipcRenderer.invoke('git:add', repoPath, files),
    commit: (repoPath, message) => ipcRenderer.invoke('git:commit', repoPath, message),
    push: (repoPath, remote, branch) => ipcRenderer.invoke('git:push', repoPath, remote, branch),
    pull: (repoPath) => ipcRenderer.invoke('git:pull', repoPath),
    diff: (repoPath, file) => ipcRenderer.invoke('git:diff', repoPath, file),
    clone: (url, targetPath) => ipcRenderer.invoke('git:clone', url, targetPath)
  },
  gh: {
    checkInstalled: () => ipcRenderer.invoke('gh:checkInstalled'),
    createPR: (repoPath, title, body, base, head) => ipcRenderer.invoke('gh:createPR', repoPath, title, body, base, head),
    listPRs: (repoPath) => ipcRenderer.invoke('gh:listPRs', repoPath),
    viewPR: (repoPath, prNumber) => ipcRenderer.invoke('gh:viewPR', repoPath, prNumber)
  },
  fs: {
    selectDirectory: () => ipcRenderer.invoke('fs:selectDirectory')
  },
  terminal: {
    execute: (repoPath, command) => ipcRenderer.invoke('terminal:execute', repoPath, command)
  }
});
