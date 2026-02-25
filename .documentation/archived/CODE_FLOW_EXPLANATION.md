# Code Flow Explanation - RAG System

## Overview Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         STREAMLIT WEB UI                            │
│              (app/streamlit_app.py)                                 │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       RAG PIPELINE                                  │
│              (src/rag_pipeline.py)                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Orchestrates all components:                                │   │
│  │ - PDF Processing                                            │   │
│  │ - Embedding Generation                                      │   │
│  │ - Semantic Retrieval                                        │   │
│  │ - LLM Generation                                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
         │           │           │           │
         ▼           ▼           ▼           ▼
    ┌────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐
    │ PDF    │ │Embedding │ │Retrieval│ │ LLM     │
    │Process │ │ Manager  │ │ System  │ │ Handler │
    │        │ │          │ │        │ │(Groq)  │
    └────────┘ └──────────┘ └────────┘ └──────────┘

```

---

## Scenario 1: User Uploads PDF Document

### Timeline & Function Calls

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. USER ACTION: Clicks "Upload PDF" & selects file                 │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ streamlit_app.py::main() [Line 170-200]                            │
│                                                                     │
│ if uploaded_file is not None:                                      │
│   ├─ Save file to DOCUMENTS_DIR                                   │
│   ├─ Initialize RAGPipeline if needed                             │
│   └─ Call: pipeline.pipeline(pdf_path=file_path)                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ RAGPipeline.pipeline() [rag_pipeline.py::290-350]                  │
│                                                                     │
│ def pipeline(pdf_path, query=None, ...):                           │
│   ├─ chunks = process_pdf(pdf_path)                               │
│   ├─ embedded = embed_chunks(chunks)                              │
│   ├─ setup_retriever(embedded)                                    │
│   └─ return {"status": "success", "chunks_processed": len(...)}   │
└─────────────────────────────────────────────────────────────────────┘
         │           │           │
    ┌────┴──┐   ┌────┴──┐   ┌───┴────┐
    │       │   │       │   │        │
    ▼       ▼   ▼       ▼   ▼        ▼

Step 1: process_pdf()      Step 2: embed_chunks()     Step 3: setup_retriever()
Step 2: embed all chunks   Step 3: add embeddings     Step 4: prepare for search
```

### Detailed Step-by-Step Breakdown

#### **Step 1: PDF Processing**

```python
# Location: RAGPipeline.process_pdf() [rag_pipeline.py::57-72]
def process_pdf(self, pdf_path: str):
    chunks = self.pdf_processor.process_pdf(pdf_path)
    return chunks


# Calls PDFProcessor.process_pdf() [pdf_processor.py::95-200]
def process_pdf(self, pdf_path):
    # 1. Extract text from all pages
    pages = extract_text_from_pdf(pdf_path)
    #    └─> Uses fitz (PyMuPDF) to open PDF and read each page
    #    └─> Returns: [{"page_num": 0, "text": "..."}, ...]
    
    # 2. Clean and format text
    cleaned_pages = [text_formatter(page["text"]) for page in pages]
    #    └─> Removes \n, extra spaces, normalizes text
    
    # 3. Split into sentences using spaCy
    sentences = split_text_into_sentences(cleaned_text)
    #    └─> Uses NLP sentenceizer to find sentence boundaries
    
    # 4. Group sentences into chunks
    chunks = combine_sentences_into_chunks(sentences)
    #    └─> Groups multiple sentences into SENTENCE_CHUNK_SIZE
    #    └─> Ensures each chunk has MIN_CHUNK_TOKENS
    
    # 5. Return formatted chunks
    return [
        {
            "sentence_chunk": "The quick brown fox...",
            "chunk_token_count": 125,
            "page_number": 0
        },
        ...  # More chunks
    ]
```

