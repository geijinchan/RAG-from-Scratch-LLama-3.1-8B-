"""
RAG PIPELINE - COMPLETE FUNCTION FLOW DOCUMENTATION

This document details the exact function calling sequence and data flow
through the entire RAG system, from user action to response.
"""

# ============================================================================
# COMPREHENSIVE FUNCTION FLOW DOCUMENTATION
# ============================================================================

## 🎯 SCENARIO 1: USER UPLOADS PDF IN STREAMLIT APP
### Timeline & Function Calls

```
USER ACTION: Clicks "Upload PDF Document" and selects a file
│
├─→ Streamlit Event: streamlit_app.py :: file_uploader()
│   │
│   └─→ streamlit_app.py :: initialize_pipeline() [FIRST RUN ONLY]
│       │
│       └─→ RAGPipeline.__init__()
│           ├─→ PDFProcessor.__init__()
│           │   └─→ spacy.lang.en.English()
│           │       └─→ nlp.add_pipe("sentencizer")
│           │
│           ├─→ EmbeddingManager.__init__()
│           │   └─→ SentenceTransformer() [Downloads model ~400MB]
│           │
│           └─→ LLMHandler.__init__() [MAY TAKE 10+ MINUTES]
│               ├─→ AutoTokenizer.from_pretrained()
│               └─→ AutoModelForCausalLM.from_pretrained() [Downloads ~16GB]
│
└─→ streamlit_app.py :: Main Upload Section
    │
    ├─→ Save uploaded file to DOCUMENTS_DIR
    │   └─→ Path: data/documents/{filename}
    │
    ├─→ Pipeline.pipeline()
    │   │
    │   ├── STEP 1: Process PDF ─────────────────────────────────
    │   │   └─→ PDFProcessor.process_pdf(pdf_path)
    │   │       │
    │   │       ├─→ extract_text_from_pdf(pdf_path)
    │   │       │   ├─→ fitz.open(pdf_path)
    │   │       │   └─→ Loop: for each page
    │   │       │       ├─→ page.get_text()
    │   │       │       └─→ text_formatter(text)
    │   │       │           └─→ re.sub() - clean whitespace
    │   │       │
    │   │       ├─→ split_into_sentences(pages_and_texts)
    │   │       │   └─→ Loop: for each page
    │   │       │       ├─→ nlp(text)  [spaCy sentencizer]
    │   │       │       └─→ Extract sentences
    │   │       │
    │   │       ├─→ chunk_sentences(pages_and_texts)
    │   │       │   └─→ Loop: for each page
    │   │       │       └─→ _split_list(sentences, chunk_size=10)
    │   │       │
    │   │       ├─→ create_chunks(pages_and_texts)
    │   │       │   └─→ Loop: page → chunks → individual items
    │   │       │       ├─→ Join sentences
    │   │       │       └─→ Calculate token count
    │   │       │
    │   │       └─→ filter_chunks(pages_and_chunks)
    │   │           └─→ pandas: Filter by token_count > MIN_CHUNK_TOKENS
    │   │
    │   ├── STEP 2: Generate Embeddings ────────────────────────
    │   │   └─→ RAGPipeline.embed_chunks(chunks)
    │   │       └─→ EmbeddingManager.embed_chunks(chunks)
    │   │           └─→ Extract texts from chunks
    │   │           └─→ model.encode(texts, batch_size=32)
    │   │               └─→ Convert_to_tensor=True
    │   │           └─→ Attach embeddings to chunks
    │   │
    │   ├── STEP 3: Save Embeddings [OPTIONAL] ────────────────
    │   │   └─→ EmbeddingManager.save_embeddings(embedded_chunks)
    │   │       ├─→ Save chunks with embeddings
    │   │       │   └─→ pickle.dump() → embeddings.pkl
    │   │       └─→ Save metadata
    │   │           └─→ json.dump() → embeddings_metadata.json
    │   │
    │   ├── STEP 4: Setup Retriever ─────────────────────────────
    │   │   └─→ RAGPipeline.setup_retriever(embedded_chunks)
    │   │       └─→ SemanticRetriever.__init__()
    │   │           └─→ _prepare_embeddings()
    │   │               └─→ Convert numpy → torch tensors
    │   │
    │   └─→ Return: {"status": "success", "chunks_processed": N, ...}
    │
    └─→ Display: "✅ Successfully processed {N} chunks!"
        └─→ Set session_state.pdf_loaded = True

TIMELINE:
- Model download: 10-15 minutes (first run)
- PDF processing small doc (50 pages): 30-60 seconds
- Embedding generation: 1-3 minutes (100 chunks)
- Total first run: 15-20 minutes
- Total subsequent runs: 2-5 minutes
```

