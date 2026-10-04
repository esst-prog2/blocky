# Shows Blocky's entries and Docker Desktop's lines in the hosts file. Reading the hosts file needs no admin rights.
# Once:   powershell -ExecutionPolicy Bypass -File spike\p1-lifecycle\watch-hosts.ps1
# Watch:  powershell -ExecutionPolicy Bypass -File spike\p1-lifecycle\watch-hosts.ps1 -Watch   (every 10 s; Ctrl+C stops)
param([switch]$Watch)

$hosts = "C:\Windows\System32\drivers\etc\hosts"

function Show-Hosts {
    $blocky = @()
    $docker = @()
    $inBlocky = $false
    $inDocker = $false
    foreach ($line in Get-Content $hosts) {
        $marker = $line.Trim()
        if ($marker -eq "# BEGIN BLOCKY") { $inBlocky = $true; continue }
        if ($marker -eq "# END BLOCKY") { $inBlocky = $false; continue }
        if ($marker -eq "# Added by Docker Desktop") { $inDocker = $true; continue }
        if ($marker -eq "# End of section") { $inDocker = $false; continue }
        if ($inBlocky) { $blocky += $line }
        if ($inDocker -and -not $marker.StartsWith("#")) { $docker += $line }
    }
    $time = (Get-Date).ToString("HH:mm:ss")
    Write-Host "$time  Blocky entries: $($blocky.Count)  Docker lines: $($docker.Count)"
    if (-not $Watch) {
        $blocky | ForEach-Object { Write-Host "  Blocky: $_" }
        $docker | ForEach-Object { Write-Host "  Docker: $_" }
    }
}

if ($Watch) {
    while ($true) {
        Show-Hosts
        Start-Sleep -Seconds 10
    }
} else {
    Show-Hosts
}
