$csvFile = "C:\GitHub-Repositories\Katalog-RSS\МашПорт-список-RZN-очищенный-CLEAN.csv"
$mdFile = "C:\GitHub-Repositories\Katalog-RSS\docs\Комплектующие\MashPort-TKP-RZN\Список офееров МашПорт-RSS-ЧТО ЕСТЬ.md"
$outDir = "C:\GitHub-Repositories\Katalog-RSS\docs\Комплектующие\MashPort-TKP-RZN"

$intersectionFile = Join-Path $outDir "ПЕРЕСЕЧЕНИЕ.txt"
$missingFile = Join-Path $outDir "НЕДОСТАЮЩИЕ.txt"
$falseMatchFile = Join-Path $outDir "ЛОЖНЫЕ_СОВПАДЕНИЯ.txt"

function Normalize-Name {
    param([string]$s)
    if ([string]::IsNullOrWhiteSpace($s)) { return "" }

    $s = $s.Trim()
    $s = $s.TrimStart('#').TrimStart('-').TrimStart('*').Trim()
    $s = $s.ToLowerInvariant()

    $s = $s -replace '[“”"]', ''
    $s = $s -replace '[\(\)\[\]\{\}]', ' '
    $s = $s -replace '[,;:]', ' '
    $s = $s -replace '\.+$', ''
    $s = $s -replace '\s+', ' '
    $s = $s.Trim()

    if ($s.EndsWith(",")) {
        $s = $s.Substring(0, $s.Length - 1).Trim()
    }

    $s = $s -replace '\s*-\s*', '-'
    $s = $s -replace '\s+', ' '
    return $s.Trim()
}

function Split-FirstColumn {
    param([string]$line)
    if ([string]::IsNullOrWhiteSpace($line)) { return "" }

    if ($line.StartsWith('"')) {
        $m = [regex]::Match($line, '^"((?:[^"]|"")*)"')
        if ($m.Success) { return $m.Groups[1].Value.Replace('""', '"') }
    }

    $parts = $line.Split(',')
    if ($parts.Count -gt 0) { return $parts[0] }
    return $line
}

function Similarity-Score {
    param(
        [string]$a,
        [string]$b
    )

    $a = Normalize-Name $a
    $b = Normalize-Name $b

    if ([string]::IsNullOrWhiteSpace($a) -or [string]::IsNullOrWhiteSpace($b)) { return 0 }
    if ($a -eq $b) { return 100 }

    $aChars = $a.ToCharArray()
    $bChars = $b.ToCharArray()
    $lenA = $aChars.Count
    $lenB = $bChars.Count
    $maxLen = [Math]::Max($lenA, $lenB)
    if ($maxLen -eq 0) { return 0 }

    $minLen = [Math]::Min($lenA, $lenB)
    $commonPrefix = 0
    for ($i = 0; $i -lt $minLen; $i++) {
        if ($aChars[$i] -eq $bChars[$i]) { $commonPrefix++ } else { break }
    }

    $prefixScore = [Math]::Round(($commonPrefix / $maxLen) * 100, 0)

    $containsScore = 0
    if ($a.Contains($b) -or $b.Contains($a)) {
        $containsScore = 75
    }

    $sharedWords = 0
    $aWords = $a -split ' '
    $bWords = $b -split ' '
    foreach ($w in $aWords) {
        if ($w.Length -ge 3 -and $bWords -contains $w) {
            $sharedWords++
        }
    }
    $wordScore = 0
    if (($aWords.Count + $bWords.Count) -gt 0) {
        $wordScore = [Math]::Round((($sharedWords * 2) / ($aWords.Count + $bWords.Count)) * 100, 0)
    }

    return [Math]::Max($prefixScore, [Math]::Max($containsScore, $wordScore))
}

if (!(Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir | Out-Null
}

$allOffers = @()
Get-Content $csvFile -Encoding UTF8 | ForEach-Object {
    $line = $_.Trim()
    if ([string]::IsNullOrWhiteSpace($line)) { return }

    $name = Split-FirstColumn $line
    $name = Normalize-Name $name
    if ($name) { $allOffers += $name }
}
$allOffers = $allOffers | Sort-Object -Unique

$existingOffers = @()
Get-Content $mdFile -Encoding UTF8 | ForEach-Object {
    $line = $_.Trim()
    if ([string]::IsNullOrWhiteSpace($line)) { return }

    $candidate = $line
    if ($candidate -match '^\s*#{1,6}\s+(.+?)\s*#*\s*$') {
        $candidate = $matches[1]
    }
    elseif ($candidate -match '^\s*[-*]\s+(.+)$') {
        $candidate = $matches[1]
    }

    $candidate = Normalize-Name $candidate
    if ($candidate) { $existingOffers += $candidate }
}
$existingOffers = $existingOffers | Sort-Object -Unique

$existingSet = @{}
foreach ($x in $existingOffers) { $existingSet[$x] = $true }

$intersection = @()
$missing = @()
$falseMatches = @()

foreach ($offer in $allOffers) {
    if ($existingSet.ContainsKey($offer)) {
        $intersection += $offer
    }
    else {
        $missing += $offer

        $bestMatch = $null
        $bestScore = 0

        foreach ($existing in $existingOffers) {
            $score = Similarity-Score $offer $existing
            if ($score -gt $bestScore) {
                $bestScore = $score
                $bestMatch = $existing
            }
        }

        if ($bestScore -ge 70 -and $bestMatch) {
            $falseMatches += "$offer -> $bestMatch (score: $bestScore)"
        }
    }
}

$intersection | Set-Content $intersectionFile -Encoding UTF8
$missing | Set-Content $missingFile -Encoding UTF8
$falseMatches | Set-Content $falseMatchFile -Encoding UTF8

Add-Content $intersectionFile ("ИТОГО: " + $intersection.Count)
Add-Content $missingFile ("ИТОГО: " + $missing.Count)
Add-Content $falseMatchFile ("ИТОГО: " + $falseMatches.Count)

Write-Host "ПЕРЕСЕЧЕНИЕ: $($intersection.Count)"
Write-Host "НЕДОСТАЮЩИЕ: $($missing.Count)"
Write-Host "ЛОЖНЫЕ_СОВПАДЕНИЯ: $($falseMatches.Count)"
Write-Host "Файлы сохранены в: $outDir"