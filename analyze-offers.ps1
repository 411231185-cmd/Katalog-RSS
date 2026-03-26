#Requires -Version 5.1
<#
.SYNOPSIS
    Product catalog analyzer - FINAL WORKING VERSION
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ============================================================================
# CONFIGURATION
# ============================================================================

$FilePath = "C:\GitHub-Repositories\Katalog-RSS\all-offers-list.txt"
$OutputDir = [System.IO.Path]::GetDirectoryName($FilePath)
$BaseName = [System.IO.Path]::GetFileNameWithoutExtension($FilePath)

$UniqueFile = Join-Path $OutputDir "$BaseName-unique.txt"
$DupesFile = Join-Path $OutputDir "$BaseName-dupes.txt"
$SimilarGroupsFile = Join-Path $OutputDir "$BaseName-similar-groups.csv"
$ReportFile = Join-Path $OutputDir "$BaseName-report.txt"

# Stop-words
$StopWords = @{}
@(
    'dlya', 'i', 'v', 'vo', 'na', 'k', 'ko', 'po', 's', 'so', 'iz', 'ot', 'pod', 'nad',
    'pri', 'bez', 'za', 'ob', 'o', 'a', 'ili', 'eto', 'kak', 'nabor', 'komplekt',
    'the', 'a', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from'
) | ForEach-Object { $StopWords[$_] = $true }

# ============================================================================
# OUTPUT FUNCTIONS
# ============================================================================

function Write-LogInfo {
    param([string]$Message)
    Write-Host "[*] $Message" -ForegroundColor Cyan
}

function Write-LogSuccess {
    param([string]$Message)
    Write-Host "[+] $Message" -ForegroundColor Green
}

function Write-LogWarning {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor Yellow
}

function Write-LogError {
    param([string]$Message)
    Write-Host "[-] $Message" -ForegroundColor Red
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host ""
}

# ============================================================================
# PROCESSING FUNCTIONS
# ============================================================================

function Normalize-Product {
    param([string]$Text)
    
    $normalized = $Text.ToLower()
    $normalized = $normalized -replace '[-_/\\]', ' '
    $normalized = $normalized -replace '[^\p{L}\p{N}\s]', ''
    $normalized = $normalized -replace '\s+', ' '
    return $normalized.Trim()
}

function Get-SignificantWords {
    param([string]$NormalizedText)
    
    if ([string]::IsNullOrWhiteSpace($NormalizedText)) {
        return @()
    }
    
    [string[]]$words = @($NormalizedText -split '\s+' | Where-Object { $_ -and $_.Length -gt 0 })
    [string[]]$significant = @()
    
    foreach ($word in $words) {
        if ($word.Length -gt 2 -and -not $StopWords[$word]) {
            $significant += $word
        }
    }
    
    return @($significant)
}

function Get-WordSignature {
    param([string]$NormalizedText)
    
    [string[]]$words = @(Get-SignificantWords -NormalizedText $NormalizedText)
    
    if ($words.Count -eq 0) {
        return ""
    }
    
    [string[]]$sorted = @($words | Sort-Object -Unique)
    return ($sorted -join '|')
}

function Get-CommonWordsCount {
    param(
        [string[]]$Words1,
        [string[]]$Words2
    )
    
    if ($Words1.Count -eq 0 -or $Words2.Count -eq 0) {
        return 0
    }
    
    $common = 0
    foreach ($w1 in $Words1) {
        if ($Words2 -contains $w1) {
            $common++
        }
    }
    
    return $common
}

function Escape-CsvField {
    param([string]$Field)
    
    if ($Field -match '[",\r\n]') {
        return '"' + ($Field -replace '"', '""') + '"'
    }
    return $Field
}

# ============================================================================
# MAIN CODE
# ============================================================================

Write-Host ""
Write-Host ("╔" + ("=" * 78) + "╗")
Write-Host ("║  PRODUCT CATALOG ANALYZER AND CLEANUP  ".PadRight(79) + "║")
Write-Host ("╚" + ("=" * 78) + "╝")
Write-Host ""

