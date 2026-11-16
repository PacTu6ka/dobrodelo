@echo off
chcp 65001 > nul
echo ========================================================
echo  Запуск сервиса «ДоброДело» (Платформа волонтерства)
echo ========================================================
echo.
if not exist "venv\Scripts\activate.bat" (
    echo [ОШИБКА] Виртуальное окружение venv не найдено!
    pause
    exit /b
)

call venv\Scripts\activate.bat

echo База данных: PostgreSQL (dobrodelo)
echo.
echo Сервер запускается по адресу: http://127.0.0.1:5000
echo Для остановки нажмите Ctrl + C
echo.
python run.py
pause
