# START.ps1 - Запуск ExpertBot
Write-Host "===============================================" -ForegroundColor Green
Write-Host "       ExpertBot - Telegram бот-эксперт" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

# Проверка Python
Write-Host "[1/7] Проверка Python..." -ForegroundColor Cyan
try {
    python --version | Out-Null
    Write-Host "      ✅ Python найден" -ForegroundColor Green
} catch {
    Write-Host "      ❌ Python не установлен!" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

# Создание venv
Write-Host "[2/7] Создание виртуального окружения..." -ForegroundColor Cyan
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "      ✅ Виртуальное окружение создано" -ForegroundColor Green
} else {
    Write-Host "      ✅ Виртуальное окружение уже существует" -ForegroundColor Green
}

# Активация
Write-Host "[3/7] Активация окружения..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1
Write-Host "      ✅ Окружение активировано" -ForegroundColor Green

# Установка зависимостей
Write-Host "[4/7] Установка зависимостей..." -ForegroundColor Cyan
pip install -r requirements.txt | Out-Null
Write-Host "      ✅ Зависимости установлены" -ForegroundColor Green

# Проверка Node.js
Write-Host "[5/7] Проверка Node.js..." -ForegroundColor Cyan
try {
    node --version | Out-Null
    Write-Host "      ✅ Node.js найден" -ForegroundColor Green
    $ADMIN_AVAILABLE = $true
} catch {
    Write-Host "      ⚠️ Node.js не установлен, админ-панель не запустится" -ForegroundColor Yellow
    $ADMIN_AVAILABLE = $false
}

# Проверка .env
Write-Host "[6/7] Проверка конфигурации..." -ForegroundColor Cyan
if (-not (Test-Path ".env")) {
    Write-Host "      ❌ Файл .env не найден!" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}
Write-Host "      ✅ Конфигурация проверена" -ForegroundColor Green

# Запуск сервисов
Write-Host "[7/7] Запуск сервисов..." -ForegroundColor Cyan
Write-Host ""

Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PSScriptRoot'; venv\Scripts\Activate; Write-Host '[БОТ] Запуск...' -ForegroundColor Green; python -m bot.main`""
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PSScriptRoot'; venv\Scripts\Activate; Write-Host '[API] Запуск на порту 8000...' -ForegroundColor Green; uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload`""
Start-Sleep -Seconds 2

if ($ADMIN_AVAILABLE -and (Test-Path "admin\package.json")) {
    Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PSScriptRoot\admin'; Write-Host '[АДМИН-ПАНЕЛЬ] Установка зависимостей...' -ForegroundColor Green; npm install; Write-Host '[АДМИН-ПАНЕЛЬ] Запуск на порту 3000...' -ForegroundColor Green; npm start`""
} else {
    Write-Host "      ⚠️ Админ-панель не запущена" -ForegroundColor Yellow
}

Start-Sleep -Seconds 5
Clear-Host

# Финальная информация
Write-Host "===============================================" -ForegroundColor Green
Write-Host "    ✅ ExpertBot УСПЕШНО ЗАПУЩЕН!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "📱 TELEGRAM БОТ" -ForegroundColor Cyan
Write-Host "    Бот запущен и готов к работе"
Write-Host "    Откройте Telegram и напишите боту"
Write-Host ""
Write-Host "🌐 АДМИН-ПАНЕЛЬ (React)" -ForegroundColor Cyan
Write-Host "    Ссылка: http://localhost:3000"
Write-Host "    Логин: admin"
Write-Host "    Пароль: указан в файле .env"
Write-Host ""
Write-Host "📚 API ДОКУМЕНТАЦИЯ (Swagger)" -ForegroundColor Cyan
Write-Host "    Ссылка: http://localhost:8000/docs"
Write-Host ""
Write-Host "💚 ПРОВЕРКА ЗДОРОВЬЯ" -ForegroundColor Cyan
Write-Host "    Healthcheck: http://localhost:8000/health"
Write-Host ""
Write-Host "===============================================" -ForegroundColor Yellow
Write-Host "    🛑 ЗАКРОЙТЕ ЭТО ОКНО ДЛЯ ОСТАНОВКИ БОТА" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Yellow
Write-Host ""

# Бесконечное ожидание
while ($true) { Start-Sleep -Seconds 1 }