---

## 🎯 SCENARIO 2: USER SUBMITS A QUERY
### Timeline & Function Calls

```
USER ACTION: Types question and clicks "Ask"
│
├─→ Streamlit: query = st.text_input()
│
├─→ Streamlit Button: if submit and query
│   │
│   └─→ RAGPipeline.ask(query, top_k=5, temperature=0.7, return_context=True)
│       │
│       ├─── STEP 1: RETRIEVE CONTEXT ────────────────────────────────
│       │   │
│       │   └─→ RAGPipeline.retrieve(query, top_k=5)
│       │       │
│       │       └─→ SemanticRetriever.retrieve_with_metadata(query, top_k=5)
│       │           │
│       │           ├─→ embedding_manager.generate_embeddings(query)
│       │           │   └─→ SentenceTransformer.encode(query)
│       │           │       └─→ [768-dimensional vector]
│       │           │
│       │           ├─→ torch.nn.functional.dot_score(query_emb, embeddings)
│       │           │   └─→ Cosine similarity calculation
│       │           │
│       │           ├─→ torch.topk(scores, k=5)
│       │           │   └─→ Get top 5 most similar chunks
│       │           │
│       │           └─→ Attach similarity_scores to chunks
│       │
│       │   RESULT: [chunk1, chunk2, chunk3, chunk4, chunk5]
│       │           where each has similarity_score
│       │
│       ├─── STEP 2: FORMAT PROMPT WITH CONTEXT ─────────────────────
│       │   │
│       │   └─→ RAGPipeline.generate(query, context_chunks, ...)
│       │       │
│       │       └─→ LLMHandler.format_prompt_with_context(query, context_chunks)
│       │           │
│       │           ├─→ Extract text from each context chunk
│       │           │   └─→ "- " + "\n- ".join([chunks...])
│       │           │
│       │           ├─→ Create base_prompt with examples
│       │           │   └─→ base_prompt.format(context=context, query=query)
│       │           │
│       │           ├─→ Create dialogue_template
│       │           │   └─→ [{"role": "user", "content": formatted_prompt}]
│       │           │
│       │           └─→ tokenizer.apply_chat_template()
│       │               └─→ [formatted final prompt]
│       │
│       │   RESULT: Special formatted prompt with examples + context
│       │
│       ├─── STEP 3: GENERATE RESPONSE ────────────────────────────
│       │   │
│       │   └─→ LLMHandler.generate(prompt, temperature=0.7, max_tokens=512)
│       │       │
│       │       ├─→ tokenizer(prompt, return_tensors="pt")
│       │       │   └─→ Convert text to token IDs
│       │       │
│       │       ├─→ with torch.no_grad():
│       │       │   └─→ model.generate(
│       │       │       input_ids, 
│       │       │       temperature=0.7, 
│       │       │       max_new_tokens=512,
│       │       │       do_sample=True
│       │       │     )
│       │       │       └─→ Llama 3.1 8B generates tokens one-by-one
│       │       │           Loop: until EOF or max_tokens reached
│       │       │               ├─→ model(input_ids) → logits
│       │       │               ├─→ Apply temperature
│       │       │               ├─→ Sample next token
│       │       │               └─→ Append to output
│       │       │
│       │       ├─→ tokenizer.decode(output_ids)
│       │       │   └─→ Convert tokens back to text
│       │       │
│       │       └─→ Clean up output
│       │           └─→ Remove prompt, special tokens, etc.
│       │
│       │   RESULT: Generated answer text (200-500 words)
│       │
│       └─→ Return: (answer, context_chunks)
│
├─→ Add to chat history
│   └─→ st.session_state.chat_history.append({"role": "user", "content": query})
│   └─→ st.session_state.chat_history.append({"role": "assistant", "content": answer, "context": context})
│
└─→ Display answer
    └─→ st.write(answer)
    └─→ with st.expander("📚 Show Retrieved Context")
        └─→ for each context chunk
            ├─→ Display Score, Text, Page number

TIMELINE:
- Embedding generation: 50-200ms
- Similarity search: <50ms
- Prompt formatting: <100ms
- LLM generation: 5-30 seconds (depending on answer length)
- Total: 6-31 seconds per query

CONCURRENT OPERATIONS:
- User types next question while previous answer streams
- Chat history updates in real-time
```

