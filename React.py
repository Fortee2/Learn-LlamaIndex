from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama
from llama_index.llms.bedrock import Bedrock
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.llms import ChatMessage
from llama_index.core.tools import BaseTool, FunctionTool
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.core.tools import RetrieverTool
import os
import logging
import sys
import llama_index
from llama_index.core.memory import ChatMemoryBuffer

llama_index.core.set_global_handler("simple")

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url="http://localhost:11434"
)

Settings.chunk_size = 512
Settings.chunk_overlap = 50

""" profile_name = "LB-Integration"
llm = Bedrock(
    model="meta.llama3-70b-instruct-v1:0", 
    profile_name=profile_name, 
    context_size=2048,
    temperature=0.5,
    additional_kwargs={'top_p': 0.9,},
) """

memory = ChatMemoryBuffer.from_defaults(token_limit=3500)

""" llm = Ollama(model="llama3", temperature=0.5, timeout=35000, top_p=0.9)
llm.base_url = 'http://192.168.1.94:11434' """

llm = Ollama(model="llama3", temperature=0.5, timeout=35000, top_p=0.9)
llm.base_url = 'http://localhost:11434'

codeExt = ["py", "java", "js", "ts", "cpp", "c", "h", "hpp", "cs", "php", "go", "rs", "rb", "swift", "kt", "m", "sh", "bash", "ps1", "psm1", "pl", "perl", "lua", "r", "scala", "groovy", "dart", "swift", "ts", "tsx", "jsx", "vue", "svelte", "clj", "cljs", "cljc", "edn"]

def checkType(fileName: str): 
    fileExt = fileName.split(".")[-1]
    if fileExt in codeExt:
        return "code"
    else:
        return "text"
    
def getMetadata(file_path: str):
    print(file_path)
    file_name_only = os.path.basename(file_path)
    return {"type": checkType(file_path), "file_path": file_path, "file_name": file_name_only}

#Load the index
PERSIST_DIR = "./code_storage"
if(not os.path.exists(PERSIST_DIR)):
    documents = SimpleDirectoryReader(input_dir="./code", recursive=True, filename_as_id=True).load_data()
    index = VectorStoreIndex.from_documents(documents,)    
    # Save the index to disk
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    #load the index from disk
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)

def multiply(a: int, b: int) -> int:
    """Multiply two integers and returns the result integer"""
    return a * b


multiply_tool = FunctionTool.from_defaults(fn=multiply)

def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b


add_tool = FunctionTool.from_defaults(fn=add)

codebase_retriever = index.as_retriever(similarity_top_k=5, verbose=True)
codebase_tool =RetrieverTool.from_defaults(
    retriever=codebase_retriever,
    description = "Useful for retrieving files from the codebase for the chrome extension.")

nodes = codebase_retriever.retrieve("what does background.js do?")

print(nodes)

agent =ReActAgent.from_tools([multiply_tool, add_tool, codebase_tool], llm=llm, verbose=True, chat_history=memory.get_all())

while True:
    chat_input = input("You: ")
    response = agent.chat(chat_input)
    print(response)
    if chat_input.lower() == "exit":
        break 