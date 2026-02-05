# ============================================================================
# VS Code Startup Script for NEW-DIRECT-BY-MDT Repository
# ============================================================================
# Этот скрипт автоматически открывает важные файлы при запуске проекта
# 
# Использование:
#   1. Откройте .vscode/settings.json
#   2. Добавьте в конец (перед закрывающей скобкой):
#      "terminal.executeOnStartup": "./.vscode/startup.ps1"
#
# ============================================================================

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🚀 NEW-DIRECT-BY-MDT — VS CODE STARTUP                   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Определяем пути
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$checklistPath = Join-Path $repoRoot "CHECKLIST.md"
$readmePath = Join-Path $repoRoot "README.md"
$strategyPath = Join-Path $repoRoot "STRATEGY.md"

Write-Host "📂 Репозиторий: $repoRoot" -ForegroundColor Green
Write-Host ""

# Проверка статуса Git
Write-Host "🔍 Проверка Git статуса..." -ForegroundColor Yellow
$branch = & git rev-parse --abbrev-ref HEAD 2>$null
$status = & git status --short 2>$null

if ($branch) {
    Write-Host "📌 Текущая ветка: $branch" -ForegroundColor Green
    if ($status) {
        Write-Host "📝 Неподтвержденные изменения:" -ForegroundColor Yellow
        $status | ForEach-Object { Write-Host "   $_" }
    } else {
        Write-Host "✅ Рабочая директория чистая" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  Git репозиторий не найден" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📋 ВАЖНЫЕ ФАЙЛЫ ДЛЯ ОТКРЫТИЯ:" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Проверка наличия критичных файлов
$files = @(
    @{ name = "CHECKLIST.md"; path = $checklistPath; emoji = "📋"; priority = "КРИТИЧНО" },
    @{ name = "README.md"; path = $readmePath; emoji = "📖"; priority = "ВАЖНО" },
    @{ name = "STRATEGY.md"; path = $strategyPath; emoji = "🎯"; priority = "ВАЖНО" }
)

$missedFiles = @()

foreach ($file in $files) {
    if (Test-Path $file.path) {
        Write-Host "$($file.emoji) $($file.name) - $($file.priority)" -ForegroundColor Green
        Write-Host "   ✓ Найден в: $(Split-Path -Leaf $file.path)" -ForegroundColor Green
    } else {
        Write-Host "$($file.emoji) $($file.name) - $($file.priority)" -ForegroundColor Red
        Write-Host "   ✗ НЕ НАЙДЕН!" -ForegroundColor Red
        $missedFiles += $file.name
    }
}

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🎯 СЛЕДУЮЩИЕ ДЕЙСТВИЯ:" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 📖 Откройте в VS Code: CHECKLIST.md" -ForegroundColor Yellow
Write-Host "   Команда: code CHECKLIST.md" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 📌 Прочитайте текущие приоритеты" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. 🔧 Начните с задач в разделе 🔴 КРИТИЧНЫЕ" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. 💾 После каждого изменения обновляйте CHECKLIST.md" -ForegroundColor Yellow
Write-Host "   Команда: git add CHECKLIST.md && git commit -m 'update checklist'" -ForegroundColor Gray
Write-Host ""

if ($missedFiles.Count -gt 0) {
    Write-Host "⚠️  ВНИМАНИЕ: Отсутствуют файлы:" -ForegroundColor Red
    $missedFiles | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
    Write-Host ""
}

Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✨ Удачи в оптимизации! Начните с CHECKLIST.md 👇" -ForegroundColor Green
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Предложение открыть файл
$response = Read-Host "Открыть CHECKLIST.md в VS Code? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    if (Test-Path $checklistPath) {
        & code $checklistPath
        Write-Host "✅ CHECKLIST.md открыт в VS Code" -ForegroundColor Green
    } else {
        Write-Host "❌ CHECKLIST.md не найден!" -ForegroundColor Red
    }
}

Write-Host ""
