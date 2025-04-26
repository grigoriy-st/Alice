#!/bin/bash

# Упрощенный скрипт для Glitch
set -eu

# Отключаем буферизацию вывода Python
export PYTHONUNBUFFERED=true

# Проверяем наличие requirements.txt и устанавливаем зависимости
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Запускаем приложение напрямую, без виртуального окружения
python3 server.py