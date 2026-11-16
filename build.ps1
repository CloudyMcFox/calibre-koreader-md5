# Build and install the Koreader MD5 plugin into calibre
# Run from the plugin directory

$pluginDir = $PSScriptRoot
if (-not $pluginDir) { $pluginDir = Get-Location }

$zipName = "KoreaderMD5.zip"
$zipPath = Join-Path $pluginDir $zipName

# Remove old zip if exists
if (Test-Path $zipPath) { Remove-Item $zipPath }

# Files to include in the plugin ZIP
$files = @(
    "__init__.py",
    "ui.py",
    "main.py",
    "config.py",
    "plugin-import-name-koreader_md5.txt"
)

# Add images if icon exists
if (Test-Path (Join-Path $pluginDir "images\icon.png")) {
    $files += "images\icon.png"
}

# Create ZIP. Compress-Archive would flatten images\icon.png to icon.png,
# but the plugin loads 'images/icon.png', so add entries with their paths.
Add-Type -AssemblyName System.IO.Compression, System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::Open($zipPath, 'Create')
try {
    foreach ($f in $files) {
        $entry = $f -replace '\\', '/'
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
            $zip, (Join-Path $pluginDir $f), $entry) | Out-Null
    }
} finally {
    $zip.Dispose()
}

Write-Host "Created: $zipPath"
Write-Host ""
Write-Host "To install, run:"
Write-Host "  calibre-customize -a `"$zipPath`""
Write-Host ""
Write-Host "Or install via Calibre GUI: Preferences -> Plugins -> Load plugin from file"
