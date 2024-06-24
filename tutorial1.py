import os
os.environ['OLLAMA_URI'] = 'http://192.168.1.94'
from llama_index.llms.ollama import Ollama

llm = Ollama(model="llama3", request_timeout=1000)
llm.base_url = 'http://192.168.1.94:11434'
#response = llm.complete("What is the capital of France?")
#print(response)

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import Settings

Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url="http://192.168.1.94:11434"
)

Settings.llm = llm

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage

PERSIST_DIR = "./storage"
if(not os.path.exists(PERSIST_DIR)):
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)    
    # Save the index to disk
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    #load the index from disk
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
    
query_engine = index.as_query_engine()
response = query_engine.query("Please summarize this transcript highlighting the key points.")
print(response)