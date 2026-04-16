# Создаём исправленный скрипт filter
$scriptPath = "C:\GitHub-Repositories\Katalog-RSS\mashport-filter.ps1"

$scriptContent = @'
# MashPort CSV Filter - Удаление строк с отметкой "2"

param(
    [string]$InputFile = "C:\GitHub-Repositories\Katalog-RSS\МашПорт-список-RZN-чистый.csv.temp.csv",
    [string]$OutputFile = "C:\GitHub-Repositories\Katalog-RSS\МашПорт-список-RZN-очищенный.csv",
    [string]$FilterColumn = "L"
)

# COLORS
$colors = @{
    Success = 'Green'
    Error = 'Red'
    Warning = 'Yellow'
    Info = 'Cyan'
    Number = 'Magenta'
}

function Write-ColorOutput {
    param([string]$Message, [string]$Color = 'White')
    Write-Host $Message -ForegroundColor $Color
}

# ПРОВЕРКА ФАЙЛОВ
Write-ColorOutput "╔═══════════════════════════════════════════════════╗" $colors.Info
Write-ColorOutput "║  MashPort CSV Filter v2.0                        ║" $colors.Info
Write-ColorOutput "║  Удаление товаров с отметкой 2                  ║" $colors.Info
Write-ColorOutput "╚═══════════════════════════════════════════════════╝" $colors.Info
Write-Host ""

Write-ColorOutput "📁 Проверка файлов..." $colors.Info
Write-Host "  Input:  $InputFile"
Write-Host "  Output: $OutputFile"
Write-Host ""

if (!(Test-Path $InputFile)) {
    Write-ColorOutput "❌ ОШИБКА: Файл не найден!" $colors.Error
    Write-Host "   Путь: $InputFile"
    exit 1
}

Write-ColorOutput "✅ Файл найден" $colors.Success

# ЧТЕНИЕ CSV
Write-Host ""
Write-ColorOutput "📖 Чтение CSV файла..." $colors.Info

try {
    $content = Get-Content -Path $InputFile -Encoding UTF8 -ErrorAction Stop
    Write-ColorOutput "✅ Файл прочитан" $colors.Success
    
    $lineCount = if ($content -is [array]) { $content.Count } else { 1 }
    Write-ColorOutput "   Всего строк: $lineCount" $colors.Number
}
catch {
    Write-ColorOutput "❌ ОШИБКА при чтении файла: $($_)" $colors.Error
    exit 1
}

# ПАРСИНГ CSV
Write-Host ""
Write-ColorOutput "🔍 Парсинг CSV структуры..." $colors.Info

if ($lineCount -eq 0) {
    Write-ColorOutput "❌ ОШИБКА: Файл пуст!" $colors.Error
    exit 1
}

# Преобразуем в массив если одна строка
if ($content -isnot [array]) {
    $content = @($content)
}

$header = $content[0] -split ','
Write-Host "   Колонки: $($header -join ', ')"
Write-ColorOutput "   Всего колонок: $($header.Count)" $colors.Number

# Ищем индекс колонки
$filterColumnIndex = $header.IndexOf($FilterColumn)

if ($filterColumnIndex -eq -1) {
    Write-ColorOutput "⚠️  ВНИМАНИЕ: Колонка '$FilterColumn' не найдена!" $colors.Warning
    Write-Host "   Доступные колонки: $($header -join ', ')"
    $filterColumnIndex = -1
}
else {
    Write-ColorOutput "✅ Колонка найдена: '$FilterColumn' (индекс $filterColumnIndex)" $colors.Success
}

# ФИЛЬТРАЦИЯ
Write-Host ""
Write-ColorOutput "⚙️  Фильтрация строк..." $colors.Info

$cleanedLines = @($content[0])
$removedCount = 0
$keptCount = 1

for ($i = 1; $i -lt $content.Count; $i++) {
    $line = $content[$i]
    
    if ([string]::IsNullOrWhiteSpace($line)) {
        continue
    }
    
    $fields = $line -split ','
    
    if ($filterColumnIndex -ne -1 -and $filterColumnIndex -lt $fields.Count) {
        $cellValue = $fields[$filterColumnIndex].Trim()
        
        if ($cellValue -eq '2') {
            $removedCount++
            $productName = if ($fields.Count -gt 0) { $fields[0] } else { "Unknown" }
            Write-Host "   ✗ Удалена строка $i : $productName (L=$cellValue)" -ForegroundColor Red
            continue
        }
    }
    
    $cleanedLines += $line
    $keptCount++
}

