# Stock Discord Alert Bot

This is a minimal Python example for sending stock price alerts to Discord with a bot token.

## What it does

- Checks stock prices from Finnhub
- Sends a startup health check to Discord before entering the watch loop
- Sends a Discord message when a stock crosses your target price
- Prevents duplicate notifications until the price moves back out of the trigger range
- Can run once in GitHub Actions or keep looping on your local machine

## Setup

1. Create a Discord bot application and invite it to your server
2. Get a free API key from Finnhub
3. Create a `.env` file from `.env.example` and fill in your values:

```env
FINNHUB_API_KEY=your_finnhub_key
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=your_target_channel_id
```

4. Or set them temporarily in PowerShell if you do not want a `.env` file:

```powershell
$env:FINNHUB_API_KEY="your_finnhub_key"
$env:DISCORD_BOT_TOKEN="your_discord_bot_token"
$env:DISCORD_CHANNEL_ID="your_target_channel_id"
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
   - `DISCORD_BOT_TOKEN`
   - `DISCORD_CHANNEL_ID`
4. Go to the `Actions` tab and enable workflows if prompted

The workflow is configured to:

- run every 5 minutes
- run once per job instead of looping forever
- skip the startup health check message to avoid Discord spam

GitHub scheduled workflows use UTC time and the shortest supported interval is every 5 minutes according to GitHub's workflow syntax docs:
https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

GitHub Actions secrets setup docs:
https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets

## Discord Bot Setup

Create the bot in the Discord Developer Portal and invite it with the `bot` scope. Discord's official docs note that your code uses the bot token to authenticate as the bot user:
https://docs.discord.com/developers/platform/oauth2-and-permissions

For this project, the bot needs permission to:

- `View Channel`
- `Send Messages`

To get the target channel ID:

1. In Discord, open `User Settings` > `Advanced`
2. Turn on `Developer Mode`
3. Right-click the target channel
4. Click `Copy Channel ID`

To invite the bot, use the Developer Portal and choose the `bot` scope with the permissions above:
https://discord.com/developers/docs/bots

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
- If Discord returns `401 Unauthorized`, your bot token is invalid.
- If Discord returns `403 Forbidden`, the bot usually is not in the server yet or lacks channel permissions.
- If Discord returns `404 Not Found`, the channel ID is wrong or the bot cannot access that channel.
- The bot now sends a startup message first, so you can confirm Discord posting works before waiting for a price trigger.
- `RUN_ONCE=true` is useful for GitHub Actions because scheduled jobs should finish quickly instead of running forever.
- `SEND_STARTUP_HEALTHCHECK=false` is useful for GitHub Actions to avoid sending a startup message on every scheduled run.
