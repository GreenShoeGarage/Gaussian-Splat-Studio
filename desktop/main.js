const { app, BrowserWindow, dialog } = require("electron");
const { spawn, execSync } = require("child_process");
const path = require("path");

let composeProcess = null;

function dockerAvailable() {
  try { execSync("docker --version", { stdio: "ignore" }); return true; }
  catch { return false; }
}

function startCompose() {
  if (!dockerAvailable()) {
    dialog.showErrorBox("Docker Desktop required", "Install Docker Desktop, then reopen Maker Splat.");
    return;
  }
  const projectRoot = path.resolve(__dirname, "..");
  composeProcess = spawn("docker", ["compose", "up", "--build"], {
    cwd: projectRoot,
    shell: process.platform === "win32",
    stdio: "inherit"
  });
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1320,
    height: 900,
    title: "Maker Splat",
    backgroundColor: "#17120d",
    webPreferences: { contextIsolation: true }
  });
  setTimeout(() => win.loadURL("http://localhost:5173"), 3500);
}

app.whenReady().then(() => { startCompose(); createWindow(); });
app.on("window-all-closed", () => {
  if (composeProcess) { try { composeProcess.kill(); } catch {} }
  if (process.platform !== "darwin") app.quit();
});
