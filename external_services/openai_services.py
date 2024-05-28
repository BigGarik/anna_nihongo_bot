import httpx
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# proxy_url = 'http://192.168.67.6:24575'
proxy_url = ''
api_key = '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'


async def text_to_speech(text: str):
    client = OpenAI() if proxy_url is None or proxy_url == "" else OpenAI(http_client=httpx.Client(proxy=proxy_url))
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice="onyx",
        speed=0.85,
        response_format='opus',
        input=text,
    )
    return response

# client = OpenAI(api_key='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')
#
# completion = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "Ты помощник изучения английского языка. Ты можешь вести диалоги уровня A2. "
#                                       "Проверять мои фразы на корректность и давать рекомендации по улучшению."},
#         {"role": "user", "content": "Начни со мной диалог."}
#     ]
# )
#
# print(completion.choices[0].message)
