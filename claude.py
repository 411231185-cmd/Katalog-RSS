#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from openai import OpenAI

client = OpenAI(
    api_key="sk-Z7gvO4ie8FifuotXJS4snlYvviayYUkm",
    base_url="https://api.proxyapi.ru/openai/v1"
)

print("GPT-4o mini готов. 'выход' для выхода.\n")
history = [
    {"role": "system", "content": "Ты помощник компании ТД РУССтанкоСбыт. Помогаешь с каталогом запчастей для токарных станков."}
]

while True:
    user_input = input("Ты: ").strip()
    if not user_input:
        continue
    if user_input.lower() in ("выход", "exit"):
        break
    history.append({"role": "user", "content": user_input})
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=history,
            max_tokens=1000
        )
        reply = r.choices[0].message.content
        model_used = r.model
        print(f"\n[{model_used}]: {reply}\n")
        history.append({"role": "assistant", "content": reply})
    except Exception as e:
        print(f"\nОшибка: {e}\n")