# PowerShell helper to configure webhook for Natalia Brain
$InstanceName = "NataliaBrain"
$ApiUrl = "https://evolution-whatsapp-zn13.onrender.com"
$ApiKey = "JorgeSecureKey123"

Write-Host "🔗 WEBHOOK CONFIGURATION WIZARD" -ForegroundColor Cyan
Write-Host "We need to tell Evolution API where 'Natalia Brain' lives."
Write-Host "--------------------------------------------------------"

$BrainUrl = Read-Host "Enter your Natalia Brain URL (e.g. https://natalia-brain-xyz.onrender.com)"

if ([string]::IsNullOrWhiteSpace($BrainUrl)) {
    Write-Error "❌ URL cannot be empty."
    exit 1
}

# Ensure URL has no trailing slash
$BrainUrl = $BrainUrl.TrimEnd('/')

# The exact webhook endpoint in Natalia Brain
$TargetUrl = "$BrainUrl/webhook/evolution"

Write-Host "`n⚙️ Configuring webhook for instance: $InstanceName"
Write-Host "🎯 Target: $TargetUrl"

$Payload = @{
    webhook = @{
        enabled  = $true
        url      = $TargetUrl
        byEvents = $false
        events   = @(
            "MESSAGES_UPSERT",
            "MESSAGES_UPDATE",
            "CONNECTION_UPDATE"
        )
    }
} | ConvertTo-Json -Depth 4

try {
    $Response = Invoke-RestMethod -Uri "$ApiUrl/webhook/set/$InstanceName" `
        -Method Post `
        -Headers @{ "apikey" = $ApiKey; "Content-Type" = "application/json" } `
        -Body $Payload `
        -ErrorAction Stop

    Write-Host "`n✅ SUCCESS! Webhook Configured." -ForegroundColor Green
    Write-Host "Evolution API will now send messages to Natalia Brain."
    $JsonResp = $Response | ConvertTo-Json -Depth 2
    Write-Host "Response: $JsonResp"
}
catch {
    Write-Error "❌ FAILED to configure webhook."
    Write-Host "Error Details: $_" -ForegroundColor Red
    if ($_.Exception.Response) {
        $Stream = $_.Exception.Response.GetResponseStream()
        $Reader = New-Object System.IO.StreamReader($Stream)
        $BodyResponse = $Reader.ReadToEnd()
        Write-Host "Server Response: $BodyResponse" -ForegroundColor Red
    }
}
