"""Purple — a fully-local, Jarvis-style personal assistant.

Layers (see README):
  speech  -> voice in/out (local faster-whisper + Piper; Sarvam cloud backup)
  llm     -> the brain (local model via Ollama)
  memory  -> PostgreSQL + pgvector (conversation + long-term facts)
  agent   -> orchestration loop that reasons and calls tools
  tools   -> pluggable capabilities (PC control, web automation, ...)
"""

__version__ = "0.1.0"
