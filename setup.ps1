# Purple - one-command first-run setup (Windows PowerShell)
#
#   powershell -ExecutionPolicy Bypass -File setup.ps1
#
# Idempotent: safe to re-run. Each step is best-effort and reports clearly; nothing
# here is destructive. Finish by running: python -m purple.selfcheck

$ErrorActionPreference = "Stop"
function Step($m) { Write-Host "`n=== $m ===" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "[ OK ] $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Have($cmd) { return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

Set-Location $PSScriptRoot

Step "Python check"
if (-not (Have python)) { Warn "Python not found - install 3.12 from python.org, then re-run."; exit 1 }
python --version | ForEach-Object { Ok $_ }

Step "Virtual environment + install"
if (-not (Test-Path ".venv")) { python -m venv .venv }
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip | Out-Null
pip install -e ".[dev]"
Ok "Project installed (editable, with dev tools)"

Step "Playwright browser"
try { python -m playwright install chromium; Ok "Chromium installed" }
catch { Warn "Playwright install failed - run: python -m playwright install chromium" }

Step "Config (.env)"
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env"; Ok "Created .env from template" }
else { Ok ".env already exists" }

Step "Ollama models"
if (Have ollama) {
    foreach ($m in @("qwen2.5:14b-instruct-q4_K_M", "nomic-embed-text")) {
        Write-Host "  pulling $m ..."
        try { ollama pull $m; Ok "pulled $m" } catch { Warn "could not pull $m" }
    }
} else { Warn "Ollama not found - install from ollama.com, then: ollama pull qwen2.5:14b-instruct-q4_K_M" }

Step "PostgreSQL database"
if (Have psql) {
    $superpw = Read-Host "  Postgres superuser ('postgres') password [press Enter to skip DB setup]"
    if ([string]::IsNullOrWhiteSpace($superpw)) {
        Warn "Skipped - create role + DB manually (see README), then re-run python -m purple.selfcheck"
    } else {
        $apppw = Read-Host "  Password to set for Purple's DB role 'purple' [Enter to keep 'purple']"
        if ([string]::IsNullOrWhiteSpace($apppw)) { $apppw = "purple" }
        $env:PGPASSWORD = $superpw
        # Create the role/db if missing (harmless 'already exists' on re-run), then force the
        # role password so it always matches what we write into .env below.
        try { psql -U postgres -h 127.0.0.1 -c "CREATE USER purple WITH PASSWORD '$apppw';" } catch {}
        psql -U postgres -h 127.0.0.1 -c "ALTER USER purple WITH PASSWORD '$apppw';"
        try { psql -U postgres -h 127.0.0.1 -c "CREATE DATABASE purple OWNER purple;" } catch {}
        psql -U postgres -h 127.0.0.1 -d purple -c "CREATE EXTENSION IF NOT EXISTS vector;"
        if ($LASTEXITCODE -eq 0) {
            # Keep .env's connection string in sync with the password we just set (single source of truth).
            if (Test-Path ".env") {
                (Get-Content ".env") -replace 'PURPLE_PG_DSN=postgresql\+asyncpg://purple:[^@]*@', "PURPLE_PG_DSN=postgresql+asyncpg://purple:$apppw@" | Set-Content ".env"
                Ok "Database 'purple' + pgvector ready; password synced into .env"
            } else {
                Ok "Database 'purple' + pgvector ready (no .env yet - set PURPLE_PG_DSN password to '$apppw')"
            }
        } else { Warn "pgvector step failed - is the pgvector extension installed for your Postgres? (see README)" }
    }
} else { Warn "psql not found - create DB 'purple' + role and run CREATE EXTENSION vector; manually (README)" }

Step "Kokoro voice model"
$kdir = "models\kokoro"
New-Item -ItemType Directory -Force -Path $kdir | Out-Null
if (-not (Test-Path "$kdir\kokoro-v1.0.onnx")) {
    $base = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
    try {
        Invoke-WebRequest "$base/kokoro-v1.0.onnx" -OutFile "$kdir\kokoro-v1.0.onnx"
        Invoke-WebRequest "$base/voices-v1.0.bin" -OutFile "$kdir\voices-v1.0.bin"
        Ok "Downloaded Kokoro voice model (af_bella + 50 others)"
    } catch { Warn "Kokoro download failed - grab kokoro-v1.0.onnx + voices-v1.0.bin into $kdir manually" }
} else { Ok "Kokoro voice model present" }

Step "Web UI (React, built with Vite - served at /ui/)"
if (-not (Have node)) {
    Warn "Node.js not found - installing via winget (or get it from nodejs.org)..."
    try { winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements } catch { Warn "winget install failed - install Node.js LTS manually, then re-run." }
}
if (Have npm) {
    Push-Location frontend
    try {
        npm install --no-audit --no-fund
        npm run build
        Ok "Web UI built -> opens at http://127.0.0.1:8765/ui/ on startup"
    } catch { Warn "Web UI build failed - run manually: cd frontend; npm install; npm run build" }
    Pop-Location
} else {
    Warn "npm not on PATH yet (open a NEW terminal after installing Node), then: cd frontend; npm install; npm run build"
}

Step "Self-check"
python -m purple.selfcheck

Write-Host "`nSetup complete. Start Purple with:  purple   (or: python -m purple.run)" -ForegroundColor Cyan
Write-Host "The web UI opens automatically at http://127.0.0.1:8765/ui/" -ForegroundColor Cyan
Write-Host "For the native desktop app (Tauri), run:  powershell -ExecutionPolicy Bypass -File scripts\build_tauri.ps1" -ForegroundColor DarkGray
