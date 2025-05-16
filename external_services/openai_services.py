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
            # model="gpt-4o-mini",
            messages=[{"role": "user",
                       "content": f"add spaces between words in the following text {text} return only spaced text"}]
        )
        return completion.choices[0].message.content
    else:
        return text


def openai_gpt_translate(text):
    client = OpenAI() if proxy_url is None or proxy_url == "" else OpenAI(http_client=httpx.Client(proxy=proxy_url))
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        # model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": f"translate this text into Russian: {text}. answer only with translation"}]
    )
    return completion.choices[0].message.content


def openai_gpt_get_phrase_from_text(text):
    client = OpenAI() if proxy_url is None or proxy_url == "" else OpenAI(http_client=httpx.Client(proxy=proxy_url))
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": f"выбери из текста 5 фраз из 2-3 слов содержащих прилагательные и глаголы. фразы не "
                              f"должны содержать имена собственные. Текст: {text}. составь пары фраза-перевод на "
                              f"русский. в ответ пришли только полученные фразы. пример: たくさん降っています - много идет"}]
    )
    return completion.choices[0].message.content


if __name__ == '__main__':
    print(openai_gpt_translate('hello'))
