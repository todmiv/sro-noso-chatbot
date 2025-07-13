# ---------- Stage 1: builder ----------
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ---------- Stage 2: runtime ----------
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Системные зависимости для PDF-парсинга
RUN apt-get update && apt-get install -y gcc g++ poppler-utils && \
    rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*

# Копируем исходники
COPY . .

# Непривилегированный пользователь
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
CMD ["python", "-m", "app.main"]
