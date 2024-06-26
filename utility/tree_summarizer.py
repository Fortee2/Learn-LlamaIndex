from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.ollama import Ollama
from llama_index.core.response_synthesizers import TreeSummarize
import os

llm = Ollama(model="llama3", request_timeout=1000, temperature=0.5, top_p=0.9)
llm.base_url = 'http://192.168.1.94:11434' 

reader = SimpleDirectoryReader(input_dir= "/Volumes/Seagate Portabl/Projects/ListFlow/chrome", recursive=True, filename_as_id=True)

docs = reader.load_data()

text = docs[2].to_json()

print(text)

from llama_index.core.response_synthesizers import TreeSummarize

summarizer = TreeSummarize(verbose=True, llm=llm)

response = summarizer.get_response("describe what this file does?", [text])

print(response)