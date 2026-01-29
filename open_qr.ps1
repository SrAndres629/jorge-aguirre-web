# PowerShell helper to open the QR code immediately
$InstanceName = "NataliaBrain"
$BaseUrl = "https://evolution-whatsapp-zn13.onrender.com"
$ConnectUrl = "$BaseUrl/instance/connect/$InstanceName"

Write-Host "🚀 Opening WhatsApp Web Pairing for $InstanceName..." -ForegroundColor Green
Start-Process $ConnectUrl
