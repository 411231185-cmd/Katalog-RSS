#Requires -Version 5.1
<#
.SYNOPSIS
    Extract missing offers with descriptions
    
.PARAMETER MissingFile
    File with missing offer names (НЕ СДЕЛАННО.md)
    
.PARAMETER SourceFile
    File with all offers and descriptions (RZN-список офферов+описание.md)
    
.PARAMETER OutputFile
    Output file with missing offers and descriptions (НЕ ХВАТАЕТ.md)
    
.EXAMPLE
    .\extract-missing-with-descriptions.ps1 `
        -MissingFile "МАШПОРТ_СПИСОК+НЕ СДЕЛАННО.md" `
        -SourceFile "RZN-список офферов+описание.md" `
        -OutputFile "НЕ ХВАТАЕТ.md"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$MissingFile,
    
    [Parameter(Mandatory = $true)]
    [string]$SourceFile,
    
    [Parameter(Mandatory = $true)]
    [string]$OutputFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host ""
Write-Host ("╔" + ("=" * 76) + "╗")
Write-Host ("║  EXTRACT MISSING OFFERS WITH DESCRIPTIONS".PadRight(77) + "║")
Write-Host ("╚" + ("=" * 76) + "╝")
Write-Host ""

# ============================================================================
# VALIDATION
# ============================================================================

if (-not (Test-Path $MissingFile)) {
    Write-Host "ERROR: Missing file not found: $MissingFile" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $SourceFile)) {
    Write-Host "ERROR: Source file not found: $SourceFile" -ForegroundColor Red
    exit 1
}

Write-Host "[*] Reading missing offers: $MissingFile" -ForegroundColor Cyan

# Read missing file
try {
    [string[]]$missingLines = @(Get-Content -Path $MissingFile -Encoding UTF8 -ErrorAction Stop | 
                                Where-Object { $_ -and $_.Trim() -ne '' })
}
catch {
    Write-Host "ERROR: Cannot read missing file: $_" -ForegroundColor Red
    exit 1
}

Write-Host "[+] Loaded missing offers: $($missingLines.Count)" -ForegroundColor Green

Write-Host "[*] Reading source file: $SourceFile" -ForegroundColor Cyan

# Read source file
try {
    [string[]]$sourceLines = @(Get-Content -Path $SourceFile -Encoding UTF8 -ErrorAction Stop)
}
catch {
    Write-Host "ERROR: Cannot read source file: $_" -ForegroundColor Red
    exit 1
}

Write-Host "[+] Loaded source lines: $($sourceLines.Count)" -ForegroundColor Green

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Normalize-Item {
    param([string]$Text)
    
    $norm = $Text.ToLower().Trim()
    $norm = $norm -replace '\s+', ' '
    $norm = $norm -replace '[«»"„"]', ''
    
    return $norm
}

function Find-OfferInSource {
    param(
        [string]$OfferName,
        [string[]]$SourceLines
    )
    
    $normalizedSearch = Normalize-Item -Text $OfferName
    $result = @()
    
    for ($i = 0; $i -lt $sourceLines.Count; $i++) {
        $line = $sourceLines[$i].Trim()
        
        # Skip empty lines
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }
        
        $normalizedLine = Normalize-Item -Text $line
        
        # Exact match or contains
        if ($normalizedLine -eq $normalizedSearch -or $normalizedLine -match [regex]::Escape($normalizedSearch)) {
            # Found the offer name, now get the description (next non-empty line)
            $description = ""
            
            for ($j = $i + 1; $j -lt $sourceLines.Count; $j++) {
                $nextLine = $sourceLines[$j].Trim()
                
                if (-not [string]::IsNullOrWhiteSpace($nextLine)) {
                    # Skip service lines and company names
                    if (-not ($nextLine -match 'Машиностроительный|Контактная информация|Скрыть записи|Договорная|В наличии|₽|руб')) {
                        $description = $nextLine
                    }
                    break
                }
            }
            
            $result += @{
                Name = $line
                Description = $description
                Index = $i
            }
        }
    }
    
    return $result
}

# ============================================================================
# EXTRACT OFFERS WITH DESCRIPTIONS
# ============================================================================

Write-Host "[*] Searching for offers with descriptions..." -ForegroundColor Cyan

$found = [System.Collections.ArrayList]@()
$notFound = [System.Collections.ArrayList]@()
$progressCounter = 0

foreach ($missingOffer in $missingLines) {
    $results = Find-OfferInSource -OfferName $missingOffer -SourceLines $sourceLines
    
    if ($results.Count -gt 0) {
        foreach ($result in $results) {
            [void]$found.Add([PSCustomObject]@{
                Name = $result.Name
                Description = $result.Description
            })
        }
    }
    else {
        [void]$notFound.Add($missingOffer)
    }
    
    $progressCounter++
    if (($progressCounter % 50) -eq 0) {
        Write-Host "`rProgress: $progressCounter / $($missingLines.Count)" -NoNewline
    }
}

