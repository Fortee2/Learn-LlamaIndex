import os
import re
import logging
import sys
from llama_index.core import SimpleDirectoryReader
from llama_index.llms.ollama import Ollama
from llama_index.core.settings import Settings

# Set up logging
#llama_index.core.set_global_handler("simple")
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# Configure settings
Settings.chunk_size = 512
Settings.chunk_overlap = 50

# Initialize Bedrock LLM
""" profile_name = "default"
llm = Bedrock(
    model="meta.llama3-70b-instruct-v1:0", 
    profile_name=profile_name, 
    context_size=2048,
) """

llm = Ollama(model="llama3", request_timeout=1000)
llm.base_url = 'http://localhost:11434'

def parse_cs_file(file_content):
    classes = re.findall(r'class\s+(\w+)', file_content)
    interfaces = re.findall(r'interface\s+(\w+)', file_content)
    return classes, interfaces

def generate_llm_description(file_content, first_file):
    response = llm.complete(
        prompt=f"""Using the Mermaid language generate a uml diagram that correctly represents this C# code.  
            Return only the mermaid diagram. Do not provide anything but the mermaid markup.\n\n
            {file_content} \n\n
            Here is an example of how the output should be formatted: \n\n
                class BankAccount \n
                BankAccount : +String owner \n
                BankAccount : +Bigdecimal balance \n
                BankAccount : +deposit(amount) \n
                BankAccount : +withdrawal(amount) \n
            """
    )
    
    return cleanup_mermaid_description(response.text)
 
def cleanup_mermaid_description(mermaid_description):
    modified_response = ""
    
    try:
        index = mermaid_description.index("```mermaid")
        modified_response = mermaid_description[index + 10:]
    except ValueError:
        modified_response = mermaid_description
        
    modified_response = modified_response.replace("```", "")
    
    return modified_response
        
def verify_llm_description(mermaid_description):
    response = llm.complete(
        prompt=f"""Verify that the Mermaid diagram is correct.  
        Return only the word \"correct\" if the diagram is correct.  
        Otherwise, return the word \"incorrect\". 
        The diagram is as follows: \n\n
        {mermaid_description} \n\n"""
    )
    
    return response.text

def generate_mermaid_description(file_content, first_file):
    # Generate LLM description
    llm_description = generate_llm_description(file_content, first_file)
    # Generate Mermaid description
    return llm_description

def process_files(input_dir):
    reader = SimpleDirectoryReader(input_dir=input_dir, recursive=True, filename_as_id=True)
    documents = reader.load_data()
    first_file = True
    final_output = ""
    
    for doc in documents:
        metadata = doc.metadata
        if metadata['file_name'].endswith('.cs'):
            with open(metadata['file_path'], 'r') as file:
                file_content = file.read()
                classes, interfaces = parse_cs_file(file_content)
                if classes or interfaces:
                    full_description = generate_mermaid_description(file_content, first_file)
                    first_file = False
                    print(f"File: {metadata['file_name']}")
                    print(full_description)
                    final_output += full_description
                    print(verify_llm_description(full_description))
                    
    # Create an output filename
    output_filepath = os.path.join("./user_security_mermaid.txt")  # Ensure "output_directory" exists

    # Write the full description to the file
    with open(output_filepath, 'a') as output_file:
        output_file.write(final_output)

if __name__ == '__main__':
    input_dir = "../User-Security"
    process_files(input_dir)