**Data Transformation in Step 1:**
```
PDF File (document.pdf)
    │
    ▼
[Page 0: "...", Page 1: "...", ...]  (extract_text_from_pdf)
    │
    ▼
["Sentence 1. Sentence 2.", ...]  (split_into_sentences)
    │
    ▼
[
  {"sentence_chunk": "Sentence 1. Sentence 2.", "chunk_token_count": 25, "page_number": 0},
  {"sentence_chunk": "Sentence 3. Sentence 4.", "chunk_token_count": 22, "page_number": 0},
  ...
]
```

#### **Step 2: Embedding Generation**

```python
# Location: RAGPipeline.embed_chunks() [rag_pipeline.py::74-88]
def embed_chunks(self, chunks):
    embedded_chunks = self.embedding_manager.embed_chunks(chunks)
    return embedded_chunks


# Calls EmbeddingManager.embed_chunks() [embedding_manager.py::90-140]
def embed_chunks(self, chunks):
    # 1. Extract text from all chunks
    texts = [chunk["sentence_chunk"] for chunk in chunks]
    #    └─> ["The quick brown fox...", "Sentence 3. Sentence 4...", ...]
    
    # 2. Generate embeddings using SentenceTransformer
    embeddings = self.generate_embeddings(texts)
    #    └─> Uses 'all-mpnet-base-v2' model by default
    #    └─> Processes in batches (batch_size=32)
    #    └─> Returns: numpy array of shape (num_chunks, 768)
    #    └─> Each text → 768-dimensional vector
    
    # 3. Add embeddings back to chunks
    for i, chunk in enumerate(chunks):
        chunk["embedding"] = embeddings[i]
    
    # 4. Return enriched chunks
    return chunks
    # Result: [
    #   {"sentence_chunk": "...", "chunk_token_count": 25, "page_number": 0, 
    #    "embedding": [0.123, -0.456, 0.789, ...]},  # 768 floats
    #   ...
    # ]
```

**Visual: Embedding Process**
```
Text Chunk: "The quick brown fox jumps over the lazy dog"
    │
    ▼
[Token 1, Token 2, Token 3, ...]  (Tokenized)
    │
    ▼
Transformer Model (all-mpnet-base-v2)
    │
    ▼
Embedding Vector: [0.123, -0.456, 0.789, ..., 0.042]  (768 dimensions)
    │
    ▼
Store in chunk dictionary
```

#### **Step 3: Retriever Setup**

```python
# Location: RAGPipeline.setup_retriever() [rag_pipeline.py::90-110]
def setup_retriever(self, chunks, top_k):
    config = RetrieverConfig(top_k=top_k)
    self.retriever = SemanticRetriever(
        chunks_with_embeddings=chunks,
        embedding_manager=self.embedding_manager,
        config=config
    )
    self.chunks = chunks
    return


# Calls SemanticRetriever.__init__() [retrieval.py::35-60]
def __init__(self, chunks_with_embeddings, embedding_manager, config):
    self.chunks = chunks_with_embeddings
    self.embedding_manager = embedding_manager
    self.config = config  # top_k=5, threshold=0.0, etc.
    
    # Prepare embeddings tensor for fast similarity search
    self.embeddings = self._prepare_embeddings()
    #    └─> Extracts all embeddings from chunks
    #    └─> Converts to torch tensor
    #    └─> Shape: (num_chunks, 768)
    #    └─> Ready for cosine similarity calculations
```

**Status After Step 1-3:**
- PDF extracted and cleaned ✓
- Text split into chunks ✓
- Each chunk embedded (768-dim vector) ✓
- All chunks stored with metadata (page, text, embedding) ✓
- Retriever initialized and ready to find similar chunks ✓

---

## Scenario 2: User Asks a Question

