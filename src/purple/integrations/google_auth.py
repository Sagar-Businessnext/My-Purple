"""One-time Google authorization.

    python -m purple.integrations.google_auth

Reads the OAuth client secrets (download from Google Cloud Console — an OAuth client
of type "Desktop app", with the Gmail and Calendar APIs enabled), opens a browser for
consent, and saves the resulting token to google_token.json so Purple can use it.
"""

from __future__ import annotations

from purple.config import settings
from purple.integrations.google import SCOPES, _path


def main() -> None:
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds_path = _path(settings.google_credentials_path)
    if not creds_path.exists():
        print(f"Missing OAuth client secrets at {creds_path}.")
        print(
            "In Google Cloud Console: enable the Gmail API + Calendar API, create an "
            "OAuth client (Desktop app), download the JSON, and save it there."
        )
        raise SystemExit(1)

    flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
    creds = flow.run_local_server(port=0)
    token = _path(settings.google_token_path)
    token.write_text(creds.to_json())
    print(f"Authorized. Token saved to {token}. Purple can now use Gmail + Calendar.")


if __name__ == "__main__":
    main()
