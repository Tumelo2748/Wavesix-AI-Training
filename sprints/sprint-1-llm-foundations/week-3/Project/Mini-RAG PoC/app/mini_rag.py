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

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

class FinancialPlanningBot:
    def __init__(self, pdf_path="../data/PERSONAL_FINANCIAL_PLANNING.pdf"):
        self.pdf_path = pdf_path
        self.index = None
        self.hybrid_retriever = None
        self.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.0)
        self.llm.api_key = os.getenv("OPENAI_API_KEY")
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
        # Set up embedding model
        embed_model = OpenAIEmbedding(model_name="text-embedding-ada-002")
        
        # Create index
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
        
        print("Bot is ready to answer your financial planning questions!")
    
    def answer_question(self, question):
        print(f"\n Question: {question}\n")
        print(" Retrieving relevant information...")
        
        try:
            # Retrieve relevant nodes
            retrieved_nodes = self.hybrid_retriever.retrieve(question)
            
            # Build context for the query
            context_str = "\n\n".join([f"[Page {node.metadata.get('page_label', 'unknown')}]: {node.get_content()}" 
                                        for node in retrieved_nodes])
            
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
            for i, node in enumerate(retrieved_nodes):
                print(f"Source {i+1}: Page {node.metadata.get('page_label', 'unknown')}")
                
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