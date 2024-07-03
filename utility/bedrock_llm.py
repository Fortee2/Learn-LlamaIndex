from llama_index.llms.bedrock import Bedrock

def create_bedrock_llm(aws_profile_name: str = "integration", model: str = "meta.llama3-70b-instruct-v1:0", context_size: int = 1024, temperature: float = 0.5, top_p: float = 0.9)-> Bedrock:
    """Connect to a LLM model using Bedrock."""
    
    llm = Bedrock(
        model="meta.llama3-70b-instruct-v1:0", 
        profile_name=aws_profile_name, 
        context_size=context_size,
        temperature=temperature,
        additional_kwargs={'top_p': top_p,},
    ) 
    return llm