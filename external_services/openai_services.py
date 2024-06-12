import os

import httpx
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
location = os.getenv('LOCATION')


# proxy_url = 'http://192.168.67.6:24575'
proxy_url = ''
# api_key = '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'


async def openai_text_to_speech(text: str):
    client = OpenAI() if proxy_url is None or proxy_url == "" else OpenAI(http_client=httpx.Client(proxy=proxy_url))
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice="nova",
        speed=0.85,
        response_format='opus',
        input=text,
    )
    return response


def openai_gpt_add_space(text):
    if location == 'ja-JP':
        client = OpenAI() if proxy_url is None or proxy_url == "" else OpenAI(http_client=httpx.Client(proxy=proxy_url))
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user",
                       "content": f"add spaces between words in the following text {text} return only spaced text"}]
        )
        return completion.choices[0].message.content
    else:
        return text


def openai_gpt_translate(text):
    client = OpenAI() if proxy_url is None or proxy_url == "" else OpenAI(http_client=httpx.Client(proxy=proxy_url))
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": f"translate this text into Russian: {text}. answer only with translation"}]
    )
    return completion.choices[0].message.content
