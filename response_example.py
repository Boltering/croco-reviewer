import requests
from datetime import datetime

url = "http://localhost:8000/analyze"
data = {
    "repo": "swaitic/map-generation",
    "user": "swaitic",
    "start_date": "2025-04-01",
    "end_date": datetime.today().strftime('%Y-%m-%d'),
    "local_repo_path": "local_path_if_you_have"
}

response = requests.post(url, json=data)
print(response.json())