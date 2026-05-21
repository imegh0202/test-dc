# Stock Discord Alert Bot

This is a minimal Python example for sending stock price alerts to Discord with a webhook.

## What it does

- Checks stock prices from Finnhub
- Sends a startup health check to Discord before entering the watch loop
- Sends a Discord message when a stock crosses your target price
- Prevents duplicate notifications until the price moves back out of the trigger range
- Can run once in GitHub Actions or keep looping on your local machine

## Setup

1. Create a Discord webhook for your channel
2. Get a free API key from Finnhub
3. Create a `.env` file from `.env.example` and fill in your values:

```env
FINNHUB_API_KEY=your_finnhub_key
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_id/your_webhook_token
```

4. Or set them temporarily in PowerShell if you do not want a `.env` file:

```powershell
$env:FINNHUB_API_KEY="your_finnhub_key"
$env:DISCORD_WEBHOOK_URL="your_discord_webhook_url"
```

5. Edit `WATCHLIST` in `stock_alert_bot.py`
6. Run:

```powershell
python .\stock_alert_bot.py
```

## GitHub Actions

You can run this on GitHub with a scheduled workflow in `.github/workflows/stock-alert.yml`.

1. Push this project to a GitHub repository
2. In GitHub, open `Settings` > `Secrets and variables` > `Actions`
3. Add these repository secrets:
   - `FINNHUB_API_KEY`
   - `DISCORD_WEBHOOK_URL`
4. Go to the `Actions` tab and enable workflows if prompted

The workflow is configured to:

- run every 5 minutes
- run once per job instead of looping forever
- skip the startup health check message to avoid Discord spam

GitHub scheduled workflows use UTC time and the shortest supported interval is every 5 minutes according to GitHub's workflow syntax docs:
https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

GitHub Actions secrets setup docs:
https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets

## Example watchlist

```python
WATCHLIST = [
    {"symbol": "AAPL", "above": 220},
    {"symbol": "TSLA", "above": 200},
    {"symbol": "NVDA", "below": 120},
]
```

## Notes

- `above`: send when current price is greater than or equal to the target
- `below`: send when current price is less than or equal to the target
- `CHECK_INTERVAL_SECONDS = 300` means the bot checks every 5 minutes
- This example uses only Python standard library, so no `pip install` is required
- If Discord returns `403 Forbidden`, your webhook is usually invalid, disabled, or leaked. Create a new one and keep the full URL private.
- The bot now sends a startup message first, so you can confirm the webhook works before waiting for a price trigger.
- `RUN_ONCE=true` is useful for GitHub Actions because scheduled jobs should finish quickly instead of running forever.
- `SEND_STARTUP_HEALTHCHECK=false` is useful for GitHub Actions to avoid sending a startup message on every scheduled run.
