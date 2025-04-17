import requests
import os
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from diffs_collectors import GitHubDiffsCollector
from analyzers import MergeRequestAnalyzer, CodeReviewPrompts, YandexGPTReviewer

load_dotenv()

app = FastAPI(title="GitHub Merge Request Analyzer")


class AnalysisRequest(BaseModel):
    repo: str
    user: str
    start_date: str
    end_date: str
    local_repo_path: str


@app.post("/analyze", response_model=Dict[str, Any])
async def analyze_mr(request: AnalysisRequest):
    """
    Анализирует Merge Requests в указанном репозитории GitHub для заданного пользователя и периода времени.

    Параметры:
    - repo: GitHub репозиторий в формате 'owner/repo'
    - user: Имя пользователя GitHub
    - start_date: Начальная дата периода анализа (формат YYYY-MM-DD)
    - end_date: Конечная дата периода анализа (формат YYYY-MM-DD)
    - local_repo_path: Путь к локальной копии репозитория (для поиска использования изменённых идентификаторов)

    Возвращает:
    - Отчёт с метаданными и результатами анализа
    """
    try:
        github_collector = GitHubDiffsCollector(os.getenv("GITHUB_KEY"))
        prompt_generator = CodeReviewPrompts()
        reviewer = YandexGPTReviewer(os.getenv("FOLDER_ID"), os.getenv("ACCESS_KEY"))

        analyzer = MergeRequestAnalyzer(github_collector, prompt_generator, reviewer)
        report = analyzer.analyze(
            repo=request.repo,
            user=request.user,
            local_repo_path=request.local_repo_path,
            start_date=request.start_date,
            end_date=request.end_date
        )

        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"GitHub API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def read_root():
    return {
        "message": "GitHub Merge Request Analyzer API",
        "endpoints": {
            "POST /analyze": "Анализирует Merge Requests для заданных параметров"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)