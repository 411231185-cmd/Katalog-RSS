@echo off
chcp 65001 > nul
start "RSS Watcher" cmd /k "cd /d C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары && python Watcher_RSS.py"
