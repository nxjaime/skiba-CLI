#!/usr/bin/env node
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const pythonCmd = process.platform === "win32" ? "python" : "python3";
const scriptPath = path.resolve(__dirname, "../skiba/cli.py");

if (!fs.existsSync(scriptPath)) {
  console.error("Error: skiba/cli.py not found. Is skiba installed correctly?");
  process.exit(1);
}

const args = [scriptPath, ...process.argv.slice(2)];
const child = spawn(pythonCmd, args, {
  stdio: "inherit",
  env: { ...process.env }
});

child.on("exit", (code) => process.exit(code || 0));
child.on("error", (err) => {
  console.error("Failed to start Python:", err.message);
  process.exit(1);
});
