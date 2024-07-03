from llama_index.core import SimpleDirectoryReader
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings

reader = SimpleDirectoryReader(input_dir= "/Users/randycostner/source/User-Security", recursive=True, required_exts=[".cs"], filename_as_id=True)

llm = Ollama(model="llama3", request_timeout=1000, temperature=0.1, top_p=0.9)
llm.base_url = 'http://localhost:11434'

llm.system_prompt= "You are a .net software engineer. Your task is to create documentation for the codebase. For each file you need to extract the classes declared in the file, parameters for the constructor of each class, and the method signatures in the class."

for doc in reader.load_data():
    response = llm.complete(doc.text)
    print(response)