---

## 📊 DETAILED FUNCTION REFERENCE

### PDFProcessor Functions

```
PDFProcessor.__init__()
│   └─→ Initialize spaCy NLP pipeline

PDFProcessor.text_formatter(text: str) → str
│   └─→ Clean and normalize text
│       ├─→ Remove newlines
│       ├─→ Remove extra spaces
│       └─→ Strip edges

PDFProcessor.extract_text_from_pdf(pdf_path: str) → List[Dict]
│   └─→ Extract raw text from PDF
│       ├─→ fitz.open(pdf_path)
│       └─→ for each page: page.get_text()

PDFProcessor.split_into_sentences(pages_and_texts) → List[Dict]
│   └─→ Use spaCy to split into sentences
│       └─→ nlp(text) → doc.sents

PDFProcessor.chunk_sentences(pages_and_texts) → List[Dict]
│   └─→ Group sentences
│       └─→ _split_list(sentences, chunk_size=10)

PDFProcessor.create_chunks(pages_and_texts) → List[Dict]
│   └─→ Create individual chunk items
│       ├─→ Join sentences
│       ├─→ Calculate statistics
│       └─→ Create chunk records

PDFProcessor.filter_chunks(pages_and_chunks) → List[Dict]
│   └─→ Remove short chunks
│       └─→ Filter by MIN_CHUNK_TOKENS

PDFProcessor.process_pdf(pdf_path) → List[Dict]
│   └─→ ORCHESTRATOR function
│       ├─→ extract_text_from_pdf()
│       ├─→ split_into_sentences()
│       ├─→ chunk_sentences()
│       ├─→ create_chunks()
│       └─→ filter_chunks()
```

### EmbeddingManager Functions

```
EmbeddingManager.__init__(model_name, device)
│   └─→ Load SentenceTransformer model

EmbeddingManager._load_model()
│   └─→ SentenceTransformer(model_name, device)

EmbeddingManager.generate_embeddings(texts, batch_size) → np.ndarray
│   └─→ model.encode(texts, batch_size)

EmbeddingManager.embed_chunks(chunks, batch_size) → List[Dict]
│   └─→ for each chunk
│       ├─→ generate_embeddings(chunk_text)
│       └─→ Attach embedding to chunk

EmbeddingManager.save_embeddings(chunks, filename) → Path
│   └─→ pickle.dump(chunks, file)
│   └─→ json.dump(metadata, file)

EmbeddingManager.load_embeddings(path) → List[Dict]
│   └─→ pickle.load(file)

EmbeddingManager.get_embedding_dimension() → int
│   └─→ model.get_sentence_embedding_dimension()
```

### SemanticRetriever Functions

