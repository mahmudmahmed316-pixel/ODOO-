Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   Odoo Network Access Configurator & Fixer  " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Firewall Rule
Write-Host "[1/4] Configuring Windows Firewall..." -ForegroundColor Yellow
$RuleName = "Odoo Port 8069"
$RuleExists = Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue

if ($RuleExists) {
    Write-Host "Firewall rule '$RuleName' already exists. Re-enabling it..." -ForegroundColor Green
    Enable-NetFirewallRule -DisplayName $RuleName
} else {
    Write-Host "Creating new Firewall rule to open TCP Port 8069..." -ForegroundColor Green
    New-NetFirewallRule -DisplayName $RuleName -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8069 -Description "Allow inbound local network traffic for Odoo ERP"
}

# 2. Check Network Connection Profile (Public vs Private)
Write-Host ""
Write-Host "[2/4] Checking Network Profiles..." -ForegroundColor Yellow
$Profiles = Get-NetConnectionProfile -ErrorAction SilentlyContinue

foreach ($Profile in $Profiles) {
    Write-Host "Network Name: $($Profile.Name)"
    Write-Host "Interface: $($Profile.InterfaceAlias)"
    Write-Host "Current Category: $($Profile.NetworkCategory)"
    
    if ($Profile.NetworkCategory -eq "Public") {
        Write-Host "Network is PUBLIC. Changing to PRIVATE to allow Odoo local connections..." -ForegroundColor Green
        Set-NetConnectionProfile -InputObject $Profile -NetworkCategory Private -ErrorAction SilentlyContinue
        Write-Host "Network category successfully updated to PRIVATE!" -ForegroundColor Green
    } else {
        Write-Host "Network is already PRIVATE. Perfect!" -ForegroundColor Green
    }
}

# 3. Check Odoo Port 8069 Binding Status
Write-Host ""
Write-Host "[3/4] Checking Odoo Server Bindings (Port 8069)..." -ForegroundColor Yellow
$Connections = Get-NetTCPConnection -LocalPort 8069 -ErrorAction SilentlyContinue
if ($Connections) {
    foreach ($Conn in $Connections) {
        Write-Host "Odoo is actively listening on IP: $($Conn.LocalAddress) (State: $($Conn.State))" -ForegroundColor Green
        if ($Conn.LocalAddress -eq "127.0.0.1") {
            Write-Host "WARNING: Odoo is bound to Localhost (127.0.0.1) ONLY." -ForegroundColor Red
            Write-Host "Please ensure your 'odoo.conf' contains 'http_interface = 0.0.0.0' under '[options]' and restart Odoo." -ForegroundColor Red
        }
    }
} else {
    Write-Host "Odoo does not seem to be running on Port 8069 right now." -ForegroundColor Red
    Write-Host "Please start Odoo using: python odoo-bin -c odoo.conf" -ForegroundColor Red
}

# 4. Get Current IPs for other devices to connect
Write-Host ""
Write-Host "[4/4] Connection Guide for other devices:" -ForegroundColor Yellow
$IPs = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notmatch "127.0.0.1|169.254" }
Write-Host "Use one of these URLs on your phone or other device on the SAME Wi-Fi network:" -ForegroundColor Cyan
foreach ($IP in $IPs) {
    Write-Host "👉 http://$($IP.IPAddress):8069" -ForegroundColor Magenta
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Fix completed! Please test connection now." -ForegroundColor Green
Write-Host "Note: If it still fails, please temporarily disable 360 Total Security Firewall." -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Cyan
