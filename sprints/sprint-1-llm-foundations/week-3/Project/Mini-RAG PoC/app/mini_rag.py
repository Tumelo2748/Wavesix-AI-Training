import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.indices.postprocessor import SimilarityPostprocessor
from llama_index.core.schema import Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import QueryFusionRetriever
import logging
import sys
import dotenv
import time
import random

# Load environment variables
dotenv.load_dotenv()

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

class FinancialPlanningBot:
    def __init__(self, pdf_path="../data/PERSONAL_FINANCIAL_PLANNING.pdf"):
        self.pdf_path = pdf_path
        self.index = None
        self.hybrid_retriever = None
        self.similarity_threshold = 0.7  # Threshold for similarity filtering
        
        # Validate API key before proceeding
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set. Please set it and try again.")
            
        # Configure LLM with API key
        self.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.0, api_key=api_key)
        
        # Initialize embeddings with rate limiting
        self.initialize_bot()
    
    def initialize_bot(self):
        print("📚 Loading document...")
        # Ensure the PDF is in the data folder
        if not os.path.exists("data"):
            os.makedirs("data")
            
        if not os.path.exists(self.pdf_path) and os.path.exists(os.path.basename(self.pdf_path)):
            # Copy the file to the data directory if it's in the root
            import shutil
            shutil.copy(os.path.basename(self.pdf_path), self.pdf_path)
            
        # Load documents
        documents = SimpleDirectoryReader(input_files=[self.pdf_path]).load_data()
        
        print("✂️ Chunking document...")
        # Parse documents into nodes (chunks)
        parser = SimpleNodeParser.from_defaults(chunk_size=1000, chunk_overlap=200)
        nodes = parser.get_nodes_from_documents(documents)
        
        print("Creating embeddings and setting up retrievers...")
        # Set up embedding model with explicit rate limiting
        try:
            embed_model = OpenAIEmbedding(
                model_name="text-embedding-ada-002",
                api_key=os.getenv("OPENAI_API_KEY"),
                timeout=60,  # Increase timeout
                max_retries=3  # Limit retries
            )
            
            # Create index with backoff
            self._create_index_with_backoff(nodes, embed_model)
            
        except Exception as e:
            print(f"❌ Error initializing embeddings: {str(e)}")
            raise
        
        print("Bot is ready to answer your financial planning questions!")
    
    def _create_index_with_backoff(self, nodes, embed_model, max_attempts=5):
        """Create index with exponential backoff retry logic"""
        attempt = 0
        while attempt < max_attempts:
            try:
                self.index = VectorStoreIndex(nodes, embed_model=embed_model)
                
                # Create vector retriever
                vector_retriever = VectorIndexRetriever(
                    index=self.index,
                    similarity_top_k=3,
                )
                
                # Create BM25 retriever
                bm25_retriever = BM25Retriever.from_defaults(
                    nodes=nodes,
                    similarity_top_k=3,
                )
                
                # Set up hybrid retriever using query fusion
                self.hybrid_retriever = QueryFusionRetriever(
                    retrievers=[bm25_retriever, vector_retriever],
                    similarity_top_k=3,
                    mode="simple"  # Using simple mode which is supported
                )
                return
                
            except Exception as e:
                attempt += 1
                wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                print(f"Attempt {attempt}/{max_attempts} failed: {str(e)}")
                print(f"Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
        
        raise RuntimeError("Failed to create index after multiple attempts")
    
    def answer_question(self, question):
        print(f"\n Question: {question}\n")
        print(" Retrieving relevant information...")
        
        try:
            # Retrieve relevant nodes
            retrieved_nodes = self.hybrid_retriever.retrieve(question)
            
            # Apply similarity postprocessing to filter results
            postprocessor = SimilarityPostprocessor(similarity_cutoff=self.similarity_threshold)
            filtered_nodes = postprocessor.postprocess_nodes(retrieved_nodes, query_str=question)
            
            print(f" Found {len(filtered_nodes)} relevant chunks after similarity filtering")
            
            # If no nodes passed the similarity threshold, use original retrieved nodes
            if not filtered_nodes:
                print(" Using all retrieved nodes as none passed similarity threshold")
                filtered_nodes = retrieved_nodes
            
            # Build context for the query
            context_str = "\n\n".join([f"[Page {node.metadata.get('page_label', 'unknown')}]: {node.get_content()}" 
                                        for node in filtered_nodes])
            
            # Create prompt for the query
            query_engine_prompt = f"""You are a helpful and friendly financial planning assistant.
Use the following information to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Always provide specific information from the context.
When answering, cite the page number in square brackets at the end of each relevant piece of information, like [Page X].

Context:
{context_str}

Question: {question}

Answer: """
            
            # Get answer from LLM
            answer = self.llm.complete(query_engine_prompt)
            
            # Display the answer
            print("\n Answer:")
            print(answer)
            
            # For comparison, get answer without RAG (pure prompting)
            print("\n Comparing with pure prompting (no retrieval):")
            direct_answer = self.get_direct_answer(question)
            print(direct_answer)
            
            print("\n Sources used:")
            for i, node in enumerate(filtered_nodes):
                print(f"Source {i+1}: Page {node.metadata.get('page_label', 'unknown')}, " 
                      f"Score: {node.score:.4f if hasattr(node, 'score') else 'N/A'}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def get_direct_answer(self, question):
        # Simple direct prompting without retrieval
        prompt = f"Answer this financial planning question: {question}"
        return self.llm.complete(prompt)


def main():
    print(" Financial Planning Q&A Bot ")
    print("--------------------------------")
    
    # Initialize the bot
    bot = FinancialPlanningBot()
    
    # Interactive command loop
    while True:
        print("\n" + "-"*60)
        command = input("\n Enter your question (or type 'exit' to quit): ")
        
        if command.lower() in ['exit', 'quit']:
            print("-------Thanks for using the Financial Planning Bot!")
            break
        
        bot.answer_question(command)

if __name__ == "__main__":
    main()