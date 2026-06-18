"""Central configuration, loaded from environment / .env via pydantic-settings.

Every setting has an env var prefixed with PURPLE_ (see .env.example). Keeping all
config in one typed object means no magic strings scattered across the codebase.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root. This file lives at <root>/src/purple/config.py, so the root is 3 levels up.
# (data/, models/, logs/ and .env live at the project root, NOT inside src/.)
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PURPLE_",
        # Absolute path so the .env we READ is the same one the /config Save WRITES
        # (config_api._merge_env uses ROOT/.env), no matter which directory Purple is
        # launched from.
        env_file=str(ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    host: str = "127.0.0.1"
    port: int = 8765
    log_level: str = "INFO"

    # --- LLM (Ollama) ---
    ollama_base_url: str = "http://127.0.0.1:11434"
    llm_model: str = "qwen2.5:14b-instruct-q4_K_M"
    embed_model: str = "nomic-embed-text"

    # --- Vision (screen understanding via a local VLM) ---
    vision_model: str = "qwen3-vl:8b"  # strong GUI grounding; "qwen3-vl:30b-a3b" to upgrade

    # --- Memory (PostgreSQL + pgvector) ---
    pg_dsn: str = "postgresql+asyncpg://purple:purple@127.0.0.1:5432/purple"
    embed_dim: int = 768  # nomic-embed-text output dimension

    # --- Speech ---
    speech_provider: str = "local"  # "local" | "sarvam"
    whisper_model: str = "medium"
    whisper_device: str = "cuda"
    whisper_compute: str = "float16"
    sarvam_api_key: str = ""

    # --- TTS (natural voice) ---
    tts_engine: str = "kokoro"  # "kokoro" (natural, CPU-light) | "xtts" (clone, backup)
    kokoro_voice: str = "af_bella"  # warm, soft female ("her"-style)
    kokoro_speed: float = 1.0
    xtts_speaker_wav: str = ""  # reference clip path for XTTS voice cloning (backup)

    # --- Safety ---
    require_confirmation: bool = True

    # --- Persona (how Purple presents herself; safety rules are fixed regardless) ---
    assistant_name: str = "Purple"
    persona_tone: str = "warm"  # warm | professional | playful | terse
    persona_style: str = ""  # optional free-text persona description layered on top
    persona_use_profile: bool = True  # address the user by name + honor their comms style

    # --- Productivity / proactivity ---
    enable_scheduler: bool = True
    briefing_hour: int = 7
    briefing_minute: int = 0
    weather_location: str = ""  # city for the morning weather (blank = skip); via Open-Meteo
    news_feeds: list[str] = Field(  # RSS feeds for the morning headlines
        default_factory=lambda: ["https://feeds.bbci.co.uk/news/world/rss.xml"]
    )
    auto_memory: bool = True  # auto-extract durable facts from each turn (GPU-gated)
    auto_memory_mode: str = "moderate"  # moderate | high | aggressive — how much to learn
    session_summarize_every: int = 10  # refresh the rolling session summary every N messages
    consolidate_weekly: bool = True  # weekly memory hygiene (merge duplicate facts)
    memory_decay_days: int = 0  # forget plain facts older than this many days (0 = never)
    knowledge_dir: str = ""  # a folder Purple auto-ingests into her knowledge base (RAG)

    # --- Boot greeting (a short, time-aware hello when Purple starts) ---
    enable_greeting: bool = True  # greet on startup (time-aware; weather one-liner; news offer)

    # --- Screen-context observation (privacy: explicit consent, off by default) ---
    observe_default: bool = False  # start observing on boot? (you can also say "start observing")
    observe_log_history: bool = False  # also record each observed window to the activity log
    observe_auto_off_hours: int = 4  # auto-stop observing after this many hours (0 = never)

    # --- Wake word / voice loop ---
    enable_wake: bool = False  # off by default; needs a mic + downloaded wake model
    wake_model: str = "hey_jarvis"  # pretrained name OR path to a trained model (hey_purple.onnx)
    wake_threshold: float = 0.5
    sample_rate: int = 16000
    silence_ms: int = 800  # stop capturing the command after this much trailing silence
    vad_threshold: float = 500.0  # int16 RMS above this counts as speech
    stream_voice: bool = True  # speak replies sentence-by-sentence (low latency, cancelable)
    enable_barge_in: bool = True  # let an enrolled speaker interrupt Purple mid-reply
    conversation_mode: bool = True  # after one wake, stay in a back-and-forth until idle
    conversation_idle_seconds: int = 8  # end the conversation after this much silence

    # --- Speaker ID (voice access gate: only enrolled voices may talk to Purple) ---
    require_enrolled_voice: bool = True  # enforced once ≥1 voice is enrolled; fail-closed
    speaker_threshold: float = 0.75  # cosine similarity to accept a voice as a match

    # --- Phone bridge (Android via ADB) ---
    adb_path: str = "adb"
    phone_serial: str = ""  # blank = use the only connected device
    wireless_address: str = ""  # e.g. "192.168.1.50:5555" for Wi-Fi ADB
    enable_phone_watchers: bool = True  # watch calls (spam-aware) + messages over ADB
    phone_poll_seconds: int = 5  # how often to check call state (rings are short-lived)

    # --- Desktop (tray + push-to-talk) ---
    enable_tray: bool = False
    enable_push_to_talk: bool = False
    ptt_hotkey: str = "<ctrl>+<alt>+space"
    ui_url: str = "http://127.0.0.1:8765/ui/"  # the web UI (tray "Open Purple" + autostart)
    open_ui_on_start: bool = True  # open the web UI in your browser when Purple starts

    # --- Browser control ---
    browser_headless: bool = False  # headed so you can watch / intervene
    browser_cdp_url: str = ""  # e.g. http://127.0.0.1:9222 to drive your own Chrome

    # --- Google (Gmail + Calendar) ---
    google_credentials_path: str = "google_credentials.json"  # OAuth client secrets
    google_token_path: str = "google_token.json"  # saved after first authorization

    # --- Smart home (Home Assistant, local) ---
    ha_base_url: str = ""  # e.g. http://homeassistant.local:8123 (blank = disabled)
    ha_token: str = ""  # Home Assistant long-lived access token

    # --- Observability ---
    log_to_file: bool = True
    log_dir: Path = Field(default=ROOT / "logs")
    log_max_bytes: int = 5_000_000  # ~5 MB per log file before rotating
    log_backups: int = 5
    enable_metrics: bool = True  # expose Prometheus metrics at /metrics
    enable_tracing: bool = False  # OpenTelemetry spans (agent -> tool -> llm)
    otlp_endpoint: str = ""  # OTLP HTTP endpoint; blank = console exporter

    # --- Always-on service + GPU Focus mode ---
    api_token: str = ""  # required as X-Purple-Token for non-localhost requests; blank = localhost-only
    focus_mode: bool = False  # manual: pause GPU-heavy background work
    auto_focus: bool = True  # auto-yield the GPU when it's busy (gaming / rendering)
    gpu_busy_util: int = 50  # GPU utilisation % at/above which it's "busy"
    gpu_busy_vram_mb: int = 10000  # VRAM used (MB) at/above which it's "busy"

    # --- Proactivity / triggers (M2) ---
    enable_triggers: bool = True
    enable_self_watcher: bool = True  # Purple warns you when her own subsystems go down
    autonomy: str = "confirm"  # notify | confirm | act
    mission_max_depth: int = 1  # how deep missions may delegate steps to sub-agents
    quiet_hours_start: int = 23  # voice/toasts go quiet from this local hour...
    quiet_hours_end: int = 7  # ...until this hour (important/urgent still break through)
    vip_senders: list[str] = Field(default_factory=list)  # always-important emails/names
    email_poll_seconds: int = 180
    system_poll_seconds: int = 60
    calendar_lead_minutes: int = 15  # speak this many minutes before an event
    disk_low_gb: int = 20
    download_dir: str = ""  # folder to watch for finished downloads; blank = ~/Downloads
    cpu_high_pct: int = 90  # sustained CPU at/above this is flagged
    ram_high_pct: int = 90  # sustained RAM at/above this is flagged (you run 16GB)
    gpu_high_pct: int = 97  # sustained GPU utilisation at/above this is flagged
    gpu_vram_high_pct: int = 92  # sustained GPU-VRAM use at/above this is flagged (16GB card)

    # Derived paths
    data_dir: Path = Field(default=DATA_DIR)
    models_dir: Path = Field(default=MODELS_DIR)

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)


# Import this singleton everywhere: `from purple.config import settings`
settings = Settings()