### Timeline & Function Calls

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. USER ACTION: Types question & clicks "Ask"                      │
│    Query: "What is this document about?"                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ streamlit_app.py::main() [Line 245-270]                            │
│                                                                     │
│ if submit and query:                                               │
│   answer, context = pipeline.ask(                                  │
│       query="What is this document about?",                        │
│       top_k=5,                                                     │
│       temperature=0.7,                                             │
│       max_new_tokens=512,                                          │
│       return_context=True                                          │
│   )                                                                │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ RAGPipeline.ask() [rag_pipeline.py::256-280]                       │
│                                                                     │
│ def ask(query, top_k, temperature, max_new_tokens, return_context):│
│   ├─ context_chunks = self.retrieve(query, top_k=5)               │
│   ├─ answer = self.generate(query, context_chunks, ...)           │
│   └─ return answer, context_chunks                                │
└─────────────────────────────────────────────────────────────────────┘
         │                                    │
         ▼                                    ▼
    retrieve()                           generate()
    [Find similar                        [Generate answer]
     chunks]
```

### Detailed Step-by-Step Breakdown

#### **Step A: Retrieval (Finding Relevant Context)**

```python
# Location: RAGPipeline.retrieve() [rag_pipeline.py::120-145]
def retrieve(self, query, top_k=5):
    return self.retriever.retrieve_with_metadata(query, top_k=5)


# Calls SemanticRetriever.retrieve_with_metadata() [retrieval.py::110-180]
def retrieve_with_metadata(self, query, top_k=None):
    # 1. Embed the user's query using the same model
    query_embedding = self.embedding_manager.generate_embeddings(query, show_progress_bar=False)
    #    └─> Takes: "What is this document about?"
    #    └─> Returns: [0.234, -0.567, 0.890, ...]  (768 dimensions)
    #    └─> Same model used for chunk embeddings (all-mpnet-base-v2)
    
    # 2. Calculate similarity between query and all chunks
    cos_sim = util.cos_sim(query_embedding, self.embeddings)
    #    └─> Compares query_embedding with all chunk embeddings
    #    └─> Uses cosine similarity formula
    #    └─> Returns scores for each chunk
    #    └─> Example: [0.87, 0.65, 0.92, 0.34, 0.78, 0.44, ...]
    
    # 3. Get top-k results
    top_k = top_k or self.config.top_k  # default: 5
    top_results_idx = cos_sim[0].argsort(descending=True)[:top_k]
    #    └─> Sorts chunks by similarity score (highest first)
    #    └─> Keeps only top 5: indices [2, 0, 4, 1, 5]
    
    # 4. Retrieve full chunk data with metadata
    retrieved_chunks = []
    for idx in top_results_idx:
        chunk = self.chunks[idx].copy()
        chunk["similarity_score"] = cos_sim[0][idx].item()
        retrieved_chunks.append(chunk)
    
    # 5. Return chunks with scores
    return retrieved_chunks
    # Result: [
    #   {"sentence_chunk": "...", "page_number": 0, "chunk_token_count": 25,
    #    "similarity_score": 0.92},
    #   {"sentence_chunk": "...", "page_number": 2, "chunk_token_count": 28,
    #    "similarity_score": 0.87},
    #   {"sentence_chunk": "...", "page_number": 5, "chunk_token_count": 22,
    #    "similarity_score": 0.78},
    #   ...  (5 total)
    # ]
```

**Visual: Semantic Similarity Search**

```
User Query:
"What is this document about?"
    │
    ▼
Query Embedding: [0.234, -0.567, 0.890, ..., -0.123]  (768-dim)
    │
    ▼
Calculate Cosine Similarity with ALL Chunk Embeddings
    │
    ├─► Chunk 0: similarity = 0.87
    ├─► Chunk 1: similarity = 0.65
    ├─► Chunk 2: similarity = 0.92  ◄─── Top 1
    ├─► Chunk 3: similarity = 0.34
    ├─► Chunk 4: similarity = 0.78
    ├─► Chunk 5: similarity = 0.44
    └─► Chunk 6: similarity = 0.81
    │
    ▼
Sort by Similarity (Top-K)
    │
    ├─ Index 2: 0.92  (Page 0: "Documents provide...")
    ├─ Index 0: 0.87  (Page 1: "This resource covers...")
    ├─ Index 4: 0.78  (Page 3: "Key topics include...")
    ├─ Index 6: 0.81  (Page 2: "We explore...")
    └─ Index 1: 0.65  (Page 4: "Additional details...")
    │
    ▼
