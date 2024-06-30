from llama_index.llms.ollama import Ollama
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from pydantic import BaseModel, Field
from pydantic.json import pydantic_encoder
import os

def ask_question ( question: str ) -> str:
    """Useful for getting more information from the user."""
    print(question)
    return input("You: ")



question_tool = FunctionTool.from_defaults(fn=ask_question)
#statement_tool = FunctionTool.from_defaults(fn=make_a_statement)

llm = Ollama(model="llama3", request_timeout=2000, temperature=0.3, top_p=0.9)
llm.base_url = 'http://192.168.1.94:11434'

memory = ChatMemoryBuffer.from_defaults(token_limit=3500)  

# Modify the system prompt to ask for reasoning steps
system_prompt = ("You are a coding assistant with a background in financial services. Your job is to help me design a system that will allow me develop and back test stock trading strategies.  If at any point you need more information, feel free to ask for it.  If you don't know the answer, you can say 'I don't know' and I will provide more information. If you can answer without using a tool, you can say 'I can answer that' and provide the answer.")

    
agent =ReActAgent.from_tools([question_tool], llm=llm, verbose=True, chat_history=memory.get_all())

while True:
    chat_input = input("You: ")
    response = agent.chat(chat_input)
    print(response)
    if chat_input.lower() == "exit":
        break 

chats = memory.get_all()

print(chats)