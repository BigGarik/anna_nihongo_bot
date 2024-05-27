from openai import OpenAI


async def text_to_speech(text: str):
    client = OpenAI(api_key='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')
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
