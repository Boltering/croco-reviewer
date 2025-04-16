import requests
import os
import json
import re
from datetime import datetime
# тут находятся настройки которые можно автоматизировать + мой токен от huggingface 
GITHUB_REPO = "swaitic/map-generation" # мой публичный репозиторий генерации карт для игры в ДнД
GITHUB_USER = "swaitic"
HUGGINGFACE_TOKEN = "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"
LOCAL_REPO_PATH = "local_path_if_you_have"
MR_START_DATE = "2025-04-01"
MR_END_DATE = datetime.today().strftime('%Y-%m-%d')
SAVE_PATH = "mr_analysis_report.json"
MODEL_NAME = "bigcode/starcoder" #по словам ИИ эксперта заебись моедль для анализа кода

headers = {
    "Authorization": f"Bearer {HUGGINGFACE_TOKEN}"
}
def get_user_commits(repo, author, per_page=5):
    url = f"https://api.github.com/repos/{repo}/commits"
    params = {"author": author, "per_page": per_page}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_commit_diff(repo, sha):
    url = f"https://api.github.com/repos/{repo}/commits/{sha}"
    response = requests.get(url)
    response.raise_for_status()
    commit_data = response.json()
    diffs = []
    for file in commit_data["files"]:
        if "patch" in file:
            diffs.append(f"--- {file['filename']}\n{file['patch']}")
    return "\n".join(diffs), commit_data.get("html_url", "URL неизвестен")

def extract_changed_identifiers(diff):
    pattern = re.compile(r"^\+.*\\bdef (\w+)\\b|\+.*\\bfunction (\w+)\\b|\+.*\\bclass (\w+)\\b", re.MULTILINE)
    matches = pattern.findall(diff)
    names = {name for group in matches for name in group if name}
    return list(names)

def find_usages(identifiers):
    usage_map = {}
    for root, _, files in os.walk(LOCAL_REPO_PATH):
        for file in files:
            if file.endswith((".py", ".java", ".php")):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    for i, line in enumerate(lines):
                        for ident in identifiers:
                            if ident in line:
                                usage_map.setdefault(ident, []).append((file_path, i + 1, line.strip()))
                except:
                    continue
    return usage_map

def review_merge_request(diff, commit_url, mr_number, usages):
    usages_str = "\n".join(
        f"- {ident}: используется в {', '.join(f'{os.path.relpath(f, LOCAL_REPO_PATH)}:{line}' for f, line, _ in usage_list)}"
        for ident, usage_list in usages.items()
    ) or "Нет явных применений"

    prompt = f"""
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
  "score": число от 1 до 10,
  "score_comment": "пояснение",
  "complexity": "S/M/L",
  "problems": [
    {{ "type": "Тип", "description": "Описание проблемы" }}
  ],
  "antipatterns": [
    {{ "name": "Название", "description": "Описание антипаттерна" }}
  ],
  "positives": [
    "Положительный момент 1",
    "Положительный момент 2"
  ],
  "impacts": [
    "Описание потенциального влияния на другие части кода"
  ]
}}
"""

    response = requests.post(
        f"https://api-inference.huggingface.co/models/{MODEL_NAME}",
        headers=headers,
        json={"inputs": prompt, "parameters": {"max_new_tokens": 1024}}
    )

    if response.status_code == 200:
        return response.json()[0].get("generated_text", "")
    else:
        print(f"Ошибка HuggingFace API: {response.status_code}, {response.text}")
        return None

def main():
    commits = get_user_commits(GITHUB_REPO, GITHUB_USER)
    results = []

    for idx, commit in enumerate(commits, start=1):
        sha = commit["sha"]
        diff, commit_url = get_commit_diff(GITHUB_REPO, sha)

        if not diff.strip():
            print(f"Коммит {sha} пустой, пропускаем.")
            continue

        identifiers = extract_changed_identifiers(diff)
        usages = find_usages(identifiers)
        review_json = review_merge_request(diff, commit_url, idx, usages)

        if review_json:
            try:
                parsed = json.loads(review_json)
                results.append(parsed)
                print(f"MR #{idx} обработан: оценка {parsed.get('score')}/10")
            except json.JSONDecodeError as e:
                print(f"Ошибка парсинга JSON от модели: {e}")
                print(review_json)

    report = {
        "metadata": {
            "repo": GITHUB_REPO,
            "user": GITHUB_USER,
            "period": {
                "start": MR_START_DATE,
                "end": MR_END_DATE
            },
            "total": len(results)
        },
        "results": results
    }

    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\nОтчёт сохранён в файл: {SAVE_PATH}")

if __name__ == "__main__":
    main()
