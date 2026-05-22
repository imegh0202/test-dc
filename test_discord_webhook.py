import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


def load_dotenv(dotenv_path: str = ".env") -> None:
    env_file = Path(dotenv_path)
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")

        if key and key not in os.environ:
            os.environ[key] = value


def send_test_message(webhook_url: str) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "content": f"Discord webhook test OK. Sent at {now}.",
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "discord-webhook-test/1.0",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        print(f"Discord returned HTTP {response.status}. Test message sent.")


def main() -> int:
    load_dotenv()
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Missing DISCORD_WEBHOOK_URL. Add it to .env or set it in PowerShell.")
        return 1

    if not webhook_url.startswith("https://discord.com/api/webhooks/"):
        print("DISCORD_WEBHOOK_URL does not look like a Discord webhook URL.")
        return 1

    try:
        send_test_message(webhook_url)
        return 0
    except urllib.error.HTTPError as exc:
        print(f"Discord returned HTTP {exc.code} {exc.reason}.")
        if exc.code == 401:
            print("The webhook is unauthorized. Create a new webhook and update .env.")
        elif exc.code == 403:
            print("The webhook is forbidden, disabled, invalid, or may have been leaked.")
        elif exc.code == 404:
            print("The webhook was not found. Check that the full webhook URL is correct.")
        return 1
    except urllib.error.URLError as exc:
        print(f"Could not reach Discord: {exc.reason}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