```
SemanticRetriever.__init__(chunks, embedding_manager, config)
│   └─→ _prepare_embeddings()
│       └─→ Convert numpy embeddings to torch tensors

SemanticRetriever.retrieve(query, top_k) → (List[Dict], List[float])
│   └─→ embedding_manager.generate_embeddings(query)
│   └─→ util.dot_score(query_emb, embeddings)
│   └─→ torch.topk(scores, k)

SemanticRetriever.retrieve_with_metadata(query, top_k) → List[Dict]
│   └─→ retrieve(query, top_k)
│   └─→ Attach similarity_score to each chunk

SemanticRetriever.update_chunks(new_chunks)
│   └─→ Replace chunks and rebuild embeddings tensor

SemanticRetriever.add_chunks(new_chunks)
│   └─→ Extend chunks and rebuild embeddings tensor

SemanticRetriever.search_by_page(query, page_number, top_k) → List[Dict]
│   └─→ retrieve() and filter by page

SemanticRetriever.get_chunk_statistics() → Dict
│   └─→ Calculate and return statistics
```

### LLMHandler Functions

```
LLMHandler.__init__(model_id, device, use_8bit, use_4bit)
│   └─→ _load_model()
│       ├─→ AutoTokenizer.from_pretrained()
│       └─→ AutoModelForCausalLM.from_pretrained()

LLMHandler.generate(prompt, temperature, max_tokens) → str
│   └─→ tokenizer(prompt)
│   └─→ with torch.no_grad():
│       └─→ model.generate(...)
│   └─→ tokenizer.decode(output)

LLMHandler.generate_streaming(prompt, ...) → Generator
│   └─→ TextIteratorStreamer()
│   └─→ Thread: model.generate()
│   └─→ yield token for each token generated

LLMHandler.format_prompt_with_context(query, context_items) → str
│   └─→ Create context string from items
│   └─→ base_prompt.format(context, query)
│   └─→ tokenizer.apply_chat_template()

LLMHandler.get_model_info() → Dict
│   └─→ Return model statistics
```

### RAGPipeline Functions

```
RAGPipeline.__init__(embedding_model, llm_model, load_llm)
│   ├─→ PDFProcessor()
│   ├─→ EmbeddingManager()
│   └─→ LLMHandler() [if load_llm=True]

RAGPipeline.process_pdf(pdf_path) → List[Dict]
│   └─→ pdf_processor.process_pdf(pdf_path)

RAGPipeline.embed_chunks(chunks) → List[Dict]
│   └─→ embedding_manager.embed_chunks(chunks)

RAGPipeline.setup_retriever(chunks, top_k)
│   └─→ SemanticRetriever(chunks, embedding_manager)

RAGPipeline.load_llm(model_id)
│   └─→ LLMHandler(model_id, ...)

RAGPipeline.retrieve(query, top_k) → List[Dict]
│   └─→ retriever.retrieve_with_metadata(query, top_k)

RAGPipeline.generate(query, context_chunks, ...) → str
│   └─→ llm_handler.format_prompt_with_context()
│   └─→ llm_handler.generate()

RAGPipeline.generate_streaming(query, context_chunks) → Generator
│   └─→ llm_handler.format_prompt_with_context()
│   └─→ for token in llm_handler.generate_streaming()

RAGPipeline.ask(query, top_k, ..., return_context) → str or (str, List)
│   └─→ retrieve(query, top_k)
│   └─→ generate(query, context_chunks)
│   └─→ return [answer, context] if return_context else answer

RAGPipeline.pipeline(pdf_path, query, save_embeddings) → Dict
│   ├─→ process_pdf(pdf_path)
│   ├─→ embed_chunks(chunks)
│   ├─→ If save_embeddings: embedding_manager.save_embeddings()
│   ├─→ setup_retriever(embedded_chunks)
│   └─→ If query: ask(query)

RAGPipeline.get_statistics() → Dict
│   └─→ Collect stats from all components
```

---

## 🔄 IMPORTANT SEQUENCES

### Sequence 1: FIRST TIME INITIALIZATION (10-20 minutes)
```
streamlit_app.py::initialize_pipeline()
    ↓
RAGPipeline.__init__(load_llm=True)
    ├─→ PDFProcessor() - instant
    ├─→ EmbeddingManager() - downloads ~400MB (1-2 min)
    └─→ LLMHandler() - downloads ~16GB (8-15 min)
```

