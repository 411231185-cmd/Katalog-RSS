Write-Host "\n=== УСТАНОВКА НАБОРА РАСШИРЕНИЙ ДЛЯ VS CODE ===" -ForegroundColor Green

# 0. Проверка наличия команды code
Write-Host "\n[0/4] Проверка VS Code CLI..." -ForegroundColor Yellow
$codeVersion = code --version 2>$null
if (-not $codeVersion) {
    Write-Host "Команда 'code' недоступна. Откройте VS Code > Command Palette > 'Shell Command: Install 'code' command in PATH' и повторите." -ForegroundColor Red
    return
} else {
    Write-Host "VS Code найден: $($codeVersion.Split([Environment]::NewLine)[0])" -ForegroundColor Green
}

# 1. Список расширений
Write-Host "\n[1/4] Подготовка списка расширений..." -ForegroundColor Yellow
$extensions = @(
    "GitHub.copilot",
    "GitHub.copilot-chat",
    "eamodio.gitlens",
    "GitHub.vscode-pull-request-github",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "humao.rest-client",
    "rangav.vscode-thunder-client",
    "ms-azuretools.vscode-docker",
    "esbenp.prettier-vscode",
    "ms-python.black-formatter",
    "yzhang.markdown-all-in-one",
    "ritwickdey.LiveServer",
    "GrapeCity.gc-excelviewer",
    "usernamehw.errorlens",
    "Gruntfuggly.todo-tree",
    "ms-vscode-remote.remote-ssh",
    "mikestead.dotenv",
    "spmeesseman.vscode-taskexplorer",
    "ms-toolsai.jupyter",
    "dbaeumer.vscode-eslint",
    "pranaygp.vscode-css-peek"
)

Write-Host "Будут установлены:" -ForegroundColor Cyan
$extensions | ForEach-Object { Write-Host "  • $_" -ForegroundColor White }

# 2. Установка расширений
Write-Host "\n[2/4] Установка расширений..." -ForegroundColor Yellow

foreach ($ext in $extensions) {
    Write-Host "Устанавливаю: $ext" -ForegroundColor Cyan
    $output = code --install-extension $ext --force 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Установлено: $ext" -ForegroundColor Green
    } else {
        Write-Host ("  Проблема при установке " + $ext) -ForegroundColor Yellow
        Write-Host "     $output" -ForegroundColor DarkGray
    }
}

# 3. Список установленных расширений
Write-Host "\n[3/4] Проверка установленных расширений (фильтр по ключевым)..." -ForegroundColor Yellow
$installed = code --list-extensions 2>&1
$extensions | ForEach-Object {
    if ($installed -match [regex]::Escape($_)) {
        Write-Host "  Найдено: $_" -ForegroundColor Green
    } else {
        Write-Host "  НЕ найдено: $_" -ForegroundColor Red
    }
}

# 4. Перезапуск VS Code
Write-Host "\n[4/4] Перезапускаем VS Code для применения расширений..." -ForegroundColor Yellow
Get-Process -Name "Code" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
code
Write-Host "\nГотово! Все возможные расширения установлены, VS Code перезапущен." -ForegroundColor Green

Write-Host "\nРекомендуемые следующие шаги:" -ForegroundColor Cyan
Write-Host "  1. Ctrl+Shift+P → 'Developer: Reload Window'" -ForegroundColor White
Write-Host "  2. Ctrl+Shift+P → 'GitHub: Sign In' (для Copilot и GitHub интеграции)" -ForegroundColor White
Write-Host "  3. Настроить форматтер по умолчанию (Prettier/Black) в Settings" -ForegroundColor White
Write-Host "  4. Включить Settings Sync, чтобы сохранить этот набор на других машинах" -ForegroundColor White
