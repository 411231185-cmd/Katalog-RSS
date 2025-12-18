@echo off
chcp 65001 >nul
cls

REM 🚀 БАТНИК ДЛЯ ИНТЕГРАЦИИ UID/SKU В КАТАЛОГ СТАНКОАРТЕЛЬ
REM Скопируй этот файл в папку с integration_script.py
REM Двойной клик для запуска!

echo.
echo ====================================
echo   ИНТЕГРАЦИЯ UID/SKU
echo   Станкоартель РУССтанкоСБыт
echo ====================================
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ОШИБКА: Python не установлен!
    echo.
    echo Установи Python с https://www.python.org
    echo При установке отметь "Add Python to PATH"
    pause
    exit /b 1
)

echo ✅ Python найден
echo.

REM Запускаем скрипт интеграции
echo 🔄 Запуск скрипта интеграции...
echo.

python integration_script.py

if errorlevel 1 (
    echo.
    echo ❌ ОШИБКА при выполнении скрипта!
    echo Проверь путь к файлам в скрипте.
) else (
    echo.
    echo ✨ УСПЕШНО ЗАВЕРШЕНО!
)

echo.
echo Нажми любую клавишу для выхода...
pause >nul
