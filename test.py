from yandex_cloud_ml_sdk import YCloudML
from dotenv import load_dotenv
import os

# Загрузить переменные из .env
load_dotenv()

folder_id = os.getenv("FOLDER_ID")
access_token = os.getenv("ACCESS_KEY")

sdk = YCloudML(
    folder_id=folder_id,
    auth=access_token
)

with open("example.txt", 'r', encoding="utf_8_sig") as f: 
    example_text = f.read()

model = sdk.models.completions("yandexgpt", model_version="rc")
model = model.configure(temperature=0.3)
result = model.run(
    [
        {"role": "system", "text": "Code Review"},
        {
            "role": "user",
            "text": example_text,
        },
    ]
)

for alternative in result:
    print(alternative.text)
