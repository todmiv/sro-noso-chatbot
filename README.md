# 🤖 SRO NOSO Chat-Bot

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Development Status](https://img.shields.io/badge/status-beta-orange.svg)](https://github.com/todmiv/sro-noso-chatbot)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://t.me/)

AI-powered Telegram chatbot для **Саморегулируемой организации «Нижегородское объединение строительных организаций» (СРО НОСО)**.

Бот предоставляет круглосуточную информационную поддержку членам СРО, используя современные технологии ИИ для автоматизации консультаций по законодательству, внутренним регламентам и процедурам организации.

## ✨ Основные возможности

| Категория | Возможности |
|-----------|-------------|
| 🤖 **Консультации** | Ответы 24/7 на вопросы по законам, внутренним регламентам и процедурам СРО с использованием ИИ |
| 📄 **Документы** | Поиск, скачивание и автоматические конспекты PDF/DOCX документов из базы знаний СРО |
| 🔍 **Реестры** | Проверка членства организаций по ИНН или названию в реестрах НОСТРОЙ и НОПРИЗ |
| 👤 **Персонализация** | Профиль участника с информацией об организации, напоминания о взносах и сроках допуска |
| 📊 **Аналитика** | Сбор статистики использования и обратной связи для улучшения сервиса |

## 🏗️ Архитектура

Проект построен на современной микросервисной архитектуре:

- **Backend**: FastAPI + Aiogram 3 (асинхронная обработка)
- **База данных**: PostgreSQL с SQLAlchemy ORM
- **Кеширование**: Redis для сессий и промежуточных данных
- **ИИ**: DeepSeek API + RAG (Retrieval-Augmented Generation) система
- **Векторный поиск**: FAISS для семантического поиска по документам
- **Мониторинг**: Prometheus метрики и health checks
- **Безопасность**: JWT аутентификация, шифрование данных

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.11+
- Docker & Docker Compose
- Git

### Установка и запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/todmiv/sro-noso-chatbot.git
   cd sro-noso-chatbot
   ```

2. **Создайте виртуальное окружение:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # для Linux/Mac
   # или
   venv\Scripts\activate     # для Windows
   ```

3. **Установите зависимости:**
   ```bash
   pip install -e ".[dev,test]"
   ```

4. **Настройте переменные окружения:**
   ```bash
   cp .env.example .env
   # Отредактируйте .env файл с вашими ключами API
   ```

5. **Запустите базу данных:**
   ```bash
   docker-compose up -d postgres redis
   ```

6. **Выполните миграции:**
   ```bash
   alembic upgrade head
   ```

7. **Запустите бота:**
   ```bash
   python -m app.main
   ```

## 📖 Использование

### Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Начало работы с ботом |
| `/help` | Справка по командам |
| `/profile` | Управление профилем пользователя |
| `/consultation` | Консультация с ИИ |
| `/documents` | Поиск и скачивание документов |
| `/membership` | Проверка членства в СРО |

### Примеры взаимодействия

1. **Консультация:**
   ```
   Пользователь: /consultation
   Бот: Опишите ваш вопрос по законодательству СРО
   Пользователь: Какие требования к членству в СРО?
   Бот: [Подробный ответ на основе документов]
   ```

2. **Поиск документов:**
   ```
   Пользователь: /documents
   Бот: Выберите категорию документов
   Пользователь: Устав СРО
   Бот: [Ссылка на скачивание + краткий конспект]
   ```

## ⚙️ Конфигурация

### Переменные окружения

Создайте файл `.env` на основе `.env.example`:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=sro_bot
POSTGRES_USER=sro_user
POSTGRES_PASSWORD=secure_password

# Redis
REDIS_URL=redis://localhost:6379/0

# Настройки приложения
ENVIRONMENT=development
DEBUG=true
```

### Docker развертывание

Для продакшена используйте Docker Compose:

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot

# Остановка
docker-compose down
```

## 🛠️ Разработка

### Структура проекта

```
sro-noso-chatbot/
├── app/                    # Основной код приложения
│   ├── ai_integration/     # Интеграция с ИИ (DeepSeek, RAG)
│   ├── bot/               # Telegram бот
│   │   ├── handlers/      # Обработчики команд
│   │   ├── keyboards/     # Клавиатуры
│   │   ├── middleware/    # Промежуточное ПО
│   │   └── filters/       # Фильтры сообщений
│   ├── database/          # Работа с БД
│   ├── models/            # SQLAlchemy модели
│   ├── services/          # Бизнес-логика
│   ├── monitoring/        # Метрики и мониторинг
│   └── utils/             # Утилиты
├── config/                # Конфигурация
├── data/                  # Данные (документы, индексы)
├── scripts/               # Скрипты обслуживания
└── tests/                 # Тесты
```

### Запуск тестов

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=app --cov-report=html

# Конкретный тест
pytest tests/test_specific_feature.py
```

### Форматирование кода

```bash
# Автоматическое форматирование
black app/
isort app/

# Проверка стиля
flake8 app/
mypy app/
```

## 📊 Мониторинг

### Метрики

Бот предоставляет Prometheus метрики по адресу `/metrics`:

- Количество активных пользователей
- Время отклика на запросы
- Статистика использования ИИ
- Состояние подключений к БД/Redis

### Health Checks

Проверка состояния сервисов доступна по `/health`:

```json
{
  "status": "OK",
  "services": {
    "database": true,
    "redis": true,
    "ai_service": true
  }
}
```

## 🤝 Внесение вклада

Мы приветствуем вклад в развитие проекта! Ознакомьтесь с:

- [CONTRIBUTING.md](CONTRIBUTING.md) - Руководство по внесению вклада
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) - Кодекс поведения
- [SECURITY.md](SECURITY.md) - Политика безопасности
- [TODO.md](TODO.md) - Список задач и недочетов

### Процесс разработки

1. Создайте issue для новой фичи или бага
2. Создайте ветку: `git checkout -b feature/your-feature-name`
3. Внесите изменения, следуя стилю кода
4. Напишите тесты
5. Создайте Pull Request

## 📋 Документация

- [Техническое задание (ТЗ)](TZ.md)
- [Журнал изменений](CHANGELOG.md)
- [Руководство по развертыванию](docs/deployment.md)
- [API документация](docs/api.md)

## 📄 Лицензия

Проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).

## 📞 Контакты

- **GitHub Issues**: [Сообщить о проблеме](https://github.com/todmiv/sro-noso-chatbot/issues)
- **Telegram**: [@sro_noso_support](https://t.me/sro_noso_support)
- **Email**: support@sro-noso.ru

## 🙏 Благодарности

- Команда СРО НОСО за поддержку и обратную связь
- Сообщество разработчиков за вклад в opensource
- DeepSeek за мощный AI API

---

> Проект находится на этапе **MVP** и активно развивается. Добро пожаловать в pull request'ы и предложения по улучшению! 🚀
