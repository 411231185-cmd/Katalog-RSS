# cleanup_repo.ps1 - Автоматическая очистка репозитория
$archiveDir = "._archive_to_delete"
$daysOld = 7

Write-Host "🧹 ОЧИСТКА РЕПОЗИТОРИЯ" -ForegroundColor Yellow

# 1. Перемещаем старые файлы в архив (кроме защищённых)
$protected = @(
    "ATALONNY-PERELIKOVKA.csv",
    "MASTER_WITH_HTML_LINKS copy.csv",
    ".git",
    "._archive_to_delete"
)

Get-ChildItem -File -Recurse | Where-Object {
    $file = $_
    $_.LastAccessTime -lt (Get-Date).AddDays(-$daysOld) -and
    -not ($protected | Where-Object { $file.FullName -like "*$_*" })
} | ForEach-Object {
    $dest = Join-Path $archiveDir $_.Name
    Move-Item $_.FullName $dest -Force
    Write-Host "📦 Архивировано: $($_.Name)" -ForegroundColor Gray
}

# 2. Удаляем файлы из архива старше 15 дней
Get-ChildItem "$archiveDir\*" | Where-Object {
    $_.LastWriteTime -lt (Get-Date).AddDays(-15)
} | ForEach-Object {
    Remove-Item $_.FullName -Force
    Write-Host "🗑️ Удалено: $($_.Name)" -ForegroundColor Red
}

# 3. Удаляем пустые файлы сразу
Get-ChildItem -File -Recurse | Where-Object {
    $_.Length -eq 0
} | Remove-Item -Force

Write-Host "✅ Очистка завершена!" -ForegroundColor Green
