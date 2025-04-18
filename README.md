# Croco Reviewer

API для анализа Merge Requests в GitHub репозиториях с использованием Yandex GPT.
Как 

## 🚀 Запуск проекта

### Требования
- `.env` файл с переменными окружения (см. `.env_example`)

### Запуск 
1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/Boltering/croco-reviewer.git
   cd croco-reviewer
   
2. Установите зависимости через Poetry:
   ```bash
   pip install poetry
   poetry shell
   poetry install
   ```

3. Создайте .env файл на основе примера:
    ```bash
   cp .env_example .env
   
Заполните его:
   ```ini
   GITHUB_KEY=ваш_github_token
   FOLDER_ID=ваш_yandex_cloud_folder_id
   ACCESS_KEY=ваш_yandex_cloud_iam_token
   ```

4. Запустите приложение:
    ```bash
   poetry run python croco_reviewer/main.py

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
    "mean_score": 8
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
