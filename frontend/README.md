# Purple frontend (React + Tauri)

The UI is deliberately thin — it's just the face. All the intelligence (LLM, memory,
PC control, web automation) lives in the Python backend. The actual chat UI is already
written for you in `frontend/ui-src/`; you scaffold a Tauri shell on your PC and drop
those files in.

## 1. Scaffold the desktop shell (run on your PC, one time)

From `D:\Purple\frontend`:

```bash
npm create tauri-app@latest app -- --template react-ts
cd app
npm install
```

Choose React + TypeScript. This creates `frontend/app` — a real native desktop app
(small, fast, system-tray capable) wrapping a React UI.

## 2. Drop in Purple's UI

Copy the provided files over the template defaults:

```bash
copy ..\ui-src\App.tsx  src\App.tsx
copy ..\ui-src\App.css  src\App.css
copy ..\ui-src\purple.ts src\purple.ts
```

## 3. Run it

```bash
# in one terminal, from D:\Purple:
python run.py
# in another, from D:\Purple\frontend\app:
npm run tauri dev
```

The window connects to the backend over WebSocket, streams replies, pops a confirm
dialog for risky tools, and has a mic button (records audio, posts to /voice, plays
the spoken reply).

## Tauri config (let the webview reach the backend)

The desktop webview must be allowed to talk to the local backend. In
`frontend/app/src-tauri/tauri.conf.json`, set the security CSP so it can open the
WebSocket and call the API:

```json
{
  "app": {
    "security": {
      "csp": "default-src 'self'; connect-src 'self' http://127.0.0.1:8765 ws://127.0.0.1:8765; img-src 'self' data:; media-src 'self' data: blob:"
    }
  }
}
```

The backend already sends the matching CORS headers (localhost + tauri origins).

## Voice mode

Set `PURPLE_ENABLE_WAKE=true` in `.env` and run the backend; it listens for the wake
word and pushes live events to the UI (`listening` → `woke` → `heard` → `reply`),
which the chat reflects automatically. The in-app Mic button is separate push-to-talk.

## Backend API contract

REST:
- `GET  /health` → `{ ok, ollama, model, speech_provider, tools }`
- `POST /chat` → `{ "message": str, "session_id": str }` → `{ "reply": str }`
- `POST /voice` → multipart file `file` → `{ transcript, reply, audio_base64 }`

WebSocket `/ws` (used by the app):
- send `{ "message": "open steam" }`
- may receive `{ "type": "confirm_request", "tool": "...", "args": {...} }`
  → reply `{ "approved": true | false }`
- finally receive `{ "type": "reply", "reply": "..." }`

## Notes

- Mic records WebM (browser default). faster-whisper decodes it fine via ffmpeg; if
  you ever want strict WAV, we can add in-browser PCM encoding later.
- When you're ready I'll add a settings panel (model, voice, provider), a system-tray
  icon, and a global push-to-talk hotkey.
