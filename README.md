# Croco Reviewer

API для анализа Merge Requests в GitHub репозиториях с использованием Yandex GPT.

## 🚀 Запуск проекта

### Требования
- Docker
- `.env` файл с переменными окружения (см. `.env_example`)

### Запуск через Docker
1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/your-username/croco-reviewer.git
   cd croco-reviewer

2. Создайте .env файл на основе примера:
    ```bash
   cp .env_example .env
   
Заполните необходимые переменные (GitHub Token, Yandex Cloud credentials).

3. Соберите и запустите контейнер:
    ```bash
   docker build -t croco-reviewer .
   docker run -p 8000:8000 --env-file .env croco-reviewer

## Пример запроса
После запуска API будет доступно на `http://localhost:8000`.

Пример запроса через curl:

   ```bash
   curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "repo": "owner/repo",
       "user": "github-username",
       "start_date": "2023-01-01",
       "end_date": "2023-12-31",
       "local_repo_path": "/path_to_local_repo"
     }'
   ```

## 🔧 Конфигурация
`GITHUB_KEY` - GitHub Personal Access Token

`FOLDER_ID` - Yandex Cloud Folder ID

`ACCESS_KEY` - Yandex Cloud IAM Token

## 📊 Пример ответа
```json
{
  "metadata": {
    "repo": "owner/repo",
    "user": "github-username",
    "period": {
      "start": "2023-01-01",
      "end": "2023-12-31"
    },
    "total": 3
  },
  "results": [
    {
      "mr_number": 1,
      "url": "https://github.com/owner/repo/commit/abc123",
      "complexity": "M",
      "problems": {
        "minor": [...],
        "regular": [...],
        "critical": [...]
      },
      "score": "8.5/10"
    }
  ]
}
```

## 🛠 Технологии
- FastAPI - веб-фреймворк

- Poetry - управление зависимостями

- Yandex GPT - анализ кода

- GitHub API - сбор данных о MR


### Примечания:
1. Перед первым запуском создайте `.env` файл на основе `.env.example` с вашими ключами.
2. Для локальной разработки можно использовать:
   ```bash
   poetry install
   poetry run uvicorn croco-reviewer.croco_reviewer.main:app --reload

3. В продакшн-среде рекомендуется использовать:
   ```dockerfile
   RUN poetry install --only main --no-dev