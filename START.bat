@echo off
title Hustle Castle Bot - Установка
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo    HUSTLE CASTLE BOT - УСТАНОВКА
echo ========================================
echo.

:: Проверка Python
echo [1/3] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python не найден! Скачиваю...
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.12.0/python-3.12.0.exe -OutFile python_installer.exe"
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
    echo Python установлен!
) else (
    echo Python уже есть!
)
echo.

:: Установка библиотек
echo [2/3] Установка библиотек...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet pyautogui pygetwindow pillow pyscreeze
echo Библиотеки установлены!
echo.

:: Создание файла запуска
echo [3/3] Создание ярлыка...
echo @echo off > "Запустить бота.bat"
echo title Hustle Castle Bot >> "Запустить бота.bat"
echo cd /d "%~dp0" >> "Запустить бота.bat"
echo python "burmalcastle.py" >> "Запустить бота.bat"
echo pause >> "Запустить бота.bat"
echo Ярлык создан!
echo.

echo ========================================
echo    УСТАНОВКА ЗАВЕРШЕНА!
echo ========================================
echo.
echo Запустите файл "Запустить бота.bat"
echo.
pause
