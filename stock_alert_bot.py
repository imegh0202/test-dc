import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


# Edit this list to track the stocks and trigger prices you want.
WATCHLIST = [
    ##{"symbol": "TSLA", "above": 220},
    ##{"symbol": "2330", "above": 200},
    {"symbol": "NVDA", "below": 120},
]

CHECK_INTERVAL_SECONDS = 300


def get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


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


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Add it to your .env file or set it in PowerShell first."
        )
    return value


def fetch_price(symbol: str, api_key: str) -> float:
    params = urllib.parse.urlencode({"symbol": symbol, "token": api_key})
    url = f"https://finnhub.io/api/v1/quote?{params}"

    with urllib.request.urlopen(url, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))

    price = data.get("c")
    if price in (None, 0):
        raise RuntimeError(f"Could not fetch a valid price for {symbol}: {data}")

    return float(price)


def send_discord_message(webhook_url: str, content: str) -> None:
    payload = json.dumps({"content": content}).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=15):
            return
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            raise RuntimeError(
                "Discord webhook returned 403 Forbidden. "
                "The webhook URL is likely invalid, disabled, or leaked. "
                "Create a new webhook in Discord and keep the full URL private."
            ) from exc
        raise


def send_startup_healthcheck(webhook_url: str) -> None:
    send_discord_message(
        webhook_url,
        "Stock alert bot startup check passed. Webhook is reachable.",
    )


def check_rule(price: float, rule: dict) -> tuple[bool, str]:
    above = rule.get("above")
    below = rule.get("below")

    if above is not None and price >= above:
        return True, f"{rule['symbol']} is now ${price:.2f}, above ${above:.2f}"

    if below is not None and price <= below:
        return True, f"{rule['symbol']} is now ${price:.2f}, below ${below:.2f}"

    return False, ""


def run_checks(finnhub_api_key: str, discord_webhook_url: str, sent_alerts: set[str]) -> None:
    print("Checking prices...")

    for rule in WATCHLIST:
        symbol = rule["symbol"]

        try:
            price = fetch_price(symbol, finnhub_api_key)
            triggered, message = check_rule(price, rule)
            alert_key = f"{symbol}:{rule.get('above')}:{rule.get('below')}"

            if triggered and alert_key not in sent_alerts:
                send_discord_message(discord_webhook_url, message)
                sent_alerts.add(alert_key)
                print(f"Alert sent: {message}")
            elif not triggered and alert_key in sent_alerts:
                sent_alerts.remove(alert_key)
                print(f"Alert reset: {symbol}")
            else:
                print(f"{symbol}: ${price:.2f}")

        except urllib.error.HTTPError as exc:
            print(f"HTTP error for {symbol}: {exc.code} {exc.reason}")
        except urllib.error.URLError as exc:
            print(f"Network error for {symbol}: {exc.reason}")
        except Exception as exc:
            print(f"Unexpected error for {symbol}: {exc}")


def run() -> int:
    load_dotenv()
    try:
        finnhub_api_key = get_env("FINNHUB_API_KEY")
        discord_webhook_url = get_env("DISCORD_WEBHOOK_URL")
    except RuntimeError as exc:
        print(f"Startup failed: {exc}")
        return 1

    run_once = get_bool_env("RUN_ONCE", False)
    send_healthcheck = get_bool_env("SEND_STARTUP_HEALTHCHECK", True)
    sent_alerts = set()

    if send_healthcheck:
        print("Sending Discord webhook health check...")
        try:
            send_startup_healthcheck(discord_webhook_url)
        except RuntimeError as exc:
            print(f"Startup failed: {exc}")
            return 1
        except urllib.error.HTTPError as exc:
            print(f"Startup failed: Discord returned HTTP {exc.code} {exc.reason}.")
            return 1
        except urllib.error.URLError as exc:
            print(f"Startup failed: could not reach Discord webhook: {exc.reason}")
            return 1

        print("Discord webhook health check passed.")
    else:
        print("Skipping startup webhook health check.")

    if run_once:
        run_checks(finnhub_api_key, discord_webhook_url, sent_alerts)
        return 0

    while True:
        run_checks(finnhub_api_key, discord_webhook_url, sent_alerts)
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    sys.exit(run())
