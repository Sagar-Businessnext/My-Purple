# Purple — one-command first-run setup (Windows PowerShell)
#
#   powershell -ExecutionPolicy Bypass -File setup.ps1
#
# Idempotent: safe to re-run. Each step is best-effort and reports clearly; nothing
# here is destructive. Finish by running `python -m purple.selfcheck`.

$ErrorActionPreference = "Stop"
function Step($m) { Write-Host "`n=== $m ===" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "[ OK ] $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Have($cmd) { return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

Set-Location $PSScriptRoot

Step "Python check"
if (-not (Have python)) { Warn "Python not found — install 3.12 from python.org, then re-run."; exit 1 }
python --version | ForEach-Object { Ok $_ }

Step "Virtual environment + install"
if (-not (Test-Path ".venv")) { python -m venv .venv }
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip | Out-Null
pip install -e ".[dev]"
Ok "Project installed (editable, with dev tools)"

Step "Playwright browser"
try { python -m playwright install chromium; Ok "Chromium installed" }
catch { Warn "Playwright install failed — run `python -m playwright install chromium` manually" }

Step "Config (.env)"
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env"; Ok "Created .env from template" }
else { Ok ".env already exists" }

Step "Ollama models"
if (Have ollama) {
    foreach ($m in @("qwen2.5:14b-instruct-q4_K_M", "nomic-embed-text")) {
        Write-Host "  pulling $m ..."
        try { ollama pull $m; Ok "pulled $m" } catch { Warn "could not pull $m" }
    }
} else { Warn "Ollama not found — install from ollama.com, then `ollama pull qwen2.5:14b-instruct-q4_K_M`" }

Step "PostgreSQL database"
if (Have psql) {
    $env:PGPASSWORD = "postgres"
    $sql = "CREATE DATABASE purple;","CREATE USER purple WITH PASSWORD 'purple';","GRANT ALL PRIVILEGES ON DATABASE purple TO purple;"
    foreach ($s in $sql) { try { psql -U postgres -h 127.0.0.1 -c $s 2>$null } catch {} }
    try { psql -U postgres -h 127.0.0.1 -d purple -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>$null; Ok "Database 'purple' + pgvector ready" }
    catch { Warn "Could not enable pgvector — ensure the pgvector extension is installed for your Postgres" }
} else { Warn "psql not found — create DB 'purple' and run CREATE EXTENSION vector; manually (see README)" }

Step "Kokoro voice model"
$kdir = "models\kokoro"
New-Item -ItemType Directory -Force -Path $kdir | Out-Null
if (-not (Test-Path "$kdir\kokoro-v1.0.onnx")) {
    $base = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
    try {
        Invoke-WebRequest "$base/kokoro-v1.0.onnx" -OutFile "$kdir\kokoro-v1.0.onnx"
        Invoke-WebRequest "$base/voices-v1.0.bin" -OutFile "$kdir\voices-v1.0.bin"
        Ok "Downloaded Kokoro voice model (af_bella + 50 others)"
    } catch { Warn "Kokoro download failed — grab kokoro-v1.0.onnx + voices-v1.0.bin into $kdir manually" }
} else { Ok "Kokoro voice model present" }

Step "Self-check"
python -m purple.selfcheck

Write-Host "`nSetup complete. Start Purple with:  purple   (or: python -m purple.run)" -ForegroundColor Cyan
