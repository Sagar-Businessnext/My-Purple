# Email + Calendar (Google)

This connects Purple to your real Gmail and Google Calendar. It is the **one feature
that isn't local** — it calls Google's APIs over OAuth. Your token is stored locally in
`google_token.json`; nothing else leaves your machine because of this.

## One-time setup

1. Install the extra: `pip install -e ".[google]"`
2. In [Google Cloud Console](https://console.cloud.google.com):
   - Create (or pick) a project.
   - Enable the **Gmail API** and **Google Calendar API**.
   - Configure the OAuth consent screen (External, add yourself as a test user).
   - Create an **OAuth client ID** of type **Desktop app**, download the JSON.
   - Save it as `google_credentials.json` in `D:\Purple` (or set `PURPLE_GOOGLE_CREDENTIALS_PATH`).
3. Authorize once:
   ```
   python -m purple.integrations.google_auth
   ```
   A browser opens for consent; on success the token is written to `google_token.json`.

## Tools

| Tool | Action | Safety |
|---|---|---|
| `list_emails` | recent inbox | read |
| `search_email` | Gmail query (e.g. `from:mom is:unread`) | read |
| `read_email` | full message body by id | read |
| `draft_email` | create a Gmail **draft** (does not send) | prepare |
| `send_email` | send a message | **confirm** |
| `list_events` | upcoming calendar events | read |
| `create_event` | add a calendar event | **confirm** |

`send_email` and `create_event` are confirmation-gated — Purple prepares them and waits
for your explicit OK, the same prepare-then-commit rule used everywhere else. A typical
flow: "reply to Mom that I'll call tonight" → Purple drafts it → you say send → it asks
to confirm → sent.

## Scopes

`gmail.modify` (read + send + draft) and `calendar` (read + create events). No broader
access is requested.