if (-not (Test-Path $FilePath)) {
    Write-LogError "File not found: $FilePath"
    exit 1
}

Write-LogInfo "Reading file: $FilePath"

try {
    [string[]]$allLines = @(Get-Content -Path $FilePath -Encoding UTF8 -ErrorAction Stop | 
                            Where-Object { $_ -and $_.Trim() -ne '' })
}
catch {
    Write-LogError "Error reading file: $_"
    exit 1
}

$totalCount = $allLines.Count
Write-LogSuccess "Loaded items: $totalCount"
Write-Host ""

# ============================================================================
# STAGE 1: EXACT DUPLICATES
# ============================================================================

Write-Header "STAGE 1: Normalization and exact duplicates detection"

Write-LogInfo "Processing items..."

$normalizedMap = @{}
$allDuplicatesMap = @{}

foreach ($line in $allLines) {
    $normalized = Normalize-Product -Text $line
    
    if ([string]::IsNullOrEmpty($normalized)) {
        continue
    }
    
    if (-not $normalizedMap.ContainsKey($normalized)) {
        $normalizedMap[$normalized] = $line
        $allDuplicatesMap[$normalized] = @($line)
    }
    else {
        $allDuplicatesMap[$normalized] += $line
    }
}

# Count duplicates
$exactDuplicatesCount = 0
$duplicatesDetails = [System.Collections.ArrayList]@()

foreach ($norm in $allDuplicatesMap.Keys) {
    [string[]]$copies = @($allDuplicatesMap[$norm])
    $copyCount = $copies.Count
    
    if ($copyCount -gt 1) {
        $exactDuplicatesCount += ($copyCount - 1)
        [void]$duplicatesDetails.Add([PSCustomObject]@{
            Normalized = $norm
            Original = $copies[0]
            Copies = $copies
            Count = $copyCount
        })
    }
}

[string[]]$uniqueAfterExactDedup = @($normalizedMap.Values)

Write-LogSuccess "Found exact duplicates: $exactDuplicatesCount"
Write-LogSuccess "Unique items (after exact dedup): $($uniqueAfterExactDedup.Count)"
Write-Host ""

# ============================================================================
# STAGE 2: BUILD WORD SIGNATURES
# ============================================================================

Write-Header "STAGE 2: Building word signatures for similarity detection"

Write-LogInfo "Computing word signatures for $($uniqueAfterExactDedup.Count) items..."

$itemSignatures = @{}
$progressCounter = 0

foreach ($item in $uniqueAfterExactDedup) {
    $normalized = Normalize-Product -Text $item
    [string[]]$words = @(Get-SignificantWords -NormalizedText $normalized)
    $wordCount = $words.Count
    $signature = Get-WordSignature -NormalizedText $normalized
    
    $itemSignatures[$item] = @{
        Normalized = $normalized
        Words = $words
        WordCount = $wordCount
        Signature = $signature
    }
    
    $progressCounter++
    if (($progressCounter % 5000) -eq 0) {
        Write-Host "`rProcessed: $progressCounter / $($uniqueAfterExactDedup.Count)" -NoNewline
    }
}

Write-Host "`rProcessed: $($uniqueAfterExactDedup.Count) / $($uniqueAfterExactDedup.Count)" 
Write-Host ""

# ============================================================================
# STAGE 3: FIND SIMILAR ITEMS
# ============================================================================

Write-Header "STAGE 3: Finding similar items (optimized comparison)"

Write-LogInfo "Comparing items by similarity..."

$similarityPairs = [System.Collections.ArrayList]@()
$progressCounter = 0
$startTime = Get-Date

