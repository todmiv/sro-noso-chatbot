# scripts/setup.sh
#!/bin/bash
set -e

echo "Setting up SRO NOSO Chatbot..."

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Проверка наличия Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Создание .env файла если его нет
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your actual configuration values."
    exit 1
fi

# Создание необходимых директорий
mkdir -p logs uploads documents

# Сборка и запуск контейнеров
docker-compose build
docker-compose up -d

echo "Setup completed! Check the status with: docker-compose ps"
