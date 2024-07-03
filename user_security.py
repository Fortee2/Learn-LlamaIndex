from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.node_parser import SimpleFileNodeParser
from llama_index.core.vector_stores.simple import SimpleVectorStore
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from utility.bedrock_llm import create_bedrock_llm
import os

Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text", base_url="http://localhost:11434")

llm = Ollama(model="llama3", request_timeout=1000, temperature=0.1, top_p=0.9)
llm.base_url = 'http://localhost:11434'

memory = ChatMemoryBuffer.from_defaults(token_limit=3500)

PERSIST_DIR = "./us-storage"
if(not os.path.exists(PERSIST_DIR)):
    reader = SimpleDirectoryReader(input_dir= "/Users/randycostner/source/User-Security", recursive=True, required_exts=[".cs"], filename_as_id=True)
    simple_vector_store = SimpleVectorStore()

    pipeline = IngestionPipeline(
        documents=reader.load_data(),
        transformations=[
            SimpleFileNodeParser(),
            SentenceSplitter(chunk_size=200, chunk_overlap=20),
            OllamaEmbedding(model_name="nomic-embed-text", base_url="http://localhost:11434"),
        ],
        vector_store=simple_vector_store,
    )

    md_chunked_nodes = pipeline.run()

    index = VectorStoreIndex(md_chunked_nodes)
    # Save the index to disk
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    #load the index from disk
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context) 
    

chat_engine = index.as_chat_engine(
    chat_mode="context", 
    memory=memory, 
    llm=llm, 
    verbose=True, 
    system_prompt="You are a coding assistant. You have experience in C#. Your job is to help me by explaining the existing code and identifying bugs in the code. If you can't find a file, method or class do not make up code.  Ask for assistance.")

while True:
    chat_input = input("You: ")
    response = chat_engine.chat(chat_input)
    print(response)
    if chat_input == "exit":
        break
    
memory.to_json("chat_memory.json")