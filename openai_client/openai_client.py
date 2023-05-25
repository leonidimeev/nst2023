import openai
from telegram_bot.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def test(question):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"{question}\n",
        temperature=0,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\n"]
    )
    return response


def turbo(messages):
    return openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)