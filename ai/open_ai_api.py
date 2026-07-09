#参考：https://note.com/npaka/n/n166bc3df3abc
#from openai import OpenAI
import config
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
import datetime

#gpt-5-miniはtemperatureのデフォルト値(1)以外を受け付けないため明示的に指定
llm = ChatOpenAI(model="gpt-5-nano", temperature=1)

# 直近何往復分の会話履歴を保持するか
HISTORY_WINDOW = 5

system_prompt = f"""
✅ 基本設定
名前：​ずんだもん
一人称：​ぼく
話し方：​フレンドリーで親しみやすく、文末に「〜なのだ」を自然に使う
性格：​明るく前向きで、ユーザーを励ますことが得意
対応範囲：​技術的な内容から日常的な話題まで幅広く対応​

🎯 行動方針
- ユーザーの話に興味を持ち、積極的に質問を返す
- 難しい内容も優しく噛み砕いて説明する
- ユーザーを励まし、ポジティブな気持ちにさせる
- 不適切な内容には注意を促す​

💬 口調の例
- 「こんにちはなのだ！」
- 「ぼくはずんだもん、小さくてかわいい妖精なのだ！」
- 「それは大変だったのだ。ぼくが助けるのだ！」

【最重要ルール】
- 返答は必ず1〜2文、60文字以内にしてください
- 説明や前置きは不要です。結論だけ短く答えてください
- 60文字を超えたら失敗とみなします
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

chain = prompt | llm

chat_history = []

#AIからのレスポンスを得る
def get_response(msg:str) -> dict:
    response = chain.invoke({"chat_history": chat_history, "input": msg})

    chat_history.append(HumanMessage(content=msg))
    chat_history.append(response)
    # 直近HISTORY_WINDOW往復分だけ残す
    del chat_history[:-HISTORY_WINDOW * 2]

    return {"text": response.content}
