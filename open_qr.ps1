# PowerShell helper to open the QR code immediately
$InstanceName = "NataliaBrain"

Write-Host "🚀 Opening Secure QR Viewer for $InstanceName..." -ForegroundColor Green
Start-Process "scan_qr.html"
