# Build/run Purple as a NATIVE desktop app (Tauri) - the same React UI in its own window.
#
#   powershell -ExecutionPolicy Bypass -File scripts\build_tauri.ps1
#
# Heavier than the web UI: needs Node AND the Rust toolchain (+ "Desktop development
# with C++" / VS Build Tools on Windows). The first build downloads and compiles a lot,
# so it can take several minutes. The plain web UI (http://127.0.0.1:8765/ui/) needs none
# of this - use Tauri only if you want a standalone window.

$ErrorActionPreference = "Stop"
function Have($c) { return [bool](Get-Command $c -ErrorAction SilentlyContinue) }
Set-Location (Join-Path $PSScriptRoot "..\frontend")

if (-not (Have node)) { Write-Host "Install Node.js LTS first (https://nodejs.org), then re-run." -ForegroundColor Yellow; exit 1 }

if (-not (Have cargo)) {
    Write-Host "Rust not found - installing rustup..." -ForegroundColor Cyan
    try { winget install -e --id Rustlang.Rustup --accept-source-agreements --accept-package-agreements } catch {}
    Write-Host "If 'cargo' still isn't found after this, install Rust from https://rustup.rs and the" -ForegroundColor Yellow
    Write-Host "'Desktop development with C++' workload (Visual Studio Build Tools), then re-run." -ForegroundColor Yellow
}

npm install --no-audit --no-fund

if (-not (Test-Path "src-tauri")) {
    Write-Host "Scaffolding the Tauri app (one time)..." -ForegroundColor Cyan
    # Non-interactive scaffold wired to this Vite project. If your Tauri CLI rejects a flag,
    # run `npm run tauri init` interactively and answer:
    #   frontend dev command : npm run dev
    #   frontend build command: npm run build
    #   dev server URL        : http://localhost:5173
    #   web assets (dist)     : ../../src/purple/web
    npm run tauri init -- --ci `
        --app-name "Purple" `
        --window-title "Purple" `
        --frontend-dist "../../src/purple/web" `
        --dev-url "http://localhost:5173" `
        --before-dev-command "npm run dev" `
        --before-build-command "npm run build"
}

Write-Host "`nLaunching the Purple desktop window (live dev mode)..." -ForegroundColor Cyan
Write-Host "To produce an installable .exe instead, run:  npm run tauri build" -ForegroundColor DarkGray
npm run tauri dev
