# Financial Planning Bot (Mini-RAG) Architecture

## Overview
The Financial Planning Bot is a Retrieval-Augmented Generation (RAG) system that answers financial planning questions by referencing a PDF document. It combines keyword-based and vector-based retrieval methods to provide accurate answers.

## Architecture Components

### 1. Document Processing
- **Input**: PDF financial planning document
- **Process**:
  - Document loading via `SimpleDirectoryReader`
  - Text chunking with `SimpleNodeParser` (1000 token chunks, 200 token overlap)
- **Output**: Collection of text nodes with metadata (including page numbers)

### 2. Indexing System
- **Vector Index**:
  - Uses OpenAI's text-embedding-ada-002 model
  - Transforms text chunks into vector embeddings
  - Stores in VectorStoreIndex for similarity search
- **Keyword Index**:
  - BM25 statistical ranking function
  - Language-agnostic lexical search

### 3. Hybrid Retrieval System
- **Components**:
  - Vector Retriever: Semantic search using embeddings
  - BM25 Retriever: Keyword-based search
  - Query Fusion: Combines both retrieval methods
- **Configuration**:
  - Each retriever fetches top-k=3 results
  - Fusion mode: "simple" (combining results)

### 4. Question Answering
- **RAG Pipeline**:
  1. User question received
  2. Hybrid retrieval fetches relevant document chunks
  3. Retrieved chunks assembled into context
  4. Context + question sent to OpenAI's GPT-3.5 Turbo
  5. LLM generates answer with citations
- **Comparison Feature**:
  - Direct prompting (non-RAG approach)
  - Same question sent to LLM without retrieved context
  - Both answers displayed for comparison

### 5. System Resilience
- API request handling with exponential backoff
- Error handling and logging
- Environment variable validation

## Data Flow
1. User inputs a question
2. Question processed by hybrid retriever
3. Retrieved context chunks combined with the question
4. Combined prompt sent to LLM
5. Answer returned to user with source citations
6. Comparison answer (non-RAG) also displayed

## Implementation Notes
- Built on llama-index framework
- Uses OpenAI APIs for embeddings and LLM
- Implements error handling and retry mechanisms
- Interactive command-line interface
