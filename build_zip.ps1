# LVT Map Layout — Auto-versioned ZIP builder
# Usage: Right-click → Run with PowerShell, or run in terminal

$src = $PSScriptRoot
$outDir = $PSScriptRoot
$baseName = "LVT_Layout_28Apr2026_v2"

# Find next version number
$existing = Get-ChildItem "$outDir\${baseName}_*.zip" -ErrorAction SilentlyContinue |
    ForEach-Object {
        if ($_.BaseName -match '_(\d{3})$') { [int]$Matches[1] }
    } | Sort-Object -Descending | Select-Object -First 1

$nextVer = if ($existing) { $existing + 1 } else { 1 }
$verStr = $nextVer.ToString("D3")  # 001, 002, 003...
$zipName = "${baseName}_${verStr}.zip"
$zipPath = Join-Path $outDir $zipName

# Build in temp
$tmp = Join-Path $env:TEMP $baseName
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
New-Item -ItemType Directory -Path $tmp -Force | Out-Null
New-Item -ItemType Directory -Path "$tmp\templates" -Force | Out-Null

# Copy plugin files (exclude build artifacts)
$files = @(
    "__init__.py", "lvt_map_layout.py", "lvt_dialog.py",
    "lvt_engine.py", "lvt_extent_tool.py", "metadata.txt", "README.md"
)
foreach ($f in $files) {
    $fp = Join-Path $src $f
    if (Test-Path $fp) { Copy-Item $fp $tmp }
}
Copy-Item "$src\templates\*.qpt" "$tmp\templates\"

# Create zip
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path $tmp -DestinationPath $zipPath -Force

# Report
$size = [math]::Round((Get-Item $zipPath).Length / 1KB, 1)
Write-Host ""
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host "  BUILD COMPLETE" -ForegroundColor Green
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host "  Version : $verStr" -ForegroundColor Yellow
Write-Host "  File    : $zipName" -ForegroundColor Yellow
Write-Host "  Size    : $size KB" -ForegroundColor Yellow
Write-Host "  Path    : $zipPath" -ForegroundColor Yellow
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host ""
