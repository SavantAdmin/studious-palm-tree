# Prompt the user for the new computer name
$newName = Read-Host "Enter the new computer name"

# Validate if the input is not empty
if ([string]::IsNullOrEmpty($newName)) {
    Write-Host "Computer name cannot be empty. Exiting script."
    Exit
}

# Change the computer name
$computerInfo = Get-WmiObject Win32_ComputerSystem
$computerInfo.Rename($newName)

# Verify if the computer name was changed successfully
if ($?) {
    Write-Host "Computer name changed successfully. Restarting computer..."
    # Restart the computer to apply the new name
    Restart-Computer -Force
} else {
    Write-Host "Failed to change computer name."
}
