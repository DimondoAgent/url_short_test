# URL Shortener

Микросервис для сокращения ссылок на FastAPI + PostgreSQL.

## Стек

- FastAPI, Uvicorn
- SQLAlchemy 2, PostgreSQL
- Pydantic v2
- Docker, docker-compose
- pytest

## Запуск через Docker

```bash
cp .env.example .env
docker-compose up --build
```

API: http://localhost:8000  
Документация: http://localhost:8000/docs

## Запуск локально

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# В .env прописать DATABASE_URL с localhost вместо db
uvicorn app.main:app --reload
```

## Тесты

Запускаются без PostgreSQL — используют SQLite in-memory.

```bash
pytest test/ -v
```

## API

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/shorten` | Создать короткую ссылку |
| GET | `/{short_id}` | Редирект на оригинальный URL |
| GET | `/stats/{short_id}` | Статистика переходов |

### Пример

```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'
```

```json
{
  "id": 1,
  "short_id": "aB3xKp7",
  "original_url": "https://google.com",
  "clicks": 0,
  "created_at": "2025-04-09T12:00:00+00:00"
}
```