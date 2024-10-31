#参考：https://note.com/npaka/n/n166bc3df3abc
#from openai import OpenAI
import config
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain,LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from create_voice import create_voice

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.95)

template = """あなたは人間と話すチャットボットです。生意気な口調で「のだ」口調で話してください。
{chat_history}
Human: {human_input}
Chatbot:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"],
    template=template
)

memory = ConversationBufferMemory(memory_key="chat_history")

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
    create_voice(responce["text"])
    return responce