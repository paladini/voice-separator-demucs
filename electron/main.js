const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const si = require('systeminformation');

let mainWindow;
let backendProcess = null;
let backendPort = 7860; // default FastAPI port

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1100,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    icon: path.join(__dirname, 'icon.png'),
    title: 'Voice Separator',
  });
  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));
}

function startBackend() {
  if (backendProcess) return;
  const pythonPath = process.env.PYTHON_PATH || 'python3';
  const backendScript = path.join(__dirname, '..', 'main.py');
  backendProcess = spawn(pythonPath, [backendScript], {
    cwd: path.join(__dirname, '..'),
    env: { ...process.env, UVICORN_PORT: backendPort },
    stdio: 'ignore',
    detached: true,
  });
  backendProcess.unref();
}

function stopBackend() {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
}

app.on('ready', () => {
  startBackend();
  createWindow();
});

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

// IPC: Hardware info
ipcMain.handle('get-hardware-info', async () => {
  const cpu = await si.cpu();
  const mem = await si.mem();
  const gpuArr = await si.graphics();
  return {
    cpu: cpu.manufacturer + ' ' + cpu.brand,
    cores: cpu.cores,
    ram: Math.round(mem.total / (1024 * 1024 * 1024)),
    gpu: gpuArr.controllers && gpuArr.controllers.length > 0 ? gpuArr.controllers[0].model : 'None',
  };
});

// IPC: File dialogs
ipcMain.handle('show-open-dialog', async (event, opts) => {
  return await dialog.showOpenDialog(mainWindow, opts);
});
ipcMain.handle('show-save-dialog', async (event, opts) => {
  return await dialog.showSaveDialog(mainWindow, opts);
});

// IPC: Open output folder
ipcMain.handle('open-output-folder', async () => {
  const outputPath = path.join(__dirname, '..', 'static', 'output');
  require('electron').shell.openPath(outputPath);
});

// IPC: Stop backend (for quit)
ipcMain.handle('stop-backend', () => {
  stopBackend();
});
