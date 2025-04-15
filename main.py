from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, List
from pr_collector import GitHubPRDiffCollector
from reviewer import Reviewer
import requests


app = FastAPI()


# Модель для входных данных запроса
class AnalysisRequest(BaseModel):
    repo: str
    username: Optional[str] = None
    email: Optional[str] = None
    start_date: str
    end_date: str

# Модель для ответа
# TODO: Добавить поля, не только что есть сейчас
class AnalysisResponse(BaseModel):
    bad_patterns: List[Dict]
    code_complexity: float
    good_things: List[Dict]
    code_quality: float
    total_diffs_analyzed: int
    status: str = "success"


@app.post("/analyze-pr-diffs", response_model=AnalysisResponse)
async def analyze_pr_diffs(request: AnalysisRequest):
    try:
        datetime.strptime(request.start_date, "%Y-%m-%d")
        datetime.strptime(request.end_date, "%Y-%m-%d")

        collector = GitHubPRDiffCollector()
        diffs = collector.collect_pr_diffs(
            repo=request.repo,
            username=request.username,
            email=request.email,
            start_date=request.start_date,
            end_date=request.end_date
        )

        report = Reviewer.report(diffs)

        return report

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"GitHub API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "GitHub PR Diff Analyzer Service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
