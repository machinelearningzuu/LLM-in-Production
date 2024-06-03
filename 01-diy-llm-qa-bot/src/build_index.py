import qdrant_client
import os, nest_asyncio, tiktoken
from llama_index.core import Settings
from IPython.display import Markdown, display
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core import StorageContext, get_response_synthesizer, VectorStoreIndex, SimpleDirectoryReader
from util.llm_services import *
nest_asyncio.apply() 


def load_documents():
    documents = SimpleDirectoryReader(path_config.kb_documents_dir).load_data()
    nodes = Settings.node_parser.get_nodes_from_documents(documents)
    print(f"Total nodes: {len(nodes)}")

    return nodes

def save_and_load_index(
                        nodes,      
                        collection_name = "banks"
                        ):
    client = qdrant_client.QdrantClient(
                                    path=path_config.vector_store_path
                                    )
    vector_store = QdrantVectorStore(
                                    client=client, 
                                    collection_name=collection_name
                                    )
    if not os.path.exists(f"{path_config.vector_store_path}/collection/{collection_name}"):
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
                                        node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
                                    )
    return query_engine

def index_pipeline():
    nodes = load_documents()
    query_engine = save_and_load_index(nodes)
    return query_engine