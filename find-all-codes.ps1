#Requires -Version 5.1

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Путь к каталогу
$RootPath  = "C:\GitHub-Repositories\Katalog-RSS"
$OutputDir = $RootPath

$CodesFile   = Join-Path $OutputDir "all-codes.txt"
$ReportFile  = Join-Path $OutputDir "codes-report.csv"


# Регулярное выражение под шифры:
# - РТxxxx, ГСxxx, 16ВТ20П‑21, 1Н65, 1М63Н, 16К20, 16К20Ф3, 16К40Ф3, 1М65, 1516Ф3, 16Р30Ф3, 16Р40Ф3, 1А983, 1М983, 1Н983, 16К20ТС1,
# - РТ772Ф3, РТ783, РТ779Ф3, РТ983, РТ5004, UBB112, UBB112Ф3, РТ820Ф2, РТ820Ф3, РТ30101, РТ917, РТ5003, РТ5004, РТ905Ф1, РСС‑263, РТ595, РТ911Ф1, РТ4011, РТ693, РТ694, STR‑500Ф3, KZH1840, KZH1842 и т.п.

# Паттерн:
# - РТ/ГС/16/1Н/1М/(15)16/1А/1М/1Н/16К/16Р/РТ/STR/КЖ/KZH/1516/UBB/16ВТ/РСС и т.д. с цифрами и, опционально, Ф1/Ф2/Ф3, П‑21, П‑22, 80х10мм и т.п.
$Pattern = "\b(?:РТ|ГС|16[КРВМТ]|1[НМ]|1516|1А983|1M63H|RT|ГС|STR|KZH|КЖ|UBB|16ВТ|РСС|80х10) [-\w/]{0,1}\d{2,}(?:[А-Яa-zа-я]{1,3})?\b"


# Вспомогательные функции
function Write-LogInfo  { param([string]$Message); Write-Host "[*] $Message" -ForegroundColor Cyan }
function Write-LogSuccess{ param([string]$Message); Write-Host "[+] $Message" -ForegroundColor Green }
function Write-LogError  { param([string]$Message); Write-Host "[-] $Message" -ForegroundColor Red }

# Поиск всех файлов
Write-LogInfo "Поиск всех файлов в папке: $RootPath"
$allFiles = @(Get-ChildItem -Path $RootPath -Recurse -File -ErrorAction SilentlyContinue)
Write-LogSuccess "Найдено файлов: $($allFiles.Count)"

if ($allFiles.Count -eq 0) {
    Write-LogError "Нет файлов в каталоге или подкаталогах."
    exit 1
}

# Собираем все найденные шифры
$codeHits = @()
$uniqueCodes = @{}

foreach ($file in $allFiles) {
    $fileName = $file.FullName

    try {
        $content = Get-Content -Path $fileName -Encoding UTF8 -Raw -ErrorAction SilentlyContinue
    } catch {
        $content = $null
    }

    if ([string]::IsNullOrWhiteSpace($content)) {
        continue
    }

    $matches = [regex]::Matches($content, $Pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    foreach ($match in $matches) {
        $code = $match.Value.Trim()

        if ($code -match $Pattern) {
            if (-not $uniqueCodes.ContainsKey($code)) {
                $uniqueCodes[$code] = @()
            }
            $uniqueCodes[$code] += $fileName
        }
    }
}

Write-LogSuccess "Найдено уникальных шифров: $($uniqueCodes.Count)"

# Сохраняем все уникальные шифры в txt
$uniqueCodes.Keys | Sort-Object | Set-Content -Path $CodesFile -Encoding UTF8
Write-LogSuccess "Все шифры записаны в: $CodesFile"

# Отчёт: код, количество файлов, список файлов
$reportLines = @("code,file_count,files")

foreach ($code in $uniqueCodes.Keys | Sort-Object) {
    $files = $uniqueCodes[$code]
    $fileCount = @($files).Count
    $fileList = $files -join " | "
    $fileListEscaped = $fileList -replace '"', '""'
    $reportLine = "$code,$fileCount,""\""$fileListEscaped\"""""
    $reportLines += $reportLine
}

$reportLines | Out-File -FilePath $ReportFile -Encoding UTF8 -Force
Write-LogSuccess "Отчёт по шифрам записан в: $ReportFile"

Write-Host ""
Write-LogSuccess "ПОИСК ШИФРОВ ЗАВЕРШЁН!"
Write-Host "Уникальных шифров: $($uniqueCodes.Count)"
Write-Host "Файл со всеми шифрами: $CodesFile"
Write-Host "Отчёт по встречаемости: $ReportFile"