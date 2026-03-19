# MashPort CSV Cleaner - Обработка списка товаров
# Скрипт извлекает названия товаров после строки "Скрыть записи этой компании"

param(
    [string]$InputFile = "C:\GitHub-Repositories\Katalog-RSS\МашПорт-список-RZN.csv",
    [string]$OutputFile = "C:\GitHub-Repositories\Katalog-RSS\МашПорт-список-RZN-чистый.csv"
)

# ============ COLORS ============
$colors = @{
    Success = 'Green'
    Error = 'Red'
    Warning = 'Yellow'
    Info = 'Cyan'
    Number = 'Magenta'
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = 'White'
    )
    Write-Host $Message -ForegroundColor $Color
}

# ============ ПРОВЕРКА ФАЙЛОВ ============
Write-ColorOutput "╔════════════════════════════════════════════════════╗" $colors.Info
Write-ColorOutput "║  MashPort CSV Cleaner v1.0                        ║" $colors.Info
Write-ColorOutput "╚════════════════════════════════════════════════════╝" $colors.Info
Write-Host ""

Write-ColorOutput "📁 Проверка файлов..." $colors.Info
Write-Host "  Input:  $InputFile"
Write-Host "  Output: $OutputFile"
Write-Host ""

# Проверка существования исходного файла
if (!(Test-Path $InputFile)) {
    Write-ColorOutput "❌ ОШИБКА: Исходный файл не найден!" $colors.Error
    Write-Host "   Путь: $InputFile"
    exit 1
}

Write-ColorOutput "✅ Исходный файл найден" $colors.Success

# Проверка папки для выходного файла
$OutputDir = Split-Path -Parent $OutputFile
if (!(Test-Path $OutputDir)) {
    Write-ColorOutput "⚠️  Папка не существует, создаю..." $colors.Warning
    try {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
        Write-ColorOutput "✅ Папка создана: $OutputDir" $colors.Success
    }
    catch {
        Write-ColorOutput "❌ ОШИБКА при создании папки: $_" $colors.Error
        exit 1
    }
}

# ============ ЧТЕНИЕ ФАЙЛА ============
Write-Host ""
Write-ColorOutput "📖 Чтение файла..." $colors.Info

try {
    $fileContent = Get-Content -Path $InputFile -Encoding UTF8 -ErrorAction Stop
    Write-ColorOutput "✅ Файл прочитан успешно" $colors.Success
    Write-ColorOutput "   Строк в файле: $(($fileContent | Measure-Object -Line).Lines)" $colors.Number
}
catch {
    Write-ColorOutput "❌ ОШИБКА при чтении файла: $_" $colors.Error
    exit 1
}

# ============ ОБРАБОТКА ДАННЫХ ============
Write-Host ""
Write-ColorOutput "🔍 Поиск товаров..." $colors.Info

$products = @()
$targetMarker = "Скрыть записи этой компании"
$lineCount = $fileContent.Count

# Если это одна строка, преобразуем в массив
if ($fileContent -is [string]) {
    $fileContent = @($fileContent)
}

Write-Host ""

for ($i = 0; $i -lt $lineCount - 1; $i++) {
    $currentLine = $fileContent[$i]
    
    # Проверяем ТОЧНОЕ совпадение
    if ($currentLine -eq $targetMarker) {
        $nextLine = $fileContent[$i + 1]
        
        # Проверяем что следующая строка не пустая
        if (![string]::IsNullOrWhiteSpace($nextLine)) {
            $products += $nextLine
            Write-ColorOutput "   ✓ Найден товар: '$nextLine'" $colors.Success
            $i++ # Пропускаем следующую строку, т.к. уже обработали
        }
        else {
            Write-ColorOutput "   ⚠️  После маркера пустая строка на линии $($i+1)" $colors.Warning
        }
    }
}

Write-Host ""

# ============ СТАТИСТИКА ============
$foundCount = $products.Count

if ($foundCount -eq 0) {
    Write-ColorOutput "⚠️  Товары не найдены!" $colors.Warning
    Write-Host "   Проверьте формат файла и наличие строк: '$targetMarker'"
}
else {
    Write-ColorOutput "✅ Найдено товаров: $foundCount" $colors.Number
}

# ============ ЗАПИСЬ В ВЫХОДНОЙ ФАЙЛ ============
Write-Host ""
Write-ColorOutput "💾 Запись в выходной файл..." $colors.Info

try {
    # Если выходной файл существует, удаляем его
    if (Test-Path $OutputFile) {
        Remove-Item $OutputFile -Force
        Write-ColorOutput "   Старый файл удален" $colors.Warning
    }
    
    # Записываем товары в файл
    $products | Out-File -Path $OutputFile -Encoding UTF8 -ErrorAction Stop
    
    Write-ColorOutput "✅ Файл успешно создан!" $colors.Success
    Write-Host "   Путь: $OutputFile"
    
    # Проверяем что файл создан и показываем размер
    $fileSize = (Get-Item $OutputFile).Length
    Write-ColorOutput "   Размер: $([math]::Round($fileSize / 1KB, 2)) KB" $colors.Number
}
catch {
    Write-ColorOutput "❌ ОШИБКА при записи файла: $_" $colors.Error
    exit 1
}

# ============ ФИНАЛЬНЫЙ ОТЧЕТ ============
Write-Host ""
Write-ColorOutput "╔════════════════════════════════════════════════════╗" $colors.Success
Write-ColorOutput "║  ✅ ОБРАБОТКА ЗАВЕРШЕНА УСПЕШНО                   ║" $colors.Success
Write-ColorOutput "╚════════════════════════════════════════════════════╝" $colors.Success

Write-Host ""
Write-ColorOutput "📊 ИТОГОВАЯ СТАТИСТИКА:" $colors.Info
Write-ColorOutput "   • Всего найдено товаров: $foundCount" $colors.Number
Write-ColorOutput "   • Входной файл: $InputFile" $colors.Info
Write-ColorOutput "   • Выходной файл: $OutputFile" $colors.Info

# Показываем первые 5 и последние 5 товаров
if ($foundCount -gt 0) {
    Write-Host ""
    Write-ColorOutput "📝 ПРИМЕРЫ НАЙДЕННЫХ ТОВАРОВ:" $colors.Info
    
    if ($foundCount -le 10) {
        $products | ForEach-Object { Write-Host "   • $_" -ForegroundColor Gray }
    }
    else {
        Write-Host "   Первые 5:"
        $products[0..4] | ForEach-Object { Write-Host "   • $_" -ForegroundColor Gray }
        Write-Host "   ..."
        Write-Host "   Последние 5:"
        $products[($foundCount-5)..($foundCount-1)] | ForEach-Object { Write-Host "   • $_" -ForegroundColor Gray }
    }
}

Write-Host ""
Write-ColorOutput "🎉 Скрипт завершен!" $colors.Success