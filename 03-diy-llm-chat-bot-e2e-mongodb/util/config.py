import yaml, os

with open("secrets.yaml", "r") as file:
    secrets = yaml.safe_load(file)

os.environ["LLAMA_CLOUD_API_KEY"] = secrets["LLAMA_CLOUD_API_KEY"]
os.environ["VOYAGE_API_KEY"] = secrets["VOYAGE_AI_API_KEY"]
os.environ["OPENAI_API_KEY"] = secrets["OPENAI_API_KEY"]
os.environ["GROQ_API_KEY"] = secrets["GROQ_API_KEY"]
os.environ["MONGO_URI"] = secrets["MONGO_URL"]

class DBconfig:
    '''Configuration class for the database'''
    mongo_url = secrets['MONGO_URL']
    mongo_db = "03-diy-llm-chat-bot-e2e-mongodb"
    chat_collection = "chat_history"
    user_collection = "user_details"

class PATHconfig:
    '''Configuration Paths for the project'''
    vector_store_path = 'db/qabot_index'
    eval_dataset_path = 'db/eval/eval_data.csv'
    eval_results_path = 'db/eval/eval_results.csv'
    kb_documents_dir = 'db/kb/'

class DATAconfig:
    '''Configuration class for the data'''
    api_key = os.environ['LLAMA_CLOUD_API_KEY']
    gpt4o_mode = False
    chunk_size = 1000

class LLMconfig:
    '''Configuration class for the LLM model'''
    temperature = 0.15
    model_type = "groq"
    model_name = {
                "openai": "gpt-3.5-turbo",
                "groq": "mixtral-8x7b-32768",
                }
    api_keys = {
                "openai": os.environ["OPENAI_API_KEY"],
                "groq": os.environ["GROQ_API_KEY"],
                }
    human_message_template = """Given the context: {context}. Answer the question {question}."""
    system_message_template = """You are a helpful assistant built by Databricks, you are good at helping to answer a question based on the context provided, the context is a document. If the context does not provide enough relevant information to determine the answer, just say I don't know. If the context is irrelevant to the question, just say I don't know. If you did not find a good answer from the context, just say I don't know. If the query doesn't form a complete question, just say I don't know. If there is a good answer from the context, try to summarize the context to answer the question."""

class EMBEDconfig:
    '''Configuration class for the embedding model'''
    model_type = "hf"
    model_name = {
                "openai": "text-embedding-3-small",
                "voyage": "voyage-large-2-instruct",
                "hf": "BAAI/bge-small-en-v1.5",
                }
    api_keys = {
                "openai": os.environ["OPENAI_API_KEY"],
                "voyage": os.environ["VOYAGE_API_KEY"],
                }