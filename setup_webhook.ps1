# =================================================================
# SETUP WEBHOOK - Conecta los oidos de Natalia
# Jorge Aguirre Flores Web
# =================================================================

# --- CONFIGURACION ---
$InstanceName = "NataliaBrain"
$EvolutionUrl = "https://evolution-whatsapp-zn13.onrender.com"
$WebhookUrl = "https://natalia-brain.onrender.com/webhook/evolution"
$ApiKey = "JorgeSecureKey123"

# --- HEADERS ---
$Headers = @{
    "apikey"       = $ApiKey
    "Content-Type" = "application/json"
}

# --- BODY DEL WEBHOOK ---
$Body = @{
    webhook = @{
        enabled  = $true
        url      = $WebhookUrl
        events   = @(
            "MESSAGES_UPSERT",
            "MESSAGES_UPDATE",
            "CONNECTION_UPDATE",
            "QRCODE_UPDATED"
        )
        byEvents = $false
    }
} | ConvertTo-Json -Depth 10

# --- EJECUCION ---
Write-Host "Configurando Webhook para $InstanceName..." -ForegroundColor Cyan
Write-Host "Destino: $WebhookUrl" -ForegroundColor Gray

Try {
    $Uri = "$EvolutionUrl/webhook/set/$InstanceName"
    $Response = Invoke-RestMethod -Uri $Uri -Method POST -Body $Body -Headers $Headers

    Write-Host "EXITO! Webhook Configurado Correctamente." -ForegroundColor Green
    Write-Host "Respuesta del Servidor:" -ForegroundColor Green
    $Response | ConvertTo-Json | Write-Host
}
Catch {
    Write-Host "ERROR AL CONFIGURAR WEBHOOK" -ForegroundColor Red
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Yellow
}
