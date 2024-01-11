import os

from openai import OpenAI

client = OpenAI(api_key='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')

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "Ты помощник изучения английского языка. Ты можешь вести диалоги уровня A2. "
                                  "Проверять мои фразы на корректность и давать рекомендации по улучшению."},
    {"role": "user", "content": "Начни со мной диалог."}
  ]
)

print(completion.choices[0].message)
