import os
import json
from yandex_cloud_ml_sdk import YCloudML
from typing import Dict, List, Tuple, Optional, Any

from diffs_collectors import GitHubDiffsCollector

LOCAL_REPO_PATH = ''

class CodeReviewPrompts:
    """Класс для управления промптами для ревью кода."""

    @staticmethod
    def get_review_prompt(diff: str, commit_url: str, mr_number: int,
                          usages: Dict[str, List[Tuple[str, int, str]]]) -> str:
        """Сгенерировать промпт для анализа MR."""
        
        usages_str = "\n".join(
            f"- {ident}: используется в {', '.join(f'{os.path.relpath(f, LOCAL_REPO_PATH)}:{line}' for f, line, _ in usage_list)}"
            for ident, usage_list in usages.items()
        ) or "Нет явных применений"

        return f"""
Вы — AI-ассистент для анализа Merge Request (MR) в проектах на Java, Python, PHP.

Ваша задача — провести ревью кода, оценить его качество, выявить проблемы, антипаттерны и положительные аспекты,  
а также проанализировать **влияние изменений на остальной код**, где используются изменённые функции или классы.

--- DIFF ---
{diff}

--- ФУНКЦИИ/КЛАССЫ, ГДЕ ПРИМЕНЯЮТСЯ ИЗМЕНЕНИЯ ---
{usages_str}

Формат ответа (строго в JSON):
{{
  "mr_number": {mr_number},
  "url": "{commit_url}",
  "complexity": "S/M/L",
  "problems": {{
    "minor": [
      {{
        "type": "Тип проблемы",
        "description": "Описание с привязкой к коду",
        "lines": [номера строк или null]
      }}
    ],
    "regular": [
      {{
        "type": "Тип проблемы",
        "description": "Описание с привязкой к коду",
        "lines": [номера строк или null]
      }}
    ],
    "critical": [
      {{
        "type": "Тип проблемы",
        "description": "Описание с привязкой к коду",
        "lines": [номера строк или null]
      }}
    ]
  }},
  "antipatterns": [
    {{
      "name": "Название", 
      "description": "Описание антипаттерна",
      "lines": [номера строк или null]
    }}
  ],
  "positives": [
    {{
      "aspect": "Описание позитивного аспекта",
      "lines": [номера строк или null]
    }}
  ],
  "impacts": [
    {{
      "description": "Описание влияния",
      "affected_components": ["список затронутых компонентов"]
    }}
  ]
}}
"""


class YandexGPTReviewer:
    """Класс для взаимодействия с Yandex GPT API."""

    def __init__(self, folder_id, access_token):
        self.sdk = YCloudML(folder_id=folder_id, auth=access_token)
        self.model = self.sdk.models.completions("yandexgpt", model_version="rc").configure(temperature=0.3)

    def review_code(self, prompt: str) -> Optional[str]:
        """Отправить запрос на ревью кода в Yandex GPT."""
        try:
            result = self.model.run([
                {"role": "system", "text": "Code Review"},
                {"role": "user", "text": prompt}
            ])
            return result[0].text
        except Exception as e:
            print(f"Ошибка при обращении к YandexGPT: {e}")
            return None


class MergeRequestAnalyzer:
    """Основной класс для анализа Merge Requests."""

    def __init__(self, github_collector: GitHubDiffsCollector, 
                 prompt_generator: CodeReviewPrompts, 
                 reviewer: YandexGPTReviewer):
        self.github_collector = github_collector
        self.prompt_generator = prompt_generator
        self.reviewer = reviewer

    def analyze(self, repo: str, user: str, local_repo_path: str,
                start_date: str, end_date: str) -> Dict[str, Any]:
        """Основной метод анализа."""
        commits = self.github_collector.get_user_commits(repo, user)
        print(commits)
        results = []

        for idx, commit in enumerate(commits, start=1):
            sha = commit["sha"]
            diff, commit_url = self.github_collector.get_commit_diff(repo, sha)

            if not diff.strip():
                print(f"Коммит {sha} пустой, пропускаем.")
                continue

            identifiers = self.github_collector.extract_changed_identifiers(diff)
            usages = self.github_collector.find_usages(identifiers, local_repo_path)

            prompt = self.prompt_generator.get_review_prompt(diff, commit_url, idx, usages)
            review_json = self.reviewer.review_code(prompt)

            if review_json:
                print(review_json)
                try:
                    review_json = review_json.replace('```', '')
                    parsed = json.loads(review_json.strip())
                    results.append(parsed)
                    print(f"MR #{idx} обработан: оценка {parsed.get('score')}/10")
                except json.JSONDecodeError as e:
                    print(f"Ошибка парсинга JSON от модели: {e}")
                    

        return {
            "metadata": {
                "repo": repo,
                "user": user,
                "period": {
                    "start": start_date,
                    "end": end_date
                },
                "total": len(results)
            },
            "results": results
        }