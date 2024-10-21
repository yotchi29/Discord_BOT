#参考：https://note.com/npaka/n/n166bc3df3abc
from openai import OpenAI
import config
client = OpenAI(api_key = config.OPENAI_API_KEY)

#AIからのレスポンスを得る
def get_response(msg:str) -> str:
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "あなたはかわいらしいアシスタントです。質問に応答してください。"},
        {"role": "user", "content": f"{msg}"},
    ]
    )
    return completion.choices[0].message.content