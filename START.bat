@echo off
chcp 65001 > nul
title ExpertBot - Запуск бота
color 0A

echo ===============================================
echo        ExpertBot - Telegram бот-эксперт
echo ===============================================
echo.

:: Проверка наличия Python
echo [1/7] Проверка Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не установлен!
    echo Скачайте Python с https://www.python.org/downloads/
    echo Не забудьте поставить галочку "Add Python to PATH"
    pause
    exit /b 1
)
echo       ✅ Python найден

:: Создание виртуального окружения
echo [2/7] Создание виртуального окружения...
if not exist "venv" (
    python -m venv venv
    echo       ✅ Виртуальное окружение создано
) else (
    echo       ✅ Виртуальное окружение уже существует
)

:: Активация виртуального окружения
echo [3/7] Активация окружения...
call venv\Scripts\activate > nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Не удалось активировать окружение
    pause
    exit /b 1
)
echo       ✅ Окружение активировано

:: Установка зависимостей
echo [4/7] Проверка и установка зависимостей...
pip install -r requirements.txt > pip_install.log 2>&1
if errorlevel 1 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Некоторые зависимости не установились
    echo Проверьте файл pip_install.log
) else (
    echo       ✅ Зависимости установлены
)

:: Проверка наличия Node.js для админ-панели
echo [5/7] Проверка Node.js...
node --version > nul 2>&1
if errorlevel 1 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Node.js не установлен!
    echo Админ-панель не будет запущена
    echo Скачайте Node.js с https://nodejs.org/
    set ADMIN_AVAILABLE=0
) else (
    echo       ✅ Node.js найден
    set ADMIN_AVAILABLE=1
)

:: Создание .env файла если его нет
echo [6/7] Проверка конфигурации...
if not exist ".env" (
    echo ВНИМАНИЕ! Файл .env не найден!
    echo Создайте файл .env со следующими параметрами:
    echo.
    echo BOT_TOKEN=ваш_токен_от_BotFather
    echo EXPERT_TELEGRAM_ID=ID_эксперта
    echo DATABASE_URL=postgresql+asyncpg://postgres:пароль@localhost:5432/expert_bot
    echo ADMIN_USERNAME=admin
    echo ADMIN_PASSWORD_HASH=хеш_пароля
    echo JWT_SECRET=секретная_строка
    echo.
    pause
    exit /b 1
)
echo       ✅ Конфигурация проверена

:: Запуск бота
echo [7/7] Запуск сервисов...
echo.
echo ===============================================
echo    Запуск сервисов...
echo ===============================================
echo.

start "ExpertBot Bot" cmd /k "cd /d %~dp0 && venv\Scripts\activate && echo [БОТ] Запуск... && python -m bot.main"
timeout /t 2 /nobreak > nul

start "ExpertBot API" cmd /k "cd /d %~dp0 && venv\Scripts\activate && echo [API] Запуск на порту 8000... && uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 2 /nobreak > nul

:: Запуск админ-панели React
if "%ADMIN_AVAILABLE%"=="1" (
    if exist "admin\package.json" (
        echo [Админ-панель] Установка зависимостей (первый запуск может быть долгим)...
        start "ExpertBot Admin Panel" cmd /k "cd /d %~dp0admin && echo [АДМИН-ПАНЕЛЬ] Установка зависимостей... && npm install && echo [АДМИН-ПАНЕЛЬ] Запуск на порту 3000... && npm start"
    ) else (
        echo [ПРЕДУПРЕЖДЕНИЕ] Папка admin не найдена
    )
) else (
    echo [ПРЕДУПРЕЖДЕНИЕ] Админ-панель пропущена (Node.js не установлен)
)

:: Ожидание запуска сервисов
timeout /t 5 /nobreak > nul

:: Очистка экрана и вывод информации
cls
echo.
echo ===============================================
echo     ✅ ExpertBot УСПЕШНО ЗАПУЩЕН!
echo ===============================================
echo.
echo 📱 TELEGRAM БОТ
echo    Бот запущен и готов к работе
echo    Откройте Telegram и напишите боту
echo.
echo 🌐 АДМИН-ПАНЕЛЬ (React)
echo    Ссылка: http://localhost:3000
echo    Логин: admin
echo    Пароль: указан в файле .env
echo.
echo 📚 API ДОКУМЕНТАЦИЯ (Swagger)
echo    Ссылка: http://localhost:8000/docs
echo.
echo 💚 ПРОВЕРКА ЗДОРОВЬЯ
echo    Healthcheck: http://localhost:8000/health
echo.
echo ===============================================
echo    🛑 ЗАКРОЙТЕ ЭТО ОКНО ДЛЯ ОСТАНОВКИ БОТА
echo ===============================================
echo.

:: Ожидание закрытия окна (просто держит окно открытым)
cmd /k