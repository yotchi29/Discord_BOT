#参考：https://note.com/npaka/n/n166bc3df3abc
#from openai import OpenAI
import config
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain import PromptTemplate,LLMChain

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.95)

template = """あなたは人間と話すチャットボットです。
{chat_history}
Human: {human_input}
Chatbot:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"],
    template=template
)

memory = ConversationBufferMemory(memory_key="chat_history")

llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
)

#AIからのレスポンスを得る
def get_response(msg:str) -> str:
    return llm_chain.run(msg)