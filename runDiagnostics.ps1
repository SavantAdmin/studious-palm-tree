# Check system uptime
$uptime = (Get-CimInstance -ClassName win32_operatingsystem).LastBootUpTime
$uptimeFormatted = [System.Management.ManagementDateTimeConverter]::ToDateTime($uptime)
Write-Output "System Uptime: $((Get-Date) - $uptimeFormatted)"

# Check available memory
$memory = Get-CimInstance -ClassName win32_operatingsystem
Write-Output "Total Physical Memory: $([math]::round($memory.TotalVisibleMemorySize / 1MB, 2)) GB"
Write-Output "Free Physical Memory: $([math]::round($memory.FreePhysicalMemory / 1MB, 2)) GB"

# Check disk space
$disks = Get-CimInstance -ClassName win32_logicaldisk -Filter "DriveType=3"
foreach ($disk in $disks) {
    $size = [math]::round($disk.Size / 1GB, 2)
    $freeSpace = [math]::round($disk.FreeSpace / 1GB, 2)
    Write-Output "Drive $($disk.DeviceID) - Total Size: $size GB, Free Space: $freeSpace GB"
}

# Check network status
$networkAdapters = Get-NetAdapter | Where-Object {$_.Status -eq "Up"}
foreach ($adapter in $networkAdapters) {
    Write-Output "Network Adapter: $($adapter.Name) - Status: $($adapter.Status)"
    $ipAddresses = Get-NetIPAddress -InterfaceIndex $adapter.ifIndex | Where-Object {$_.AddressFamily -eq "IPv4"}
    foreach ($ip in $ipAddresses) {
        Write-Output "IP Address: $($ip.IPAddress)"
    }
}

# Pause the script to view output
Write-Host "Press any key to exit..."
$x = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Initiate shutdown sequence
Write-Output "Shutting down the system in 10 seconds..."
Start-Sleep -Seconds 10
Stop-Computer -Force