Write-Host "`rProgress: $($missingLines.Count) / $($missingLines.Count) " 
Write-Host ""

Write-Host "[+] Found with descriptions: $($found.Count)" -ForegroundColor Green
Write-Host "[!] Not found: $($notFound.Count)" -ForegroundColor Yellow

# ============================================================================
# SAVE RESULTS
# ============================================================================

Write-Host ""
Write-Host "[*] Saving results..." -ForegroundColor Cyan

# Create backup if output file exists
if (Test-Path $OutputFile) {
    $backupPath = "$OutputFile.backup"
    Copy-Item -Path $OutputFile -Destination $backupPath -Force
    Write-Host "[+] Backup created: $backupPath" -ForegroundColor Green
}

# Build output content
$output = [System.Collections.ArrayList]@()

foreach ($item in $found) {
    [void]$output.Add($item.Name)
    [void]$output.Add($item.Description)
    [void]$output.Add("")  # Empty line separator
}

# Save to file
$output | Out-File -FilePath $OutputFile -Encoding UTF8 -Force
Write-Host "[+] Results saved: $OutputFile" -ForegroundColor Green

# Save not found list
if ($notFound.Count -gt 0) {
    $notFoundFile = "$OutputFile.not-found.txt"
    $notFound | Out-File -FilePath $notFoundFile -Encoding UTF8 -Force
    Write-Host "[!] Not found offers saved: $notFoundFile" -ForegroundColor Yellow
}

# ============================================================================
# SUMMARY REPORT
# ============================================================================

Write-Host ""
Write-Host ("╔" + ("=" * 76) + "╗")
Write-Host ("║  EXTRACTION REPORT".PadRight(77) + "║")
Write-Host ("╠" + ("=" * 76) + "╣")

$line1 = "║  Missing offers to find:           $($missingLines.Count.ToString().PadRight(38))"
if ($line1.Length -gt 80) { $line1 = $line1.Substring(0, 80) }
Write-Host $line1.PadRight(80) + "║"

$line2 = "║  Found with descriptions:          $($found.Count.ToString().PadRight(38))"
if ($line2.Length -gt 80) { $line2 = $line2.Substring(0, 80) }
Write-Host $line2.PadRight(80) + "║"

$line3 = "║  Not found:                        $($notFound.Count.ToString().PadRight(38))"
if ($line3.Length -gt 80) { $line3 = $line3.Substring(0, 80) }
Write-Host $line3.PadRight(80) + "║"

$percentage = if ($missingLines.Count -gt 0) { [Math]::Round(($found.Count / $missingLines.Count) * 100, 1) } else { 0 }
$line4 = "║  Success rate:                    $percentage%".PadRight(38)
if ($line4.Length -gt 80) { $line4 = $line4.Substring(0, 80) }
Write-Host $line4.PadRight(80) + "║"

Write-Host ("╚" + ("=" * 76) + "╝")

# ============================================================================
# PREVIEW
# ============================================================================

Write-Host ""
Write-Host "Preview (first 5 offers):" -ForegroundColor Green
Write-Host ""

for ($i = 0; $i -lt [Math]::Min(5, $found.Count); $i++) {
    $item = $found[$i]
    Write-Host "[$($i + 1)] NAME: $($item.Name)" -ForegroundColor White
    Write-Host "    DESC: $($item.Description.Substring(0, [Math]::Min(60, $item.Description.Length)))..." -ForegroundColor Gray
    Write-Host ""
}

Write-Host "[+] DONE!" -ForegroundColor Green
Write-Host ""