Return Top 5 Chunks with Metadata
```

#### **Step B: Generation (Creating Answer)**

```python
# Location: RAGPipeline.generate() [rag_pipeline.py::147-180]
def generate(self, query, context_chunks, temperature=0.7, max_new_tokens=512):
    # 1. Format prompt with retrieved context
    prompt = self.llm_handler.format_prompt_with_context(query, context_chunks)
    

# Calls LLMHandler.format_prompt_with_context() [llm_handler.py::160-180]
def format_prompt_with_context(self, query, context_chunks):
    # Build the prompt with context
    context_string = ""
    for i, chunk in enumerate(context_chunks, 1):
        context_string += f"\n[Chunk {i} from Page {chunk['page_number']}]:\n{chunk['sentence_chunk']}\n"
    
    # Final prompt structure:
    prompt = f"""Use the following context to answer the question.

Context:
{context_string}

Question: {query}

Answer:"""
    
    return prompt
    
    # Example output:
    # """Use the following context to answer the question.
    # 
    # Context:
    # [Chunk 1 from Page 0]:
    # This document provides comprehensive information about artificial intelligence...
    # 
    # [Chunk 2 from Page 1]:
    # AI encompasses machine learning, deep learning, and neural networks...
    # 
    # [Chunk 3 from Page 3]:
    # Applications of AI include natural language processing, computer vision...
    # 
    # Question: What is this document about?
    # 
    # Answer:"""


# Back to RAGPipeline.generate() [rag_pipeline.py::147-180]
def generate(self, query, context_chunks, temperature=0.7, max_new_tokens=512):
    prompt = self.llm_handler.format_prompt_with_context(query, context_chunks)
    
    # 2. Call LLM with formatted prompt
    answer = self.llm_handler.generate(
        prompt=prompt,
        temperature=temperature,
        max_new_tokens=max_new_tokens
    )
    

# Calls LLMHandler.generate() [llm_handler.py::52-100]
def generate(self, prompt, temperature=None, max_new_tokens=None, **kwargs):
    # 1. Use provided values or defaults
    temp = temperature if temperature is not None else self.temperature  # 0.7
    max_tok = max_new_tokens if max_new_tokens is not None else self.max_tokens  # 512
    
    # 2. Call Groq API
    response = self.client.chat.completions.create(
        model=self.model_id,  # "llama-3.3-70b-versatile"
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=temp,          # 0.7 (balanced creativity)
        max_tokens=max_tok,        # 512 (response length limit)
        top_p=1.0,                 # nucleus sampling
    )
    # 
    # API Call Details:
    # - Sends prompt to Groq servers
    # - Model: llama-3.3-70b-versatile processes the prompt
    # - Returns response in <1 second typically
    
    # 3. Extract generated text
    generated_text = response.choices[0].message.content
    
    # 4. Return answer
    return generated_text
    # Returns: "This document is a comprehensive guide to artificial intelligence,
    #          covering machine learning, deep learning, and practical applications..."
