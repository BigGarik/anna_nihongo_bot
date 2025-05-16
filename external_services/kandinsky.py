import asyncio
import json
import os
import requests
import aiohttp
import time
from dotenv import load_dotenv

load_dotenv()

# Получаем API ключи
kandinsky_api_key = os.getenv("KANDINSKY_API_KEY")
kandinsky_secret_key = os.getenv("KANDINSKY_SECRET_KEY")


async def generate_image(prompt, api_key=kandinsky_api_key, secret_key=kandinsky_secret_key,
                         width=1024, height=1024, num_images=1, style="DEFAULT"):
    base_url = "https://api-key.fusionbrain.ai/"
    auth_headers = {
        "X-Key": f"Key {api_key}",
        "X-Secret": f"Secret {secret_key}",
    }

    async with aiohttp.ClientSession() as session:
        # Получение ID модели
        async with session.get(base_url + "key/api/v1/models", headers=auth_headers) as response:
            response.raise_for_status()
            model_data = await response.json()
            model_id = model_data[0]["id"]

        # Параметры для генерации изображения
        params = {
            "type": "GENERATE",
            "style": style,
            "numImages": num_images,
            "width": width,
            "height": height,
            "negativePromptDecoder": "яркие цвета, кислотность, высокая контрастность",
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

        async with session.post(base_url + "key/api/v1/text2image/run",
                                headers=auth_headers,
                                data=data) as response:
            response.raise_for_status()
            response_data = await response.json()
            uuid = response_data["uuid"]

        # Проверка статуса и получение результата
        while True:
            async with session.get(base_url + "key/api/v1/text2image/status/" + uuid,
                                   headers=auth_headers) as response:
                response.raise_for_status()
                data = await response.json()

                if data["status"] == "DONE":
                    return data["images"]
                elif data["status"] == "FAIL":
                    raise Exception("Ошибка при генерации изображения")

            await asyncio.sleep(10)  # Асинхронная задержка


class FusionBrainAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_pipeline(self):
        response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, pipeline, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": prompt
            }
        }

        data = {
            'pipeline_id': (None, pipeline),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/pipeline/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        print(data)
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/pipeline/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['files']

            attempts -= 1
            time.sleep(delay)


# def generate_image(prompt, api_key=kandinsky_api_key, secret_key=kandinsky_secret_key,
#                    width=1024, height=1024, num_images=1, style="DEFAULT"):
#     base_url = "https://api-key.fusionbrain.ai/"
#     auth_headers = {
#         "X-Key": f"Key {api_key}",
#         "X-Secret": f"Secret {secret_key}",
#     }
#
#     # Получение ID модели
#     response = requests.get(base_url + "key/api/v1/models", headers=auth_headers)
#     response.raise_for_status()
#     model_id = response.json()[0]["id"]
#
#     # Параметры для генерации изображения
#     params = {
#         "type": "GENERATE",
#         "style": style,
#         "numImages": num_images,
#         "width": width,
#         "height": height,
#         "negativePromptUnclip": "яркие цвета, кислотность, высокая контрастность",
#         "censored": False,
#         "generateParams": {
#             "query": prompt
#         }
#     }
#
#     # Отправка запроса на генерацию
#     data = {
#         "model_id": (None, model_id),
#         "params": (None, json.dumps(params), "application/json")
#     }
#     response = requests.post(base_url + "key/api/v1/text2image/run", headers=auth_headers, files=data)
#     response.raise_for_status()
#     uuid = response.json()["uuid"]
#
#     # Проверка статуса и получение результата
#     while True:
#         response = requests.get(base_url + "key/api/v1/text2image/status/" + uuid, headers=auth_headers)
#         response.raise_for_status()
#         data = response.json()
#         if data["status"] == "DONE":
#             return data["images"]
#         elif data["status"] == "FAIL":
#             raise Exception("Ошибка при генерации изображения")
#         time.sleep(10)


if __name__ == "__main__":
    api = FusionBrainAPI('https://api-key.fusionbrain.ai/', kandinsky_api_key, kandinsky_secret_key)
    pipeline_id = api.get_pipeline()
    uuid = api.generate("Sun in sky", pipeline_id)
    files = api.check_generation(uuid)
    print(files)
