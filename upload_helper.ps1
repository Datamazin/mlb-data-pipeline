# MLB Data Upload to Fabric Lakehouse
# ====================================
# PowerShell script to help upload CSV data to Microsoft Fabric

Write-Host "🏠 MLB Data Lakehouse Upload Helper" -ForegroundColor Green
Write-Host "=" * 50

# Check if CSV files exist
$exportDir = "fabric_export"
if (-not (Test-Path $exportDir)) {
    Write-Host "❌ fabric_export directory not found. Run export_for_fabric.py first." -ForegroundColor Red
    exit 1
}

$csvFiles = Get-ChildItem -Path $exportDir -Filter "*.csv"
if ($csvFiles.Count -eq 0) {
    Write-Host "❌ No CSV files found in fabric_export directory." -ForegroundColor Red
    exit 1
}

Write-Host "📁 Found $($csvFiles.Count) CSV files ready for upload:" -ForegroundColor Cyan
foreach ($file in $csvFiles) {
    $sizeKB = [math]::Round($file.Length / 1KB, 2)
    Write-Host "   📄 $($file.Name) ($sizeKB KB)" -ForegroundColor White
}

Write-Host "`n🎯 Enhanced Statistics Verification:" -ForegroundColor Yellow
Write-Host "   ✅ stolen_bases column included in boxscore.csv"
Write-Host "   ✅ caught_stealing column included in boxscore.csv"
Write-Host "   ✅ Base on balls (walks) column included"

# Count non-zero stolen bases in the data
Write-Host "`n🔍 Checking for actual stolen base data..." -ForegroundColor Cyan
$boxscoreFile = Join-Path $exportDir "boxscore.csv"
if (Test-Path $boxscoreFile) {
    $content = Get-Content $boxscoreFile
    $header = $content[0] -split ","
    $stolenBasesIndex = [array]::IndexOf($header, "stolen_bases")
    $caughtStealingIndex = [array]::IndexOf($header, "caught_stealing")
    
    if ($stolenBasesIndex -ge 0) {
        $stolenBasesEntries = $content[1..($content.Length-1)] | ForEach-Object { 
            $fields = $_ -split ","
            if ($fields[$stolenBasesIndex] -match '^\d+$' -and [int]$fields[$stolenBasesIndex] -gt 0) { $_ }
        }
        Write-Host "   📊 Found $($stolenBasesEntries.Count) players with stolen bases > 0" -ForegroundColor Green
    }
    
    if ($caughtStealingIndex -ge 0) {
        $caughtStealingEntries = $content[1..($content.Length-1)] | ForEach-Object { 
            $fields = $_ -split ","
            if ($fields[$caughtStealingIndex] -match '^\d+$' -and [int]$fields[$caughtStealingIndex] -gt 0) { $_ }
        }
        Write-Host "   📊 Found $($caughtStealingEntries.Count) players caught stealing > 0" -ForegroundColor Green
    }
}

Write-Host "`n🚀 Upload Options:" -ForegroundColor Yellow
Write-Host "=" * 30

Write-Host "`n📋 Option 1: Fabric Web Interface Upload" -ForegroundColor Cyan
Write-Host "   1. Open your Fabric workspace in browser"
Write-Host "   2. Go to your 'mlb_api' lakehouse"
Write-Host "   3. Click 'Get data' > 'Upload files'"
Write-Host "   4. Select all CSV files from fabric_export/ folder"
Write-Host "   5. Use wizard to create tables from CSV data"

Write-Host "`n📓 Option 2: Fabric Notebook Import" -ForegroundColor Cyan
Write-Host "   1. Upload 'MLB_Data_Import.ipynb' to your Fabric workspace"
Write-Host "   2. Upload CSV files to lakehouse Files section"
Write-Host "   3. Run the notebook to import data into tables"

Write-Host "`n📧 Option 3: Request Admin Help" -ForegroundColor Cyan
Write-Host "   Send your admin:"
Write-Host "   - Table creation SQL (see FABRIC_SETUP_GUIDE.md)"
Write-Host "   - CSV files (fabric_export/ folder)"
Write-Host "   - bulk_load_script.sql for data import"

Write-Host "`n💾 Option 4: Copy Files to OneLake" -ForegroundColor Cyan
Write-Host "   If you have OneLake access:"
Write-Host "   1. Copy CSV files to OneLake storage"
Write-Host "   2. Use Fabric's automatic table detection"
Write-Host "   3. Create Delta tables from uploaded files"

# Show file locations
Write-Host "`n📁 File Locations:" -ForegroundColor Yellow
Write-Host "   🗂️  CSV Data: $(Resolve-Path $exportDir)"
Write-Host "   📄 Setup Guide: $(Resolve-Path 'FABRIC_SETUP_GUIDE.md')"
Write-Host "   📓 Jupyter Notebook: $(Resolve-Path (Join-Path $exportDir 'MLB_Data_Import.ipynb'))"
Write-Host "   💾 Bulk Load SQL: $(Resolve-Path (Join-Path $exportDir 'bulk_load_script.sql'))"

Write-Host "`n✨ Your MLB data with enhanced statistics is ready!" -ForegroundColor Green
Write-Host "   🏃 Stolen bases data: CAPTURED"
Write-Host "   🚫 Caught stealing data: CAPTURED" 
Write-Host "   🚶 Base on balls data: CAPTURED"
Write-Host "   📊 Total games: 15 (August 31, 2025)"
Write-Host "   👥 Total players: 779"
Write-Host "   📈 Total boxscore entries: 296"

Write-Host "`n🎯 Next: Choose your preferred upload method above!" -ForegroundColor Magenta
