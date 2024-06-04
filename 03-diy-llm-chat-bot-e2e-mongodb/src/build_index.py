import os, nest_asyncio, tiktoken
from llama_index.core import Settings
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core import StorageContext, get_response_synthesizer, VectorStoreIndex, SimpleDirectoryReader, PromptTemplate
from util.llm_services import *
nest_asyncio.apply() 


def load_documents():
    documents = SimpleDirectoryReader(path_config.kb_documents_dir).load_data()
    nodes = Settings.node_parser.get_nodes_from_documents(documents)
    print(f"Total nodes: {len(nodes)}")

    return nodes

def save_and_load_index(
                        nodes,      
                        collection_name = "embeddings_bank"
                        ):
    vector_store = MongoDBAtlasVectorSearch(
                                        db_name=db_config.mongo_db,
                                        client=mongo_client, 
                                        collection_name=collection_name
                                        )
    if not collection_name in mongo_client[db_config.mongo_db].list_collection_names():
        print("Building Finance Index ...")
        storage_context = StorageContext.from_defaults(
                                                        vector_store=vector_store,
                                                        )
        index = VectorStoreIndex(
                                nodes, 
                                storage_context=storage_context
                                )
        
    else:
        print("Loading Finance Index ...")
        storage_context = StorageContext.from_defaults(
                                                        vector_store=vector_store
                                                        )
        index = VectorStoreIndex.from_vector_store(
                                                    vector_store, 
                                                    storage_context=storage_context
                                                    )

    retriever = VectorIndexRetriever(
                                    index=index,
                                    similarity_top_k=3,
                                    )

    response_synthesizer = get_response_synthesizer()
    query_engine = RetrieverQueryEngine(
                                        retriever=retriever,
                                        response_synthesizer=response_synthesizer,
                                        node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.0)],
                                        )
    
    text_chat_template = """
    Context Information is below.
    ---------------------
    {context_str}
    ---------------------

    Chat History and Query is below.
    ---------------------
    {query_str}
    ---------------------

    Given the Context Information, Chat History and not prior knowledge, answer the query.

    ASSISTANT: 
    """

    text_chat_pmt_template = PromptTemplate(text_chat_template)   

    query_engine.update_prompts(
                                {"response_synthesizer:text_qa_template": text_chat_pmt_template}
                                )
    return query_engine

def index_pipeline():
    nodes = load_documents()
    query_engine = save_and_load_index(nodes)
    return query_engine