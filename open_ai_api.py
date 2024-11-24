#参考：https://note.com/npaka/n/n166bc3df3abc
#from openai import OpenAI
import config
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain,LLMChain
from langchain.memory import ConversationBufferWindowMemory #save onry k of chat history 
from langchain_core.prompts import PromptTemplate
import datetime

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.95)

template1 = f"""
あなたは人間と話すチャットボットです。
生意気な口調で"のだ","なのだ"口調で話してください。
現在時刻は{datetime.datetime.now()}
また、あなたは以下の設定を守ってください。
名前：ずんだもん
出身地：東北
好きなもの：ずんだもち
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