for ($i = 0; $i -lt $uniqueAfterExactDedup.Count; $i++) {
    $item1 = $uniqueAfterExactDedup[$i]
    $sig1 = $itemSignatures[$item1]
    [string[]]$words1 = $sig1.Words
    $w1Count = $sig1.WordCount
    
    if ($w1Count -eq 0) {
        $progressCounter++
        continue
    }
    
    for ($j = $i + 1; $j -lt $uniqueAfterExactDedup.Count; $j++) {
        $item2 = $uniqueAfterExactDedup[$j]
        $sig2 = $itemSignatures[$item2]
        [string[]]$words2 = $sig2.Words
        $w2Count = $sig2.WordCount
        
        if ($w2Count -eq 0) {
            continue
        }
        
        if ($sig1.Signature -eq $sig2.Signature -and $sig1.Signature -ne "") {
            continue
        }
        
        $commonCount = Get-CommonWordsCount -Words1 $words1 -Words2 $words2
        
        if ($commonCount -ge 2) {
            $level = if ($commonCount -ge 3) { "Strong" } else { "Probable" }
            
            [void]$similarityPairs.Add([PSCustomObject]@{
                Item1 = $item1
                Item2 = $item2
                CommonCount = $commonCount
                Level = $level
            })
        }
    }
    
    $progressCounter++
    if (($progressCounter % 2000) -eq 0) {
        $elapsed = (Get-Date) - $startTime
        $rate = if ($elapsed.TotalSeconds -gt 0) { $progressCounter / $elapsed.TotalSeconds } else { 0 }
        $remaining = if ($rate -gt 0) { [Math]::Round(($uniqueAfterExactDedup.Count - $progressCounter) / $rate) } else { 0 }
        Write-Host "`rCompared: $progressCounter / $($uniqueAfterExactDedup.Count) | ETA: ${remaining}s" -NoNewline
    }
}

Write-Host "`rCompared: $($uniqueAfterExactDedup.Count) / $($uniqueAfterExactDedup.Count) - COMPLETE" 
Write-Host ""

Write-LogSuccess "Found similarity pairs: $($similarityPairs.Count)"

[PSCustomObject[]]$strongPairs = @($similarityPairs | Where-Object { $_.Level -eq "Strong" })
[PSCustomObject[]]$probablePairs = @($similarityPairs | Where-Object { $_.Level -eq "Probable" })

$strongCount = $strongPairs.Count
$probableCount = $probablePairs.Count

Write-LogWarning "  - Strong similarity (3+ words): $strongCount"
Write-LogWarning "  - Probable similarity (2 words): $probableCount"
Write-Host ""

# ============================================================================
# STAGE 4: GROUP RELATED ITEMS
# ============================================================================

Write-LogInfo "Grouping related items..."

$groups = @{}
$groupId = 0

foreach ($pair in $similarityPairs) {
    $item1 = $pair.Item1
    $item2 = $pair.Item2
    
    $group1 = $null
    $group2 = $null
    
    foreach ($gid in $groups.Keys) {
        if ($groups[$gid] -contains $item1) {
            $group1 = $gid
        }
        if ($groups[$gid] -contains $item2) {
            $group2 = $gid
        }
    }
    
    if ($null -eq $group1 -and $null -eq $group2) {
        $groups[$groupId] = @($item1, $item2)
        $groupId++
    }
    elseif ($null -ne $group1 -and $null -eq $group2) {
        if ($groups[$group1] -notcontains $item2) {
            $groups[$group1] += $item2
        }
    }
    elseif ($null -eq $group1 -and $null -ne $group2) {
        if ($groups[$group2] -notcontains $item1) {
            $groups[$group2] += $item1
        }
    }
    elseif ($group1 -ne $group2) {
        $groups[$group1] += $groups[$group2]
        $groups.Remove($group2)
    }
}

Write-LogSuccess "Found groups of similar items: $($groups.Count)"
Write-Host ""

# ============================================================================
# STAGE 5: SAVE RESULTS
# ============================================================================

Write-Header "STAGE 5: Saving results"

Write-LogInfo "Saving unique items..."
$uniqueAfterExactDedup | Out-File -FilePath $UniqueFile -Encoding UTF8 -Force
Write-LogSuccess "File: $UniqueFile ($($uniqueAfterExactDedup.Count) items)"

Write-LogInfo "Saving exact duplicates info..."
$dupesReport = [System.Collections.ArrayList]@()
[void]$dupesReport.Add("EXACT DUPLICATES (IDENTICAL AFTER NORMALIZATION)")
[void]$dupesReport.Add("=" * 80)
[void]$dupesReport.Add("")

