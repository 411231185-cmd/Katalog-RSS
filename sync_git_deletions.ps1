# sync_git_deletions.ps1 - Синхронизация удалений с Git
cd C:\GitHub-Repositories\Katalog-RSS

Write-Host "🔄 СИНХРОНИЗАЦИЯ С GIT" -ForegroundColor Cyan

# Добавляем удалённые файлы в Git
git add -A

# Коммитим с датой
$date = Get-Date -Format "yyyy-MM-dd HH:mm"
git commit -m "🧹 Auto cleanup: $date"

# Пушим в GitHub
git push origin main

Write-Host "✅ Git синхронизирован!" -ForegroundColor Green