```

**Visual: Prompt Construction & Generation**

```
Step 1: Retrieve Context
┌──────────────────────────────────────────────────────────────┐
│ Retrieved Chunks (from semantic search):                     │
│                                                              │
│ [Chunk 1]: "AI encompasses machine learning, deep learning" │
│ [Chunk 2]: "Applications include NLP, computer vision"      │
│ [Chunk 3]: "Neural networks are fundamental to modern AI"   │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
Step 2: Format Prompt
┌──────────────────────────────────────────────────────────────┐
│ Formatted Prompt:                                            │
│                                                              │
│ Use the following context to answer the question.            │
│                                                              │
│ Context:                                                     │
│ [Chunk 1 from Page 0]:                                      │
│ AI encompasses machine learning, deep learning...            │
│                                                              │
│ [Chunk 2 from Page 1]:                                      │
│ Applications include NLP, computer vision...                 │
│                                                              │
│ [Chunk 3 from Page 3]:                                      │
│ Neural networks are fundamental to modern AI...              │
│                                                              │
│ Question: What is this document about?                       │
│                                                              │
│ Answer:                                                      │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
Step 3: Call Groq API
┌──────────────────────────────────────────────────────────────┐
│ Groq API Call:                                               │
│ - Model: llama-3.3-70b-versatile                             │
│ - Temperature: 0.7 (somewhat creative)                       │
│ - Max Tokens: 512 (response limit)                           │
│                                                              │
│ Processing on Groq servers...                                │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
Step 4: Return Generated Answer
┌──────────────────────────────────────────────────────────────┐
│ Generated Response:                                          │
│                                                              │
│ "This document is a comprehensive guide to artificial       │
│  intelligence. It covers the fundamentals of machine        │
│  learning and deep learning, explains how neural networks   │
│  work, and discusses practical applications in areas like   │
│  natural language processing and computer vision..."        │
└──────────────────────────────────────────────────────────────┘
```

#### **Step C: Return to User**

```python
# Back to streamlit_app.py::main() [Line 245-280]
answer, context = st.session_state.pipeline.ask(
    query="What is this document about?",
    top_k=5,
    temperature=0.7,
    max_new_tokens=512,
    return_context=True
)

# Display results
st.markdown("### Answer:")
st.write(answer)

with st.expander("Show Retrieved Context"):
    for i, chunk in enumerate(context, 1):
        st.markdown(f"**Chunk {i}** (Score: {chunk['similarity_score']:.4f})")
        st.write(chunk['sentence_chunk'])

# Add to chat history
st.session_state.chat_history.append({
    "role": "user",
    "content": query
})
st.session_state.chat_history.append({
    "role": "assistant",
    "content": answer,
    "context": context
})

st.rerun()  # Redraw UI with new messages
```

---

## Complete Call Sequence

### Example Execution Timeline

```
TIME    EVENT                                          COMPONENT
────────────────────────────────────────────────────────────────────

T=0ms   User clicks "Upload PDF"                       [Web Browser]
        ├─ File: "sample_document.pdf" (5.2 MB)


T=50ms  File saved to disk                            [Streamlit]
        ├─ Path: documents/sample_document.pdf


T=100ms RAGPipeline.__init__()                        [RAGPipeline]
        ├─ Initialize PDFProcessor
        ├─ Initialize EmbeddingManager
        ├─ Initialize LLMHandler (Groq client)
        └─ Status: Ready


T=200ms pipeline.pipeline(pdf_path)                   [RAGPipeline]
        ├─ START: process_pdf()


T=500ms  ├─ PDF extraction complete (50 pages)        [PDFProcessor]
        │  └─ 2,400 text chunks identified


T=1000m ├─ Text formatting & cleaning                 [PDFProcessor]
        │  └─ Combined into 245 final chunks


T=1500m ├─ COMPLETE: process_pdf()
        ├─ START: embed_chunks()


T=2000m ├─ Batch 1 (245 chunks)                       [EmbeddingManager]
        │  └─ Generating embeddings (SentenceTransformer)


T=3000m ├─ All embeddings generated                   [EmbeddingManager]
        │  └─ Shape: (245, 768) - 245 vectors, 768 dimensions


T=3100m ├─ COMPLETE: embed_chunks()
        ├─ START: setup_retriever()


T=3200m ├─ Retriever initialized                      [SemanticRetriever]
        │  └─ 245 chunks + embeddings ready
        │  └─ Similarity search enabled


T=3300m ├─ COMPLETE: setup_retriever()
        └─ UI: "✅ Successfully processed 245 chunks!"


       ============ USER TYPES QUESTION ============


T=4000m User types: "What is this document about?"    [Web Browser]
        & clicks "Ask"


T=4050m pipeline.ask(query, ...)                      [RAGPipeline]
        ├─ START: retrieve()


T=4100m ├─ Generate query embedding                   [EmbeddingManager]
        │  └─ "What is this document about?"
        │  └─ Returns: [0.234, -0.567, ..., 0.042] (768-dim)