foreach ($entry in $duplicatesDetails) {
    [void]$dupesReport.Add("ORIGINAL: $($entry.Original)")
    [void]$dupesReport.Add("Normalized: $($entry.Normalized)")
    [void]$dupesReport.Add("Total copies: $($entry.Count)")
    for ($i = 1; $i -lt $entry.Copies.Count; $i++) {
        [void]$dupesReport.Add("  [$i] $($entry.Copies[$i])")
    }
    [void]$dupesReport.Add("")
}

$dupesReport | Out-File -FilePath $DupesFile -Encoding UTF8 -Force
Write-LogSuccess "File: $DupesFile ($($duplicatesDetails.Count) groups)"

Write-LogInfo "Saving similar items groups (CSV)..."
$similarReport = [System.Collections.ArrayList]@()
[void]$similarReport.Add("group_key,count,similarity_level,sample_item,all_items")

$groupIndex = 1
foreach ($gid in ($groups.Keys | Sort-Object)) {
    $groupItems = $groups[$gid]
    
    $maxLevel = "Weak"
    foreach ($pair in $similarityPairs) {
        if (($groupItems -contains $pair.Item1) -and ($groupItems -contains $pair.Item2)) {
            if ($pair.Level -eq "Strong") {
                $maxLevel = "Strong"
                break
            }
            elseif ($pair.Level -eq "Probable" -and $maxLevel -ne "Strong") {
                $maxLevel = "Probable"
            }
        }
    }
    
    $sampleItem = $groupItems[0]
    $allItems = $groupItems -join " | "
    
    $sampleItemEsc = Escape-CsvField -Field $sampleItem
    $allItemsEsc = Escape-CsvField -Field $allItems
    
    [void]$similarReport.Add("$groupIndex,$($groupItems.Count),$maxLevel,$sampleItemEsc,$allItemsEsc")
    $groupIndex++
}

$similarReport | Out-File -FilePath $SimilarGroupsFile -Encoding UTF8 -Force
Write-LogSuccess "File: $SimilarGroupsFile ($($groups.Count) groups)"

Write-LogInfo "Saving detailed report..."

