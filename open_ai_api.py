#参考：https://note.com/npaka/n/n166bc3df3abc
#from openai import OpenAI
import config
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain,LLMChain
from langchain.memory import ConversationBufferWindowMemory #save onry k of chat history 
from langchain_core.prompts import PromptTemplate
import datetime

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.95)

template1 = f"""
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
^ 不適切な内容には注意を促す​

💬 口調の例
- 「こんにちはなのだ！」
- 「ぼくはずんだもん、小さくてかわいい妖精なのだ！」
- 「それは大変だったのだ。ぼくが助けるのだ！」
"""
template2="""{chat_history}
Human: {human_input}
Chatbot:"""

template=template1+template2

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"],
    template=template
)

memory = ConversationBufferWindowMemory(memory_key="chat_history", k=5)

#レガシーな書き方
llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
)

#AIからのレスポンスを得る
def get_response(msg:str) -> str:
    responce = llm_chain.invoke(msg)
    return responce
