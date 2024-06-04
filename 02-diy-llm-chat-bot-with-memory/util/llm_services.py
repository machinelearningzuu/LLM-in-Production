import voyageai, tiktoken
from pymongo import MongoClient
from llama_parse import LlamaParse
from llama_index.core import Settings
from llama_index.llms.groq import Groq
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.voyageai import VoyageEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from util.config import PATHconfig, LLMconfig, EMBEDconfig, DATAconfig, DBconfig

db_config = DBconfig()
path_config = PATHconfig()
embed_config = EMBEDconfig()
data_config = DATAconfig()
llm_config = LLMconfig()

if llm_config.model_type == "openai":
    print("Using OpenAI LLM ....")
    llm = OpenAI(
                api_key=llm_config.api_keys["openai"],
                temperature=llm_config.temperature,
                model=llm_config.model_name["openai"],
                )
    
elif llm_config.model_type == "groq":
    print("Using Groq LLM ....")
    llm = Groq(
                api_key=llm_config.api_keys["groq"],
                model=llm_config.model_name["groq"],
                )
    
else:
    raise ValueError(f"Model type not supported : {llm_config.model_type}")

if embed_config.model_type == "openai":
    print("Using OpenAI Embedding ....")
    embed_model = OpenAIEmbedding(
                                api_key=embed_config.api_keys["openai"],
                                model_name=embed_config.model_name["openai"]
                                )
    
elif embed_config.model_type == "voyage":
    print("Using Voyage AI Embedding ....")
    voyageai.api_key = embed_config.api_keys["voyage"]
    embed_model = VoyageEmbedding(
                                api_key=embed_config.api_keys["voyage"],
                                model_name=embed_config.model_name["voyage"]
                                )
    
elif embed_config.model_type == "hf":
    print("Using HuggingFace Embedding ....")
    embed_model = HuggingFaceEmbedding(
                                model_name=embed_config.model_name["hf"],
                                # model_kwargs={"device": "mps"}
                                )
    
else:
    raise ValueError(f"Model type not supported : {embed_config.model_type}")

document_parser = LlamaParse(
                            result_type="markdown",
                            api_key=data_config.api_key,
                            gpt4o_mode=data_config.gpt4o_mode
                            )

tiktoken_encoder = tiktoken.get_encoding("cl100k_base")

Settings.chunk_size = data_config.chunk_size
Settings.embed_model = embed_model
Settings.llm = llm

mongo_client = MongoClient(db_config.mongo_url)
db = mongo_client[db_config.mongo_db]