T=4200m ├─ Calculate similarity with all chunks       [SemanticRetriever]
        │  └─ Cosine similarity: [0.34, 0.87, 0.92, 0.65, ...]


T=4300m ├─ Sort & get top-5 chunks                    [SemanticRetriever]
        │  └─ Indices: [2, 0, 4, 1, 6] with scores [0.92, 0.87, 0.78, 0.65, 0.61]


T=4350m ├─ COMPLETE: retrieve()
        ├─ START: generate()


T=4400m ├─ Format prompt with context                 [LLMHandler]
        │  └─ Prompt: "Use the following context... Question: ..."


T=4500m ├─ Call Groq API                              [Groq Cloud]
        │  └─ Model: llama-3.3-70b-versatile
        │  └─ Temperature: 0.7, Max Tokens: 512


T=4600m ├─ [Processing on Groq servers...]


T=4700m ├─ Groq API Returns Response                  [Groq Cloud]
        │  └─ Full text: "This document is a comprehensive..."


T=4750m ├─ COMPLETE: generate()
        └─ answer = "This document is a comprehensive..."


T=4800m Display Results                               [Streamlit]
        ├─ Answer: "This document is a comprehensive..."
        ├─ Show context with similarity scores
        ├─ Add to chat history
        └─ Rerun UI


T=4850m Page refreshed with answer visible            [Web Browser]
```

---

## Data Flow Diagrams

### Upload & Process PDF Flow

```
PDF File
   │
   ├─────────────► PDFProcessor.process_pdf()
   │               ├─ Extract text (fitz/PyMuPDF)
   │               ├─ Clean & format
   │               ├─ Split into sentences (spaCy)
   │               └─ Combine into chunks
   │
   ├─► Chunks: [
   │       {"sentence_chunk": "...", "page_number": 0, "chunk_token_count": 25},
   │       {"sentence_chunk": "...", "page_number": 1, "chunk_token_count": 30},
   │       ...
   │   ]
   │
   ├─────────────► EmbeddingManager.embed_chunks()
   │               ├─ Extract texts from chunks
   │               ├─ Generate embeddings (all-mpnet-base-v2)
   │               └─ Return embeddings (768-dim vectors)
   │
   ├─► Embedded Chunks: [
   │       {"sentence_chunk": "...", "embedding": [0.12, -0.45, ..., 0.08], ...},
   │       {"sentence_chunk": "...", "embedding": [0.34, 0.67, ..., -0.21], ...},
   │       ...
   │   ]
   │
   ├─────────────► SemanticRetriever.__init__()
   │               ├─ Store chunks
   │               ├─ Extract embeddings tensor
   │               └─ Prepare for similarity search
   │
   └─► Status: Ready for queries
```

### Query & Answer Flow

```
User Query: "What is this document about?"
   │
   ├─────────────► EmbeddingManager.generate_embeddings()
   │               └─ Returns query embedding (768-dim)
   │
   ├─► Query Embedding: [0.234, -0.567, 0.890, ...]
   │
   ├─────────────► SemanticRetriever.retrieve_with_metadata()
   │               ├─ Calculate cosine similarity with all chunks
   │               ├─ Sort by similarity
   │               └─ Return top-5 chunks
   │
   ├─► Retrieved Chunks:
   │   [
   │       {"sentence_chunk": "...", "similarity_score": 0.92, "page_number": 0},
   │       {"sentence_chunk": "...", "similarity_score": 0.87, "page_number": 1},
   │       {"sentence_chunk": "...", "similarity_score": 0.78, "page_number": 3},
   │       {"sentence_chunk": "...", "similarity_score": 0.65, "page_number": 2},
   │       {"sentence_chunk": "...", "similarity_score": 0.61, "page_number": 4}
   │   ]
   │
   ├─────────────► LLMHandler.format_prompt_with_context()
   │               └─ Create prompt: "Context:...\n\nQuestion:...\n\nAnswer:"
   │
   ├─► Formatted Prompt:
   │   """
   │   Use the following context to answer the question.
   │   
   │   Context:
   │   [Chunk 1 from Page 0]: ...text...
   │   [Chunk 2 from Page 1]: ...text...
   │   [Chunk 3 from Page 3]: ...text...
   │   [Chunk 4 from Page 2]: ...text...
   │   [Chunk 5 from Page 4]: ...text...
   │   
   │   Question: What is this document about?
   │   
   │   Answer:
   │   """
   │
   ├─────────────► LLMHandler.generate()
   │               ├─ Call Groq API
   │               ├─ Model: llama-3.3-70b-versatile
   │               ├─ Temperature: 0.7
   │               ├─ Max Tokens: 512
   │               └─ Return response text
   │
   ├─► Generated Answer:
   │   "This document is a comprehensive guide to artificial intelligence.
   │    It covers machine learning, deep learning, neural networks, and
   │    practical applications in NLP and computer vision. The document
   │    provides both theoretical foundations and practical examples..."
   │
   └─► Display in Streamlit UI + Add to chat history
