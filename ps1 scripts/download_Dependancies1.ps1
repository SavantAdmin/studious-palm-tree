# Define the URL to download the Python installer
$pythonInstallerUrl = "https://www.python.org/ftp/python/3.10.4/python-3.10.4-amd64.exe"

# Define the path to save the Python installer
$pythonInstallerPath = "$env:TEMP\python-installer.exe"

# Download the Python installer
Invoke-WebRequest -Uri $pythonInstallerUrl -OutFile $pythonInstallerPath

# Define the Python installation arguments
$pythonInstallArgs = "/quiet InstallAllUsers=1 PrependPath=1"

# Run the Python installer
Start-Process -FilePath $pythonInstallerPath -ArgumentList $pythonInstallArgs -Wait

# Clean up the Python installer file
Remove-Item -Path $pythonInstallerPath

# Verify the Python installation
$pythonVersion = python --version
if ($pythonVersion) {
    Write-Output "Python installed successfully: $pythonVersion"
} else {
    Write-Error "Python installation failed."
    exit 1
}

# Install Selenium using pip
pip install selenium

# Verify Selenium installation
$seleniumVersion = pip show selenium | Select-String -Pattern "^Version: " | ForEach-Object { $_.ToString().Split(" ")[1] }
if ($seleniumVersion) {
    Write-Output "Selenium installed successfully: $seleniumVersion"
} else {
    Write-Error "Selenium installation failed."
    exit 1
}

# Enable the OpenSSH Server feature
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Start and configure the SSH server
Start-Service -Name sshd
Set-Service -Name sshd -StartupType 'Automatic'

# Verify SSH service status
$sshStatus = Get-Service -Name sshd
if ($sshStatus.Status -eq "Running") {
    Write-Output "SSH server is running and configured to start automatically."
} else {
    Write-Error "Failed to start the SSH server."
    exit 1
}

# Define the URL to download the Docker installer
$dockerInstallerUrl = "https://desktop.docker.com/win/stable/Docker%20Desktop%20Installer.exe"

# Define the path to save the Docker installer
$dockerInstallerPath = "$env:TEMP\DockerDesktopInstaller.exe"

# Download the Docker installer
Invoke-WebRequest -Uri $dockerInstallerUrl -OutFile $dockerInstallerPath

# Run the Docker installer
Start-Process -FilePath $dockerInstallerPath -ArgumentList "/quiet" -Wait

# Clean up the Docker installer file
Remove-Item -Path $dockerInstallerPath

# Verify Docker installation
$dockerVersion = docker --version
if ($dockerVersion) {
    Write-Output "Docker installed successfully: $dockerVersion"
} else {
    Write-Error "Docker installation failed."
    exit 1
}

Write-Output "Script completed successfully."
