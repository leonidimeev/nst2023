import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


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


def turbo(question):
    return openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": f"{question}"}])