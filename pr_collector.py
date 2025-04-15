import requests
from datetime import datetime
from typing import Optional

class GitHubPRDiffCollector:
    def __init__(self, github_token: str = None):
        """
        Инициализация коллектора diff'ов PR с GitHub

        :param github_token: Personal Access Token для GitHub API (необязательно, но увеличивает лимит запросов)
        """
        self.github_api_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"

    def get_user_prs(
        self,
        repo_owner: str,
        repo_name: str,
        username: Optional[str] = None,
        email: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> list[dict]:
        """
        Получить все PR пользователя за указанный период

        :param repo_owner: Владелец репозитория
        :param repo_name: Название репозитория
        :param username: Логин пользователя GitHub (хотя бы username или email должен быть указан)
        :param email: Email пользователя (хотя бы username или email должен быть указан)
        :param start_date: Начальная дата в формате YYYY-MM-DD
        :param end_date: Конечная дата в формате YYYY-MM-DD
        :return: Список PR пользователя
        """
        if not username and not email:
            raise ValueError("Необходимо указать либо username, либо email")

        prs = []
        page = 1

        # Преобразуем даты в объекты date
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

        while True:
            url = f"{self.github_api_url}/repos/{repo_owner}/{repo_name}/pulls"
            params = {
                "state": "all",
                "sort": "created",
                "direction": "desc",
                "page": page,
                "per_page": 100
            }

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if not data:
                break

            for pr in data:
                # Проверяем дату создания PR
                created_at = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ").date()

                if start_dt and created_at < start_dt:
                    # PR созданы раньше начальной даты, прекращаем поиск
                    return prs

                if end_dt and created_at > end_dt:
                    # Пропускаем PR созданные после конечной даты
                    continue

                # Проверяем автора PR
                user_match = (
                    (username and pr["user"]["login"].lower() == username.lower()) or
                    (email and pr["user"].get("email", "").lower() == email.lower())
                )

                if user_match:
                    prs.append(pr)

            page += 1

        return prs

    def get_commit_diffs(
        self,
        repo_owner: str,
        repo_name: str,
        pr_number: int
    ) -> list[dict]:
        """
        Получить diff'ы коммитов для конкретного PR

        :param repo_owner: Владелец репозитория
        :param repo_name: Название репозитория
        :param pr_number: Номер Pull Request
        :return: Список diff'ов коммитов в PR
        """
        url = f"{self.github_api_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/commits"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        commits = response.json()

        diffs = []
        for commit in commits:
            commit_sha = commit["sha"]
            # Получаем diff отдельного коммита
            commit_url = f"{self.github_api_url}/repos/{repo_owner}/{repo_name}/commits/{commit_sha}"
            commit_response = requests.get(commit_url, headers=self.headers)
            commit_response.raise_for_status()
            commit_data = commit_response.json()

            if "files" in commit_data:
                for file in commit_data["files"]:
                    diffs.append({
                        "pr_number": pr_number,
                        "commit_sha": commit_sha,
                        "commit_message": commit_data["commit"]["message"],
                        "filename": file["filename"],
                        "status": file["status"],
                        "additions": file.get("additions", 0),
                        "deletions": file.get("deletions", 0),
                        "patch": file.get("patch", "")
                    })

        return diffs

    def collect_pr_diffs(
        self,
        repo: str,
        username: Optional[str] = None,
        email: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> list[dict]:
        """
        Основной метод для сбора всех diff'ов из PR пользователя

        :param repo: Репозиторий в формате owner/repo
        :param username: Логин пользователя GitHub
        :param email: Email пользователя
        :param start_date: Начальная дата в формате YYYY-MM-DD
        :param end_date: Конечная дата в формате YYYY-MM-DD
        :return: Список всех diff'ов
        """
        repo_owner, repo_name = repo.split("/")

        print(f"Поиск PR пользователя {'@' + username if username else email} "
              f"в репозитории {repo} с {start_date} по {end_date}...")

        prs = self.get_user_prs(repo_owner, repo_name, username, email, start_date, end_date)

        if not prs:
            print("PR не найдены")
            return []

        all_diffs = []
        for pr in prs:
            print(f"Обработка PR #{pr['number']}: {pr['title']}")
            pr_diffs = self.get_commit_diffs(repo_owner, repo_name, pr["number"])
            all_diffs.extend(pr_diffs)

        print(f"\nВсего найдено {len(all_diffs)} diff'ов в {len(prs)} PR")
        return all_diffs

    @staticmethod
    def save_diffs_to_file(diffs: list[dict], filename: str):
        """
        Сохранить diff'ы в файл

        :param diffs: Список diff'ов
        :param filename: Имя файла для сохранения
        """
        with open(filename, "w", encoding="utf-8") as f:
            for diff in diffs:
                f.write(f"PR #{diff['pr_number']}\n")
                f.write(f"Commit: {diff['commit_sha']}\n")
                f.write(f"Message: {diff['commit_message']}\n")
                f.write(f"File: {diff['filename']} ({diff['status']})\n")
                f.write(f"Changes: +{diff['additions']} -{diff['deletions']}\n")
                f.write(f"Diff:\n{diff['patch']}\n")
                f.write("\n" + "="*80 + "\n\n")