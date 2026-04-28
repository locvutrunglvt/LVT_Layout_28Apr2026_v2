<# LVT Map Layout - Install Script
   Creates a symlink from QGIS plugins directory to this folder.
   Run as Administrator if needed.
#>

$PluginSource = $PSScriptRoot
$QgisPluginDir = "$env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\Layout_LVT"

if (Test-Path $QgisPluginDir) {
    Write-Host "Removing existing link/folder: $QgisPluginDir" -ForegroundColor Yellow
    Remove-Item $QgisPluginDir -Force -Recurse
}

try {
    New-Item -ItemType SymbolicLink -Path $QgisPluginDir -Target $PluginSource -Force | Out-Null
    Write-Host "SUCCESS: Symlink created!" -ForegroundColor Green
    Write-Host "  Source: $PluginSource"
    Write-Host "  Target: $QgisPluginDir"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Open QGIS"
    Write-Host "  2. Plugins > Manage and Install Plugins"
    Write-Host "  3. Find 'LVT Map Layout' and enable it"
    Write-Host "  4. Click the toolbar button or menu: Plugins > LVT Map Layout"
} catch {
    Write-Host "Symlink failed. Trying copy instead..." -ForegroundColor Yellow
    Copy-Item -Path $PluginSource -Destination $QgisPluginDir -Recurse -Force
    Write-Host "SUCCESS: Plugin copied to QGIS plugins folder!" -ForegroundColor Green
}
