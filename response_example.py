import requests
from datetime import datetime

url = "http://localhost:8000/analyze"
data = {
    "repo": "AlfaInsurance/devQ_testData_PythonProject",
    "user": "VasilevArtem",
    "start_date": "2024-05-01",
    "end_date": datetime.today().strftime('%Y-%m-%d'),
    "local_repo_path": "local_path_if_you_have"
}

response = requests.post(url, json=data)
import json
with open("mr_report.json", "w", encoding="utf-8") as f:
    json.dump(response.json(), f, ensure_ascii=False, indent=2)
