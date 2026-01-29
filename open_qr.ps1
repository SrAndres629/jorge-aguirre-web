# PowerShell helper to open the QR code immediately
$InstanceName = "NataliaBrain"
$BaseUrl = "https://evolution-whatsapp-zn13.onrender.com"
$ConnectUrl = "$BaseUrl/instance/connect/$InstanceName"

Write-Host "🚀 Opening Secure QR Viewer for $InstanceName..." -ForegroundColor Green
Start-Process "scan_qr.html"
