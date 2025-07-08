import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

PAPERS_DIR = "papers"

class PDFIngestor:
    def __init__(self, papers_dir=PAPERS_DIR):
        self.papers_dir = papers_dir
        self.index = None
        self.query_engine = None

    def ingest(self):
        # Loads all PDFs in the directory
        print(f"Ingesting PDFs from {self.papers_dir}")
        documents = SimpleDirectoryReader(self.papers_dir).load_data()
        print(f"Loaded {len(documents)} document(s)")

        # Embed and index documents
        embed_model = OpenAIEmbedding()
        self.index = VectorStoreIndex.from_documents(
            documents,
            embed_model=embed_model
        )
        # Set up retriever & query engine for answering
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=3,
        )
        llm = OpenAI(model="gpt-3.5-turbo")
        self.query_engine = self.index.as_query_engine(llm=llm)

    def retrieve_chunks(self, question: str, top_k=3, min_score=0.8):
        if self.index is None:
            raise ValueError("Index not built. Run ingest() first.")
        retriever = self.index.as_retriever(similarity_top_k=top_k)
        nodes = retriever.retrieve(question)
        # Each node is a NodeWithScore object with .score and .get_content()
        # Score: higher is better, but may depend on backend (often 0–1)
        relevant = [(node.get_content(), getattr(node, "score", 1.0)) for node in nodes]
        # Only keep chunks above threshold
        return [content for content, score in relevant if score is not None and score >= min_score]

    def query(self, question: str):
        if self.query_engine is None:
            raise ValueError("Query engine not initialized. Run ingest() first.")
        response = self.query_engine.query(question)
        return str(response)  # LlamaIndex response object → string