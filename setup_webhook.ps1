# --- CONFIGURACION ---
$InstanceName = "NataliaBrain"
$EvolutionUrl = "https://evolution-whatsapp-zn13.onrender.com"
$ApiKey = "JorgeSecureKey123"

# --- ASISTENTE ---
Write-Host '🔗 ASISTENTE DE WEBHOOK'
$BrainBaseUrl = Read-Host 'Pega la URL de Natalia Brain (ej: https://natalia-brain.onrender.com)'

if ([string]::IsNullOrWhiteSpace($BrainBaseUrl)) {
    Write-Error '❌ URL vacia'
    exit 1
}

$WebhookUrl = $BrainBaseUrl.TrimEnd('/') + '/webhook/evolution'

$Headers = @{
    'apikey'       = $ApiKey
    'Content-Type' = 'application/json'
}

$Body = @{
    'webhook' = @{
        'enabled'  = $true
        'url'      = $WebhookUrl
        'events'   = @('MESSAGES_UPSERT', 'MESSAGES_UPDATE', 'CONNECTION_UPDATE')
        'byEvents' = $false
    }
} | ConvertTo-Json -Depth 10

Write-Host ('📡 Configurando: ' + $InstanceName)
Write-Host ('🎯 Destino: ' + $WebhookUrl)

try {
    $Uri = $EvolutionUrl + '/webhook/set/' + $InstanceName
    $Response = Invoke-RestMethod -Uri $Uri -Method POST -Body $Body -Headers $Headers
    Write-Host '✅ ¡ÉXITO!'
    $Response | ConvertTo-Json | Write-Host
}
catch {
    Write-Host '❌ ERROR'
    if ($_.Exception.Response) {
        $Stream = $_.Exception.Response.GetResponseStream()
        $Reader = New-Object System.IO.StreamReader($Stream)
        $BodyErr = $Reader.ReadToEnd()
        Write-Host 'Detalle:'
        Write-Host $BodyErr
    }
    else {
        Write-Host 'Error General:'
        Write-Host $_
    }
}
