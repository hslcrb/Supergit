const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const simpleGit = require('simple-git');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 900,
    height: 700,
    minWidth: 600,
    minHeight: 400,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '../assets/icon.png'),
    resizable: true,
    maximizable: true,
    backgroundColor: '#ffffff',
    show: false
  });

  const startUrl = isDev
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../build/index.html')}`;

  mainWindow.loadURL(startUrl);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Debug: Log any errors
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error('Failed to load:', errorCode, errorDescription);
  });

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  // Debug in production too
  mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
    console.log(`Console [${level}]:`, message);
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Git operations
ipcMain.handle('git:status', async (event, repoPath) => {
  try {
    const git = simpleGit(repoPath);
    const status = await git.status();
    // Convert to plain object for IPC
    const plainStatus = {
      current: status.current,
      tracking: status.tracking,
      ahead: status.ahead,
      behind: status.behind,
      staged: status.staged || [],
      modified: status.modified || [],
      created: status.created || [],
      deleted: status.deleted || [],
      renamed: status.renamed || [],
      files: status.files || [],
      not_added: status.not_added || [],
      conflicted: status.conflicted || [],
      isClean: status.isClean
    };
    return { success: true, data: plainStatus };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('git:log', async (event, repoPath, options = {}) => {
  try {
    const git = simpleGit(repoPath);
    const log = await git.log(options);
    // Convert to plain object for IPC
    const plainLog = {
      all: log.all.map(commit => ({
        hash: commit.hash,
        date: commit.date,
        message: commit.message,
        body: commit.body,
        author_name: commit.author_name,
        author_email: commit.author_email
      })),
      total: log.total,
      latest: log.latest ? {
        hash: log.latest.hash,
        date: log.latest.date,
        message: log.latest.message,
        author_name: log.latest.author_name
      } : null
    };
    return { success: true, data: plainLog };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('git:branches', async (event, repoPath) => {
  try {
    const git = simpleGit(repoPath);
    const branches = await git.branch();
    // Convert to plain object for IPC
    const plainBranches = {
      all: branches.all || [],
      current: branches.current,
      branches: {}
    };
    // Convert branches object to plain object
    if (branches.branches) {
      Object.keys(branches.branches).forEach(key => {
        plainBranches.branches[key] = {
          current: branches.branches[key].current,
          name: branches.branches[key].name,
          commit: branches.branches[key].commit,
          label: branches.branches[key].label
        };
      });
    }
    return { success: true, data: plainBranches };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('git:checkout', async (event, repoPath, branchName) => {
  try {
    const git = simpleGit(repoPath);
    await git.checkout(branchName);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('git:createBranch', async (event, repoPath, branchName) => {
  try {
    const git = simpleGit(repoPath);
    await git.checkoutLocalBranch(branchName);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('git:add', async (event, repoPath, files) => {
  try {
    const git = simpleGit(repoPath);
    await git.add(files);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('git:commit', async (event, repoPath, message) => {
  try {
    const git = simpleGit(repoPath);
    const result = await git.commit(message);
    // Convert to plain object
    const plainResult = {
      commit: result.commit,
      branch: result.branch,
      summary: result.summary ? {
        changes: result.summary.changes,
        insertions: result.summary.insertions,
        deletions: result.summary.deletions
      } : null
    };
    return { success: true, data: plainResult };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('git:push', async (event, repoPath, remote, branch, options = {}) => {
  try {
    const git = simpleGit(repoPath);
    await git.push(remote, branch, options);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('git:pushCommit', async (event, repoPath, remote, commitHash) => {
  try {
    const git = simpleGit(repoPath);
    await git.push(remote, `${commitHash}:refs/heads/temp-push`, ['--force']);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('git:fetch', async (event, repoPath, remote) => {
  try {
    const git = simpleGit(repoPath);
    await git.fetch(remote || 'origin');
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('git:pullCommit', async (event, repoPath, commitHash) => {
  try {
    const git = simpleGit(repoPath);
    await git.raw(['cherry-pick', commitHash]);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('git:pull', async (event, repoPath) => {
  try {
    const git = simpleGit(repoPath);
    await git.pull();
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('git:diff', async (event, repoPath, file) => {
  try {
    const git = simpleGit(repoPath);
    const diff = await git.diff([file]);
    // Return as string (already serializable)
    return { success: true, data: String(diff) };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('git:clone', async (event, url, targetPath) => {
  try {
    await simpleGit().clone(url, targetPath);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// GitHub CLI operations
ipcMain.handle('gh:checkInstalled', async () => {
  try {
    await execAsync('gh --version');
    return { success: true, installed: true };
  } catch (error) {
    return { success: true, installed: false };
  }
});

ipcMain.handle('gh:createPR', async (event, repoPath, title, body, base, head) => {
  try {
    const command = `gh pr create --title "${title}" --body "${body}" --base ${base} --head ${head}`;
    const { stdout } = await execAsync(command, { cwd: repoPath });
    return { success: true, data: stdout };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('gh:listPRs', async (event, repoPath) => {
  try {
    const { stdout } = await execAsync('gh pr list --json number,title,state,author,createdAt', { cwd: repoPath });
    return { success: true, data: JSON.parse(stdout) };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('gh:viewPR', async (event, repoPath, prNumber) => {
  try {
    const { stdout } = await execAsync(`gh pr view ${prNumber} --json number,title,body,state,author,createdAt,mergeable`, { cwd: repoPath });
    return { success: true, data: JSON.parse(stdout) };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// File system operations
ipcMain.handle('fs:selectDirectory', async () => {
  const { dialog } = require('electron');
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  
  if (!result.canceled && result.filePaths.length > 0) {
    return { success: true, path: result.filePaths[0] };
  }
  return { success: false };
});

// Terminal operations
ipcMain.handle('terminal:execute', async (event, repoPath, command) => {
  try {
    const { stdout, stderr } = await execAsync(command, { 
      cwd: repoPath,
      timeout: 30000,
      maxBuffer: 1024 * 1024 * 5
    });
    return { success: true, output: stdout || stderr };
  } catch (error) {
    return { success: false, error: error.message, output: error.stderr || error.stdout };
  }
});
