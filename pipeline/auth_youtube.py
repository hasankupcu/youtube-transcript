"""Kanal basina bir kez calistir: python -m pipeline.auth_youtube fr

Gerekli: Google Cloud'da YouTube Data API v3 acik bir proje ve
pipeline/secrets/client_secret.json (OAuth masaustu uygulamasi).
"""
from __future__ import annotations

import sys

from google_auth_oauthlib.flow import InstalledAppFlow

from .config import ROOT, load_channels
from .steps.upload import SCOPES


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Kullanim: python -m pipeline.auth_youtube <kanal_anahtari>")
    _, channels = load_channels()
    channel = channels[sys.argv[1]]
    secret = ROOT / "secrets" / "client_secret.json"
    if not secret.exists():
        raise SystemExit(f"{secret} yok. Google Cloud Console'dan indir.")
    flow = InstalledAppFlow.from_client_secrets_file(str(secret), SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
    out = ROOT / channel["youtube_token"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(creds.to_json())
    print(f"Token kaydedildi: {out}")


if __name__ == "__main__":
    main()
