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
    backgroundColor: '#ffffff'
  });

  mainWindow.loadURL(
    isDev
      ? 'http://localhost:3000'
      : `file://${path.join(__dirname, '../build/index.html')}`
  );

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }
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
    return { success: true, data: status };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('git:log', async (event, repoPath, options = {}) => {
  try {
    const git = simpleGit(repoPath);
    const log = await git.log(options);
    return { success: true, data: log };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('git:branches', async (event, repoPath) => {
  try {
    const git = simpleGit(repoPath);
    const branches = await git.branch();
    return { success: true, data: branches };
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
    return { success: true, data: result };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('git:push', async (event, repoPath, remote, branch) => {
  try {
    const git = simpleGit(repoPath);
    await git.push(remote, branch);
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
    return { success: true, data: diff };
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
