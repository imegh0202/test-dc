$ErrorActionPreference = "Stop"

function Import-DotEnv {
    param([string]$Path = ".env")

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    Get-Content -LiteralPath $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) {
            return
        }

        if ($line.StartsWith("https://discord.com/api/webhooks/")) {
            [Environment]::SetEnvironmentVariable("DISCORD_WEBHOOK_URL", $line, "Process")
            return
        }

        if (-not $line.Contains("=")) {
            return
        }

        $key, $value = $line.Split("=", 2)
        $key = $key.Trim()
        $value = $value.Trim().Trim("'").Trim('"')

        if ($key -and -not [Environment]::GetEnvironmentVariable($key, "Process")) {
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

Import-DotEnv

$webhookUrl = [Environment]::GetEnvironmentVariable("DISCORD_WEBHOOK_URL", "Process")
if (-not $webhookUrl) {
    Write-Error "Missing DISCORD_WEBHOOK_URL. Add it to .env or set it in PowerShell first."
}

if (-not $webhookUrl.StartsWith("https://discord.com/api/webhooks/")) {
    Write-Error "DISCORD_WEBHOOK_URL does not look like a Discord webhook URL."
}

$body = @{
    content = "Discord webhook test OK. Sent at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')."
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri $webhookUrl -Method Post -ContentType "application/json" -Body $body | Out-Null
    Write-Host "Discord webhook test message sent."
}
catch {
    $response = $_.Exception.Response
    if ($response) {
        $statusCode = [int]$response.StatusCode
        Write-Error "Discord returned HTTP $statusCode $($response.StatusDescription). Check the webhook URL."
    }

    Write-Error "Could not send Discord webhook test: $($_.Exception.Message)"
}