Write-Host ""
Write-ColorOutput "📊 РЕЗУЛЬТАТЫ ФИЛЬТРАЦИИ:" $colors.Info
Write-ColorOutput "   • Всего строк: $($content.Count)" $colors.Number
Write-ColorOutput "   • Удалено строк: $removedCount" $colors.Warning
Write-ColorOutput "   • Оставлено строк: $keptCount" $colors.Success

# УДАЛЕНИЕ ДУБЛИКАТОВ
Write-Host ""
Write-ColorOutput "🔄 Удаление дубликатов..." $colors.Info

$uniqueLines = @($cleanedLines[0])
$uniqueSet = @{ }
$uniqueSet[$cleanedLines[0]] = $true
$dupCount = 0

for ($i = 1; $i -lt $cleanedLines.Count; $i++) {
    $line = $cleanedLines[$i]
    
    if (!$uniqueSet.ContainsKey($line)) {
        $uniqueSet[$line] = $true
        $uniqueLines += $line
    }
    else {
        $dupCount++
    }
}

if ($dupCount -gt 0) {
    Write-ColorOutput "   Удалено дубликатов: $dupCount" $colors.Warning
}
else {
    Write-ColorOutput "   Дубликатов не найдено" $colors.Success
}

# ЗАПИСЬ
Write-Host ""
Write-ColorOutput "💾 Запись в выходной файл..." $colors.Info

try {
    if (Test-Path $OutputFile) {
        Remove-Item $OutputFile -Force
        Write-ColorOutput "   Старый файл удален" $colors.Warning
    }
    
    $uniqueLines | Out-File -Path $OutputFile -Encoding UTF8 -ErrorAction Stop
    
    Write-ColorOutput "✅ Файл успешно создан!" $colors.Success
    Write-Host "   Путь: $OutputFile"
    
    $fileSize = (Get-Item $OutputFile).Length
    Write-ColorOutput "   Размер: $([math]::Round($fileSize / 1KB, 2)) KB" $colors.Number
    Write-ColorOutput "   Итоговых товаров: $($uniqueLines.Count - 1)" $colors.Number
}
catch {
    Write-ColorOutput "❌ ОШИБКА при записи файла: $($_)" $colors.Error
    exit 1
}

# ФИНАЛЬНЫЙ ОТЧЕТ
Write-Host ""
Write-ColorOutput "╔═══════════════════════════════════════════════════╗" $colors.Success
Write-ColorOutput "║  ✅ ОЧИСТКА ЗАВЕРШЕНА УСПЕШНО                    ║" $colors.Success
Write-ColorOutput "╚═══════════════════════════════════════════════════╝" $colors.Success

Write-Host ""
Write-ColorOutput "📊 ИТОГОВАЯ СТАТИСТИКА:" $colors.Info
Write-ColorOutput "   • Исходно товаров: $($content.Count - 1)" $colors.Number
Write-ColorOutput "   • Удалено (отметка 2): $removedCount" $colors.Warning
Write-ColorOutput "   • Удалено дубликатов: $dupCount" $colors.Warning
Write-ColorOutput "   • Итого в файле: $($uniqueLines.Count - 1)" $colors.Success

Write-Host ""
Write-Host "📁 Input:  $InputFile" -ForegroundColor Gray
Write-Host "📁 Output: $OutputFile" -ForegroundColor Gray

Write-Host ""
Write-ColorOutput "🎉 Готово!" $colors.Success
'@

# Сохраняем скрипт
$scriptContent | Out-File -Path $scriptPath -Encoding UTF8 -Force
Write-Host "✅ Скрипт создан: $scriptPath" -ForegroundColor Green

# Разрешаем выполнение
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force | Out-Null
Write-Host "✅ Политика выполнения обновлена" -ForegroundColor Green

# Запускаем скрипт
Write-Host ""
Write-Host "🚀 Запускаем скрипт..." -ForegroundColor Cyan
Write-Host ""

& $scriptPath