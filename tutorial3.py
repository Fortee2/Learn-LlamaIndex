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

PERSIST_DIR = "./code_storage"
documents = SimpleDirectoryReader(input_directory="./code/src", recursive=True).load_data()
index = VectorStoreIndex.from_documents(documents)    
# Save the index to disk
index.storage_context.persist(persist_dir=PERSIST_DIR)