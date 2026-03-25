#!/usr/bin/env node
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const pythonCmd = process.platform === "win32" ? "python" : "python3";
const pkgRoot = path.resolve(__dirname, "..");

if (!fs.existsSync(path.join(pkgRoot, "skiba", "cli.py"))) {
  console.error("Error: skiba package not found. Is skiba installed correctly?");
  process.exit(1);
}

const child = spawn(pythonCmd, ["-m", "skiba.cli", ...process.argv.slice(2)], {
  cwd: pkgRoot,
  stdio: "inherit",
  env: { ...process.env }
});

child.on("exit", (code) => process.exit(code || 0));
child.on("error", (err) => {
  console.error("Failed to start Python:", err.message);
  process.exit(1);
});
