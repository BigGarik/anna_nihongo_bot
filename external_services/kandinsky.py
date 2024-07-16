import os

import requests
import json
import time

from dotenv import load_dotenv

load_dotenv()

# Получаем API ключи
kandinsky_api_key = os.getenv("KANDINSKY_API_KEY")
kandinsky_secret_key = os.getenv("KANDINSKY_SECRET_KEY")


# class Text2ImageAPI:
#
#     def __init__(self, api_key, secret_key):
#         self.URL = "https://api-key.fusionbrain.ai/"
#         self.AUTH_HEADERS = {
#             "X-Key": f"Key {api_key}",
#             "X-Secret": f"Secret {secret_key}",
#         }
#
#     def get_model(self):
#         response = requests.get(self.URL + "key/api/v1/models", headers=self.AUTH_HEADERS)
#         data = response.json()
#         print(data)
#         return data[0]["id"]
#
#     def generate(self, prompt, model, images=1, width=1024, height=1024):
#         params = {
#             "type": "GENERATE",
#             "numImages": images,
#             "width": width,
#             "height": height,
#             "generateParams": {
#                 "query": f"{prompt}"
#             }
#         }
#
#         data = {
#             "model_id": (None, model),
#             "params": (None, json.dumps(params), "application/json")
#         }
#         response = requests.post(self.URL + "key/api/v1/text2image/run", headers=self.AUTH_HEADERS, files=data)
#         data = response.json()
#         return data["uuid"]
#
#     def check_generation(self, request_id, attempts=10, delay=10):
#         while attempts > 0:
#             response = requests.get(self.URL + "key/api/v1/text2image/status/" + request_id, headers=self.AUTH_HEADERS)
#             data = response.json()
#             if data["status"] == "DONE":
#                 return data["images"]
#
#             attempts -= 1
#             time.sleep(delay)


def generate_image(prompt, api_key=kandinsky_api_key, secret_key=kandinsky_secret_key,
                   width=1024, height=1024, num_images=1, style="DEFAULT"):
    base_url = "https://api-key.fusionbrain.ai/"
    auth_headers = {
        "X-Key": f"Key {api_key}",
        "X-Secret": f"Secret {secret_key}",
    }

    # Получение ID модели
    response = requests.get(base_url + "key/api/v1/models", headers=auth_headers)
    response.raise_for_status()
    model_id = response.json()[0]["id"]

    # Параметры для генерации изображения
    params = {
        "type": "GENERATE",
        "style": style,
        "numImages": num_images,
        "width": width,
        "height": height,
        "negativePromptUnclip": "яркие цвета, кислотность, высокая контрастность",
        "censored": False,
        "generateParams": {
            "query": prompt
        }
    }

    # Отправка запроса на генерацию
    data = {
        "model_id": (None, model_id),
        "params": (None, json.dumps(params), "application/json")
    }
    response = requests.post(base_url + "key/api/v1/text2image/run", headers=auth_headers, files=data)
    response.raise_for_status()
    uuid = response.json()["uuid"]

    # Проверка статуса и получение результата
    while True:
        response = requests.get(base_url + "key/api/v1/text2image/status/" + uuid, headers=auth_headers)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "DONE":
            return data["images"]
        elif data["status"] == "FAIL":
            raise Exception("Ошибка при генерации изображения")
        time.sleep(10)


if __name__ == "__main__":
    # api = Text2ImageAPI(kandinsky_api_key, kandinsky_secret_key)
    # model_id = api.get_model()
    # uuid = api.generate("Sun in sky", model_id)
    # images = api.check_generation(uuid)
    # print(images)
    # print(kandinsky_api_key, kandinsky_secret_key)
    prompt = "Красивый закат над морем"
    images = generate_image(prompt, style="ANIME")
    # print(images)