### Sequence 2: PDF PROCESSING (2-5 minutes)
```
PDFProcessor.process_pdf()
    ├─→ extract_text_from_pdf() - 10-30 sec
    ├─→ split_into_sentences() - 20-30 sec
    ├─→ chunk_sentences() - 5-10 sec
    ├─→ create_chunks() - 5-10 sec
    └─→ filter_chunks() - <1 sec
```

### Sequence 3: EMBEDDING GENERATION (1-3 minutes)
```
EmbeddingManager.embed_chunks()
    └─→ model.encode(all_texts, batch_size=32)
        └─→ Process 100 chunks in ~32-32-36 batches
            └─→ Each batch: 1-2 seconds
```

### Sequence 4: QUERY PROCESSING (6-31 seconds)
```
RAGPipeline.ask()
    ├─→ retrieve() - 50-200ms
    │   └─→ Embed query + similarity search
    ├─→ generate() - 5-30 seconds
    │   └─→ LLM inference
    └─→ Return answer
```

---

## 🔌 DATA TRANSFORMATIONS

### After PDF Processing
```
Input: Raw PDF file
Output: List[Dict]
{
    "page_number": 0,
    "sentence_chunk": "Text...",
    "chunk_token_count": 45,
    "chunk_char_count": 200,
    "chunk_word_count": 35
}
```

### After Embedding
```
Input: List[Dict] chunks
Output: List[Dict] chunks WITH embeddings
{
    ...previous fields...,
    "embedding": numpy.ndarray(768,)  # 768-dimensional vector
}
```

### After Retrieval
```
Input: query (string)
Output: List[Dict] with scores
{
    ...chunk fields...,
    "similarity_score": 0.95  # Cosine similarity
}
(Sorted by similarity_score descending)
```

### After Generation
```
Input: prompt (string)
Output: answer (string)

Example:
"Based on the provided context, macronutrients are organic compounds..."
```

---

## ⚡ PERFORMANCE BOTTLENECKS

1. **LLM Loading** (~8-15 min): Model download & initialization
   - Solution: Load once, reuse in session

2. **PDF Processing** (~1-3 min): Text extraction & chunking
   - Solution: Process in background, cache results

3. **Embedding Generation** (~1-3 min): SentenceTransformer inference
   - Solution: Batch processing, GPU acceleration

4. **LLM Generation** (~5-30 sec): Token-by-token generation
   - Solution: Streaming output, quantization

5. **Similarity Search** (~50-200ms): Vector dot product
   - Solution: Already optimized with torch

---

## 🎯 FUNCTION CALL DEPENDENCY GRAPH

```
streamlit_app.py (UI Entry Point)
    │
    ├─→ RAGPipeline (Orchestrator)
    │   ├─→ PDFProcessor
    │   │   ├─→ fitz (PyMuPDF)
    │   │   └─→ spacy.nlp
    │   ├─→ EmbeddingManager
    │   │   └─→ SentenceTransformer
    │   ├─→ SemanticRetriever
    │   │   └─→ torch ops (dot_score, topk)
    │   └─→ LLMHandler
    │       ├─→ AutoTokenizer
    │       └─→ AutoModelForCausalLM
    │
    └─→ Session State Management
        └─→ Chat History
```

---

## 🚀 EXECUTION MODES

### Mode 1: Full Pipeline (One-Shot)
```
RAGPipeline.pipeline(pdf_path, query)
    ├─→ PDF → Process
    ├─→ Chunks → Embed
    ├─→ Setup Retriever
    └─→ Answer Query
Duration: 3-10 minutes (first run) + 5-30 sec
```

### Mode 2: Separate Steps
```
RAGPipeline.process_pdf(pdf_path)
RAGPipeline.embed_chunks(chunks)
RAGPipeline.setup_retriever(chunks)
# ... later ...
RAGPipeline.ask(query)
```

### Mode 3: Pre-loaded Embeddings
```
Load embeddings from disk
RAGPipeline.setup_retriever(loaded_chunks)
# ... instant ...
RAGPipeline.ask(query)
Duration: 6-31 seconds per query
```

---

This documentation covers the complete function flow hierarchy and execution sequence!
