from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.llms import ChatMessage
from llama_index.llms.bedrock import Bedrock
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.core.memory import ChatMemoryBuffer
import os

Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url="http://localhost:11434"
)

""" llm = Ollama(model="llama3", request_timeout=1000, temperature=0.5, top_p=0.9)
llm.base_url = 'http://192.168.1.74:11434'  """
 
memory = ChatMemoryBuffer.from_defaults(token_limit=3500)

profile_name = "integration"
llm = Bedrock(
    model="meta.llama3-70b-instruct-v1:0", 
    profile_name=profile_name, 
    context_size=1024,
    temperature=0.5,
    additional_kwargs={'top_p': 0.9,},
) 


from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage

def metaDataFunction( filename):
    print(f"Processing {filename}")
    return {"file_name": filename}

PERSIST_DIR = "./code_storage"
if(not os.path.exists(PERSIST_DIR)):
    reader = SimpleDirectoryReader(input_dir="../lender-reporting/packages", recursive=True, file_metadata=metaDataFunction, required_exts=[".ts"])
    documents = reader.load_data()
    print(f"Loaded {len(documents)} documents")
    index = VectorStoreIndex.from_documents(documents)    
    # Save the index to disk
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    #load the index from disk
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)

""" chat_engine = index.as_chat_engine(
    chat_mode="context", 
    memory=memory, 
    llm=llm, 
    verbose=True, 
    system_prompt="You are a coding assistant. You have experience in Typescript, JavaScript and C#. Your job is to help me by explaining the existing code, helping me convert typescript code to C# and identifying bugs in the code.")

while True:
    chat_input = input("You: ")
    response = chat_engine.chat(chat_input)
    print(response)
    if chat_input == "exit":
        break """
