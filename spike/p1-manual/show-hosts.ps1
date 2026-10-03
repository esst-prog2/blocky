$hosts = "C:\Windows\System32\drivers\etc\hosts"
Write-Host "Checked at $((Get-Date).ToString('HH:mm:ss'))"
$inside = $false
$lines = @()
foreach ($line in Get-Content $hosts) {
    if ($line.Trim() -eq "# BEGIN BLOCKY") { $inside = $true; continue }
    if ($line.Trim() -eq "# END BLOCKY") { $inside = $false; continue }
    if ($inside) { $lines += $line }
}
if ($lines.Count -eq 0) {
    Write-Host "No Blocky entries in the hosts file"
} else {
    Write-Host "Blocky entries ($($lines.Count)):"
    $lines | ForEach-Object { Write-Host "  $_" }
}
