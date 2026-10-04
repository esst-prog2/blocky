$hosts = "C:\Windows\System32\drivers\etc\hosts"
$watching = Get-Date
Write-Host "Watching hosts file since $($watching.ToString('HH:mm:ss'))"
while (-not (Select-String -Path $hosts -Pattern "# BEGIN BLOCKY" -Quiet)) {
    Start-Sleep -Seconds 1
}
$seen = Get-Date
Write-Host "Blocky entries appeared at $($seen.ToString('HH:mm:ss'))"