$report = [System.Collections.ArrayList]@()
[void]$report.Add("╔" + ("=" * 78) + "╗")
[void]$report.Add("║  REPORT: PRODUCT CATALOG ANALYSIS  ".PadRight(79) + "║")
[void]$report.Add("╚" + ("=" * 78) + "╝")
[void]$report.Add("")
[void]$report.Add("Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
[void]$report.Add("Source: $FilePath")
[void]$report.Add("")
[void]$report.Add("STATISTICS")
[void]$report.Add("─" * 80)
[void]$report.Add("Total items in source:                      $($totalCount.ToString().PadLeft(10))")
[void]$report.Add("Exact duplicates found and removed:          $($exactDuplicatesCount.ToString().PadLeft(10))")
[void]$report.Add("UNIQUE ITEMS (after cleanup):               $($uniqueAfterExactDedup.Count.ToString().PadLeft(10))")
[void]$report.Add("Compression ratio:                          $(([Math]::Round((($exactDuplicatesCount) / $totalCount) * 100, 2)).ToString().PadLeft(8))%")
[void]$report.Add("")
[void]$report.Add("SIMILARITY ANALYSIS")
[void]$report.Add("─" * 80)
[void]$report.Add("Similarity pairs found (2+ words):          $($similarityPairs.Count.ToString().PadLeft(10))")
[void]$report.Add("  - Strong (3+ words):                      $($strongCount.ToString().PadLeft(10))")
[void]$report.Add("  - Probable (2 words):                     $($probableCount.ToString().PadLeft(10))")
[void]$report.Add("Groups of similar items:                    $($groups.Count.ToString().PadLeft(10))")
[void]$report.Add("")
[void]$report.Add("OUTPUT FILES")
[void]$report.Add("─" * 80)
[void]$report.Add("1. $BaseName-unique.txt: $($uniqueAfterExactDedup.Count) items")
[void]$report.Add("2. $BaseName-dupes.txt: $($duplicatesDetails.Count) groups")
[void]$report.Add("3. $BaseName-similar-groups.csv: $($groups.Count) groups")
[void]$report.Add("4. $BaseName-report.txt: this report")
[void]$report.Add("")

$report | Out-File -FilePath $ReportFile -Encoding UTF8 -Force
Write-LogSuccess "File: $ReportFile"

Write-Host ""

# ============================================================================
# FINAL STATISTICS
# ============================================================================

Write-Host ("╔" + ("=" * 78) + "╗")
Write-Host ("║  FINAL STATISTICS  ".PadRight(79) + "║")
Write-Host ("╠" + ("=" * 78) + "╣")
Write-Host ("║  Total items in source:                   " + $totalCount.ToString().PadLeft(20) + " ║").Substring(0, 80)
Write-Host ("║  Exact duplicates removed:                " + $exactDuplicatesCount.ToString().PadLeft(20) + " ║").Substring(0, 80)
Write-Host ("║  UNIQUE ITEMS (final):                    " + $uniqueAfterExactDedup.Count.ToString().PadLeft(20) + " ║").Substring(0, 80)
Write-Host ("║  Groups of similar items found:           " + $groups.Count.ToString().PadLeft(20) + " ║").Substring(0, 80)
Write-Host ("║  Similarity pairs for review:             " + $similarityPairs.Count.ToString().PadLeft(20) + " ║").Substring(0, 80)
Write-Host ("╚" + ("=" * 78) + "╝")
Write-Host ""

if ($groups.Count -gt 0 -and $groups.Count -le 30) {
    Write-Header "Similar item groups (top 30)"
    
    $sortedGroupIds = @($groups.Keys | Sort-Object)
    $showCount = [Math]::Min(30, $sortedGroupIds.Count)
    
    for ($i = 0; $i -lt $showCount; $i++) {
        $gid = $sortedGroupIds[$i]
        $groupItems = $groups[$gid]
        
        $maxLevel = "Weak"
        foreach ($pair in $similarityPairs) {
            if (($groupItems -contains $pair.Item1) -and ($groupItems -contains $pair.Item2)) {
                if ($pair.Level -eq "Strong") {
                    $maxLevel = "Strong"
                    break
                }
                elseif ($pair.Level -eq "Probable" -and $maxLevel -ne "Strong") {
                    $maxLevel = "Probable"
                }
            }
        }
        
        $levelColor = if ($maxLevel -eq "Strong") { "Red" } else { "Yellow" }
        
        Write-Host "Group $($i + 1) [$maxLevel] ($($groupItems.Count) items):" -ForegroundColor $levelColor
        for ($j = 0; $j -lt [Math]::Min(3, $groupItems.Count); $j++) {
            Write-Host "  > $($groupItems[$j])" -ForegroundColor White
        }
        if ($groupItems.Count -gt 3) {
            Write-Host "  ... and $($groupItems.Count - 3) more" -ForegroundColor Gray
        }
        Write-Host ""
    }
}
elseif ($groups.Count -gt 30) {
    Write-Header "Similar item groups (preview)"
    Write-LogWarning "Found $($groups.Count) groups. Showing first 10:"
    
    $sortedGroupIds = @($groups.Keys | Sort-Object)
    
    for ($i = 0; $i -lt 10; $i++) {
        $gid = $sortedGroupIds[$i]
        $groupItems = $groups[$gid]
        Write-Host "Group $($i + 1): $($groupItems.Count) items" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-LogInfo "Full list available in: $SimilarGroupsFile"
}

Write-Host ""
Write-LogSuccess "ANALYSIS COMPLETED SUCCESSFULLY!"
Write-Host ""
Write-Host "Output files:" -ForegroundColor Cyan
Write-Host "  [+] $UniqueFile" -ForegroundColor Green
Write-Host "  [*] $DupesFile" -ForegroundColor White
Write-Host "  [!] $SimilarGroupsFile" -ForegroundColor Yellow
Write-Host "  [*] $ReportFile" -ForegroundColor White
Write-Host ""
