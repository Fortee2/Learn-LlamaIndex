from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.node_parser import SimpleFileNodeParser
from llama_index.core.vector_stores.simple import SimpleVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
import os

Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url="http://localhost:11434"
)

llm = Ollama(model="llama3", request_timeout=1000, temperature=0.5, top_p=0.9)
llm.base_url = 'http://localhost:11434'

Settings.llm = llm  

reader = SimpleDirectoryReader(input_dir= "/Users/randycostner/source/lender-reporting/packages", recursive=True, required_exts=[".ts"], filename_as_id=True)
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

index = VectorStoreIndex(md_chunked_nodes);

""" node_parser = SentenceSplitter(chunk_size=512)
nodes = node_parser.get_nodes_from_documents(reader.load_data())

embed_model = OllamaEmbedding( model_name="nomic-embed-text", base_url="http://localhost:11434")
for node in nodes:
    node_embedding = embed_model.get_text_embedding(
        node.get_content(metadata_mode="all")
    )
    node.embedding = node_embedding
    
simple_vector_store.add(nodes)

print(f"Added {len(nodes)} nodes to the vector store") """

#index = VectorStoreIndex.from_vector_store(simple_vector_store)

""" PERSIST_DIR = "./storage"
PERSIST_VS_DIR = "./storage/vector_store"
if(not os.path.exists(PERSIST_DIR)):
    simple_vector_store.persist(PERSIST_VS_DIR)
    index = VectorStoreIndex.from_vector_store(simple_vector_store)
    # Save the index to disk
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    #load the index from disk
    simple_vector_store.load(PERSIST_VS_DIR)
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context) """
    
query_engine = index.as_query_engine()
response = query_engine.query("What files have a reference to the ICompanyConfiguration interface?")
print(response)