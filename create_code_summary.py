from llama_index.core import SimpleDirectoryReader
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
import sys

from pydantic import BaseModel, Field
from typing import List

from llama_index.program.lmformatenforcer import (
    LMFormatEnforcerPydanticProgram,
)

class ClassDetails(BaseModel):
    class_name: str
    constructor_parameters: List[str]
    methods: List[str]

class CodeSummary(BaseModel):
    filename: str
    classes: List[ClassDetails]


reader = SimpleDirectoryReader(input_dir= "/Users/randycostner/source/User-Security", recursive=True, required_exts=[".cs"], filename_as_id=True)

llm = Ollama(model="llama3", request_timeout=1000, temperature=0.1, top_p=0.9)
llm.base_url = 'http://localhost:11434'

prompt = ("Your response should be according to the following json schema: \n"
"{json_schema}\n" 
"You are a .net software engineer. Your task is to create documentation for the codebase in JSON format. "
" For each piece of code block you need to extract the classes declared in the file, parameters for the constructor of each class, "
" and the method signatures in the class.  The code block is: {code_block}\n")


program = LMFormatEnforcerPydanticProgram(
    output_cls=CodeSummary,
    llm=llm,
    verbose=True,
    prompt_template_str=prompt
)

for doc in reader.load_data():
    response = program(code_block=doc.text)
    print(response)