```

---

## Key Function Reference

### Core Functions Called

| Function | Location | Purpose |
|----------|----------|---------|
| `RAGPipeline.__init__()` | rag_pipeline.py:30-51 | Initialize all components |
| `RAGPipeline.pipeline()` | rag_pipeline.py:290-350 | Complete document processing |
| `RAGPipeline.ask()` | rag_pipeline.py:256-280 | Answer user questions |
| `RAGPipeline.retrieve()` | rag_pipeline.py:120-145 | Find relevant chunks |
| `RAGPipeline.generate()` | rag_pipeline.py:147-180 | Generate answer from chunks |
| `PDFProcessor.process_pdf()` | pdf_processor.py:95-200 | Extract & chunk PDF |
| `EmbeddingManager.embed_chunks()` | embedding_manager.py:90-140 | Create embeddings |
| `SemanticRetriever.retrieve_with_metadata()` | retrieval.py:110-180 | Find similar chunks |
| `LLMHandler.format_prompt_with_context()` | llm_handler.py:160-180 | Build prompt with context |
| `LLMHandler.generate()` | llm_handler.py:52-100 | Call Groq API |

---

## Performance Characteristics

### Timing (Approximate)

```
PDF Upload & Processing:
├─ PDF Extraction:        200-500ms (depends on page count)
├─ Text Cleaning:         100-200ms
├─ Chunking:              100-300ms
├─ Embedding Generation: 1000-2000ms (depends on chunk count)
└─ Total:                1400-3000ms (fairly quick!)

User Query & Answer:
├─ Query Embedding:       50-100ms
├─ Similarity Search:     50-200ms (very fast with torch)
├─ Prompt Formatting:     10-50ms
├─ Groq API Call:        500-2000ms (API latency)
├─ Response Display:      50-100ms
└─ Total:                700-2500ms (typically 1-2 seconds)
```

### Memory Usage

```
Document Processing:
├─ PDFProcessor: ~50MB (depends on PDF size)
├─ Embeddings: ~200MB (245 chunks × 768 dims × 4 bytes)
├─ EmbeddingModel: ~150MB (all-mpnet-base-v2 loaded)
└─ Total: ~400-500MB

Query Processing:
├─ Query Embedding: ~3MB
├─ Retrieval: <1MB
└─ Total: ~400-500MB (mostly from models)
```

---

## Summary

### Upload PDF:
1. Save file → Extract pages → Clean text → Split sentences → Group into chunks
2. Generate 768-dim embeddings for each chunk
3. Initialize retriever for semantic search

### Answer Question:
1. Embed user query (768-dim vector)
2. Find top-5 most similar chunks using cosine similarity
3. Format prompt with context chunks
4. Call Groq API with formatted prompt
5. Return generated answer + context chunks to user

All operations are **fast, efficient, and cloud-based**. The embedding model runs locally (CPU), while the LLM runs on Groq's servers.
