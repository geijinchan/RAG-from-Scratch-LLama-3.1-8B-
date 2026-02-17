# RAG System - Function Reference & Call Matrix

## 📍 WHERE IS EACH FUNCTION?

### Core Modules (src/)

| Module | File | Functions | Purpose |
|--------|------|-----------|---------|
| **PDFProcessor** | `src/pdf_processor.py` | `process_pdf()`, `extract_text_from_pdf()`, `split_into_sentences()`, `chunk_sentences()`, `create_chunks()`, `filter_chunks()` | Convert PDF → text → chunks |
| **EmbeddingManager** | `src/embedding_manager.py` | `generate_embeddings()`, `embed_chunks()`, `save_embeddings()`, `load_embeddings()`, `get_embedding_dimension()` | Create & manage embeddings |
| **SemanticRetriever** | `src/retrieval.py` | `retrieve()`, `retrieve_with_metadata()`, `search_by_page()`, `update_chunks()`, `add_chunks()`, `get_chunk_statistics()` | Semantic search |
| **LLMHandler** | `src/llm_handler.py` | `generate()`, `generate_streaming()`, `format_prompt_with_context()`, `get_model_info()` | LLM inference |
| **RAGPipeline** | `src/rag_pipeline.py` | `process_pdf()`, `embed_chunks()`, `setup_retriever()`, `load_llm()`, `retrieve()`, `generate()`, `ask()`, `pipeline()` | Main orchestrator |

### Web Interface (app/)

| Module | File | Functions | Purpose |
|--------|------|-----------|---------|
| **Streamlit App** | `app/streamlit_app.py` | `initialize_pipeline()`, `display_pdf_upload()`, `display_chat_interface()`, `display_settings()` | User interface |

### Configuration (config/)

| Module | File | Variables | Purpose |
|--------|------|-----------|---------|
| **Settings** | `config/settings.py` | `HUGGINGFACE_TOKEN`, `EMBEDDING_MODEL`, `LLM_MODEL_ID`, `DEVICE`, etc. | Environment configuration |

---

## 🔗 FUNCTION CALL CHAINS

### CHAIN 1: PDF Upload Flow

```
streamlit_app.py::main()
└─ st.file_uploader() [User uploads PDF]
   ├─ initialize_pipeline() [First run only]
   │  └─ RAGPipeline.__init__()
   │     ├─ PDFProcessor.__init__()
   │     ├─ EmbeddingManager.__init__()
   │     └─ LLMHandler.__init__() [Takes 10-15 min]
   │
   └─ RAGPipeline.pipeline(pdf_path, save_embeddings=True)
      ├─ PDFProcessor.process_pdf()
      │  ├─ extract_text_from_pdf()
      │  ├─ split_into_sentences()
      │  ├─ chunk_sentences()
      │  ├─ create_chunks()
      │  └─ filter_chunks()
      │
      ├─ RAGPipeline.embed_chunks(chunks)
      │  └─ EmbeddingManager.embed_chunks()
      │     └─ SentenceTransformer.encode() [For each batch]
      │
      ├─ EmbeddingManager.save_embeddings(chunks, filename)
      │  ├─ pickle.dump(chunks)
      │  └─ json.dump(metadata)
      │
      └─ RAGPipeline.setup_retriever(chunks)
         └─ SemanticRetriever.__init__()
            └─ _prepare_embeddings() [Convert to torch tensors]
```

**Total Duration:** 2-5 minutes per PDF (excluding model downloads)

---

### CHAIN 2: Query Processing Flow

```
streamlit_app.py::chat_interface()
└─ st.text_input() [User enters query]
   └─ st.button("Ask") [User clicks Ask]
      └─ RAGPipeline.ask(query, top_k=5, temperature=0.7)
         │
         ├─ RAGPipeline.retrieve(query, top_k)
         │  └─ SemanticRetriever.retrieve_with_metadata(query, top_k)
         │     ├─ EmbeddingManager.generate_embeddings(query)
         │     │  └─ SentenceTransformer.encode(query)
         │     │
         │     ├─ torch.nn.functional.dot_score(query_emb, chunk_embeddings)
         │     │
         │     └─ torch.topk(scores, k=top_k)
         │
         ├─ RAGPipeline.generate(query, context_chunks, temperature)
         │  ├─ LLMHandler.format_prompt_with_context(query, chunks)
         │  │  └─ tokenizer.apply_chat_template()
         │  │
         │  └─ LLMHandler.generate(prompt, temperature, max_tokens)
         │     ├─ tokenizer(prompt)
         │     ├─ model.generate()
         │     │  └─ [Iterative token generation loop]
         │     │
         │     └─ tokenizer.decode(output)
         │
         └─ Return (answer, context_chunks)
            └─ Display in Streamlit

         [Optional] RAGPipeline.generate_streaming()
         └─ For streaming/real-time token output
```

**Total Duration:** 50ms (retrieval) + 5-30 sec (generation) = 5.05-30.05 seconds

---

## 📊 DETAILED MODULE INTERACTIONS

### Module: PDFProcessor

**File:** `src/pdf_processor.py`

```python
class PDFProcessor:
    def __init__(self):
        """Initialize spaCy NLP pipeline for sentence splitting"""
        # nlp = spacy.load("en_core_web_sm")
        # nlp.add_pipe("sentencizer")
    
    def process_pdf(pdf_path: str) -> List[Dict]:
        """MAIN ORCHESTRATOR - Combines all steps"""
        pages_and_texts = extract_text_from_pdf(pdf_path)
        pages_and_texts = split_into_sentences(pages_and_texts)
        pages_and_texts = chunk_sentences(pages_and_texts)
        pages_and_chunks = create_chunks(pages_and_texts)
        chunks = filter_chunks(pages_and_chunks)
        return chunks
    
    def extract_text_from_pdf(pdf_path: str) -> List[Dict]:
        """Extract text from each PDF page"""
        # fitz.open(pdf_path)
        # for page in doc: page.get_text()
        return pages_and_texts
    
    def split_into_sentences(pages_and_texts) -> List[Dict]:
        """Use spaCy to split into sentences"""
        # nlp(text) → doc.sents
        return pages_and_texts_with_sentences
    
    def chunk_sentences(pages_and_texts) -> List[Dict]:
        """Group sentences into chunks of N (default: 10)"""
        # _split_list(sentences, chunk_size=10)
        return pages_and_sentence_chunks
    
    def create_chunks(pages_and_texts) -> List[Dict]:
        """Create chunk dictionaries with metadata"""
        # Calculate token count, char count, word count
        # Join sentences with spaces
        return chunks
    
    def filter_chunks(chunks) -> List[Dict]:
        """Remove chunks below minimum token threshold"""
        # Filter: token_count >= MIN_CHUNK_TOKENS (30)
        return filtered_chunks
```

**Dependencies:**
- PyMuPDF (fitz)
- spaCy NLP
- tiktoken (for token counting)
- pandas (for dataframe operations)

**Called By:**
- `RAGPipeline.process_pdf()`
- `RAGPipeline.pipeline()`

**Calls:**
- Internal helper methods
- No external module calls

---

### Module: EmbeddingManager

**File:** `src/embedding_manager.py`

```python
class EmbeddingManager:
    def __init__(model_name: str = "all-mpnet-base-v2", device: str = "cuda"):
        """Load SentenceTransformer embedding model"""
        # self.model = SentenceTransformer(model_name, device=device)
        # Downloads ~400MB on first run
    
    def generate_embeddings(texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for list of texts"""
        # self.model.encode(texts, batch_size=batch_size, convert_to_tensor=True)
        return embeddings_array  # Shape: (N, 768)
    
    def embed_chunks(chunks: List[Dict], batch_size: int = 32) -> List[Dict]:
        """Generate embeddings and attach to chunks"""
        # Extract text from chunks
        # Call generate_embeddings()
        # Attach embedding to each chunk
        return chunks_with_embeddings
    
    def save_embeddings(chunks: List[Dict], filename: str):
        """Save chunks and embeddings to disk"""
        # pickle.dump(chunks, f"embeddings.pkl")
        # json.dump(metadata, f"embeddings_metadata.json")
    
    def load_embeddings(embeddings_path: str) -> List[Dict]:
        """Load chunks and embeddings from disk"""
        # pickle.load(f"embeddings.pkl")
        return chunks_with_embeddings
    
    def get_embedding_dimension() -> int:
        """Get embedding vector size"""
        # return self.model.get_sentence_embedding_dimension()  # Usually 768
        return 768
```

**Dependencies:**
- SentenceTransformers
- PyTorch
- NumPy
- pickle (for serialization)

**Called By:**
- `RAGPipeline.embed_chunks()`
- `SemanticRetriever.__init__()`
- `SemanticRetriever.retrieve_with_metadata()` (for query embedding)

**Calls:**
- `SentenceTransformer.encode()`
- File I/O operations

---

### Module: SemanticRetriever

**File:** `src/retrieval.py`

```python
class RetrieverConfig:
    """Configuration dataclass for retrieval parameters"""
    top_k: int = 5
    similarity_threshold: float = 0.0
    # ... more parameters

class SemanticRetriever:
    def __init__(chunks: List[Dict], embedding_manager, config: RetrieverConfig):
        """Initialize retriever with pre-computed embeddings"""
        # self._prepare_embeddings()  # Convert numpy → torch tensors
        # self.chunk_embeddings = torch.tensor(embeddings)
    
    def retrieve(query: str, top_k: int) -> Tuple[List[Dict], List[float]]:
        """Core retrieval function"""
        # query_embedding = embedding_manager.generate_embeddings(query)
        # scores = torch.nn.functional.dot_score(query_emb, self.chunk_embeddings)
        # top_indices = torch.topk(scores, k=top_k).indices
        return top_chunks, scores
    
    def retrieve_with_metadata(query: str, top_k: int) -> List[Dict]:
        """Retrieve and attach similarity scores to chunks"""
        # top_chunks, scores = retrieve(query, top_k)
        # Attach 'similarity_score' field to each chunk
        return chunks_with_scores  # Sorted by score descending
    
    def search_by_page(query: str, page_number: int, top_k: int) -> List[Dict]:
        """Retrieve only chunks from specific page"""
        # retrieve_with_metadata() → filter by page_number
        return page_specific_chunks
    
    def update_chunks(new_chunks: List[Dict]):
        """Replace chunks and rebuild embeddings tensor"""
        # Recalculate embedding tensor
        # self.chunks = new_chunks
        # self.chunk_embeddings = torch.tensor(new_embeddings)
    
    def add_chunks(new_chunks: List[Dict]):
        """Add new chunks to existing set"""
        # Extend chunks list
        # Append to embedding tensor
    
    def get_chunk_statistics() -> Dict:
        """Return statistics about chunks"""
        # Calculate min/max/avg token counts
        # Count chunks per page
        return stats_dict
```

**Dependencies:**
- PyTorch
- NumPy
- EmbeddingManager (instance)

**Called By:**
- `RAGPipeline.setup_retriever()`
- `RAGPipeline.retrieve()`

**Calls:**
- `embedding_manager.generate_embeddings()`
- `torch.nn.functional.dot_score()`
- `torch.topk()`

---

### Module: LLMHandler

**File:** `src/llm_handler.py`

```python
class LLMHandler:
    def __init__(model_id: str, device: str = "cuda", use_8bit: bool = False, use_4bit: bool = False):
        """Load tokenizer and model with optional quantization"""
        # self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        # self.model = AutoModelForCausalLM.from_pretrained(
        #     model_id,
        #     quantization_config=BitsAndBytesConfig(...),  # if use_8bit or use_4bit
        #     device_map="auto"
        # )
        # Downloads ~16GB on first run for Llama 3.1 8B
    
    def generate(prompt: str, temperature: float = 0.7, max_tokens: int = 512) -> str:
        """Generate text from prompt"""
        # input_ids = self.tokenizer(prompt, return_tensors="pt")
        # with torch.no_grad():
        #     output_ids = self.model.generate(
        #         input_ids,
        #         max_new_tokens=max_tokens,
        #         temperature=temperature,
        #         do_sample=True
        #     )
        # answer = self.tokenizer.decode(output_ids)
        return answer_text
    
    def generate_streaming(prompt: str, ...) -> Generator:
        """Generate text token-by-token for streaming"""
        # streamer = TextIteratorStreamer(self.tokenizer)
        # Thread: self.model.generate(..., streamer=streamer)
        # for token in streamer:
        #     yield token
        yield token  # Yields each token as it's generated
    
    def format_prompt_with_context(query: str, context_items: List[Dict]) -> str:
        """Format query and context into prompt for LLM"""
        # Extract text from context_items
        # Combine with system prompt template
        # Apply tokenizer.apply_chat_template()
        # Add special tokens for chat format
        return formatted_prompt_string
    
    def get_model_info() -> Dict:
        """Get model statistics"""
        # Return model name, parameter count, vocab size, config
        return {
            "model_name": self.model_id,
            "num_parameters": self.model.num_parameters(),
            "vocab_size": self.tokenizer.vocab_size,
            # ... more fields
        }
```

**Dependencies:**
- Transformers
- PyTorch
- bitsandbytes (for quantization)

**Called By:**
- `RAGPipeline.load_llm()`
- `RAGPipeline.generate()`
- `RAGPipeline.generate_streaming()`

**Calls:**
- `AutoTokenizer.from_pretrained()`
- `AutoModelForCausalLM.from_pretrained()`
- `model.generate()`
- `tokenizer.decode()`

---

### Module: RAGPipeline (Main Orchestrator)

**File:** `src/rag_pipeline.py`

```python
class RAGPipeline:
    def __init__(embedding_model: str, llm_model_id: str, load_llm: bool = False):
        """Initialize all components"""
        # self.pdf_processor = PDFProcessor()
        # self.embedding_manager = EmbeddingManager(embedding_model)
        # self.llm_handler = None  # Lazy load if load_llm=True
        # self.retriever = None
    
    def process_pdf(pdf_path: str) -> List[Dict]:
        """Step 1: Process PDF"""
        # return self.pdf_processor.process_pdf(pdf_path)
        return chunks
    
    def embed_chunks(chunks: List[Dict]) -> List[Dict]:
        """Step 2: Generate embeddings"""
        # return self.embedding_manager.embed_chunks(chunks)
        return chunks_with_embeddings
    
    def setup_retriever(chunks: List[Dict], top_k: int = 5):
        """Step 3: Initialize retriever"""
        # self.retriever = SemanticRetriever(
        #     chunks,
        #     self.embedding_manager,
        #     RetrieverConfig(top_k=top_k)
        # )
    
    def load_llm(model_id: str):
        """Step 4: Load LLM (lazy initialization)"""
        # self.llm_handler = LLMHandler(model_id)
    
    def retrieve(query: str, top_k: int) -> List[Dict]:
        """Retrieve context for query"""
        # return self.retriever.retrieve_with_metadata(query, top_k)
        return context_chunks
    
    def generate(query: str, context_chunks: List[Dict], temperature: float = 0.7) -> str:
        """Generate answer given query and context"""
        # prompt = self.llm_handler.format_prompt_with_context(query, context_chunks)
        # answer = self.llm_handler.generate(prompt, temperature=temperature)
        return answer
    
    def generate_streaming(query: str, context_chunks, ...) -> Generator:
        """Generate answer with streaming"""
        # prompt = self.llm_handler.format_prompt_with_context(query, context_chunks)
        # for token in self.llm_handler.generate_streaming(prompt):
        #     yield token
        yield token
    
    def ask(query: str, top_k: int = 5, temperature: float = 0.7, return_context: bool = True):
        """Single-call RAG: retrieve + generate"""
        # context = self.retrieve(query, top_k)
        # answer = self.generate(query, context, temperature)
        if return_context:
            return answer, context
        else:
            return answer
    
    def pipeline(pdf_path: str, query: str = None, save_embeddings: bool = False) -> Dict:
        """COMPLETE END-TO-END PIPELINE"""
        # Step 1: Process PDF
        chunks = self.process_pdf(pdf_path)
        
        # Step 2: Generate embeddings
        embedded_chunks = self.embed_chunks(chunks)
        
        # Step 3: Save embeddings (optional)
        if save_embeddings:
            self.embedding_manager.save_embeddings(embedded_chunks, filename)
        
        # Step 4: Setup retriever
        self.setup_retriever(embedded_chunks)
        
        # Step 5: Process query (optional)
        if query:
            answer, context = self.ask(query)
            return {
                "status": "success",
                "answer": answer,
                "context": context,
                "num_chunks": len(chunks)
            }
        else:
            return {
                "status": "success",
                "message": "PDF processed successfully",
                "num_chunks": len(chunks)
            }
    
    def get_statistics() -> Dict:
        """Aggregate statistics from all components"""
        # Collect stats from pdf_processor, embedding_manager, retriever, llm_handler
        return stats_dict
```

**Dependencies:**
- All other src modules

**Called By:**
- `streamlit_app.py` (main entry point)

**Calls:**
- `PDFProcessor.process_pdf()`
- `EmbeddingManager.embed_chunks()`
- `SemanticRetriever.__init__()`
- `LLMHandler.generate()`

---

## 🎯 QUICK LOOKUP: "Where is function X?"

| Function | File | Called By | Calls |
|----------|------|-----------|-------|
| `process_pdf()` | PDFProcessor | RAGPipeline | extract_text, split_sentences, chunk, create, filter |
| `extract_text_from_pdf()` | PDFProcessor | process_pdf | PyMuPDF (fitz) |
| `split_into_sentences()` | PDFProcessor | process_pdf | spacy.nlp |
| `generate_embeddings()` | EmbeddingManager | embed_chunks, retrieve | SentenceTransformer.encode |
| `embed_chunks()` | EmbeddingManager | RAGPipeline | generate_embeddings |
| `retrieve()` | SemanticRetriever | retrieve_with_metadata | dot_score, topk |
| `retrieve_with_metadata()` | SemanticRetriever | RAGPipeline.retrieve | retrieve, embedding generation |
| `format_prompt_with_context()` | LLMHandler | RAGPipeline.generate | tokenizer.apply_chat_template |
| `generate()` | LLMHandler | RAGPipeline.generate | model.generate, tokenizer |
| `ask()` | RAGPipeline | Streamlit app | retrieve, generate |
| `pipeline()` | RAGPipeline | Streamlit app | All steps in sequence |

---

## ⏱️ TIMING BREAKDOWN

### First Run (10-20 minutes total)
```
Model Download:        10-15 minutes
  ├─ SentenceTransformer: 1-2 min
  └─ Llama 3.1 8B:     8-15 min

PDF Processing:        1-5 minutes
  ├─ PDF extraction:   10-30 sec
  ├─ Sentence split:   20-30 sec
  ├─ Chunking:         5-10 sec
  ├─ Embedding:        1-3 min
  └─ Retriever setup:  <1 sec

Total per query:       5-30 seconds
```

### Subsequent Runs
```
PDF Upload & Process:  2-5 minutes
Query & Answer:        6-31 seconds
```

---

## 🔄 EXECUTION EXAMPLES

### Example 1: Full Pipeline (One Statement)

```python
from src.rag_pipeline import RAGPipeline

# Initialize (first run: 15 min, subsequent: instant)
pipeline = RAGPipeline(
    embedding_model="all-mpnet-base-v2",
    llm_model_id="meta-llama/Meta-Llama-3.1-8B-Instruct",
    load_llm=True
)

# Full pipeline (2-5 min + query time)
result = pipeline.pipeline(
    pdf_path="documents/biology.pdf",
    query="What are macronutrients?",
    save_embeddings=True
)
# Returns: {
#     "status": "success",
#     "answer": "Macronutrients are...",
#     "context": [chunks with scores],
#     "num_chunks": 234
# }
```

### Example 2: Step-by-Step

```python
# Process PDF
chunks = pipeline.process_pdf("documents/biology.pdf")  # 1-3 min
print(f"Created {len(chunks)} chunks")

# Generate embeddings
embedded_chunks = pipeline.embed_chunks(chunks)  # 1-3 min

# Setup retriever
pipeline.setup_retriever(embedded_chunks)  # <1 sec

# Ask multiple questions
answer1, context1 = pipeline.ask("What are proteins?")  # 5-30 sec
answer2, context2 = pipeline.ask("List carbohydrates")  # 5-30 sec
answer3, context3 = pipeline.ask("Define fats")        # 5-30 sec
```

### Example 3: Pre-loaded Embeddings

```python
# Load previously saved embeddings (instant)
chunks = pipeline.embedding_manager.load_embeddings("embeddings.pkl")  # <1 sec

# Setup retriever
pipeline.setup_retriever(chunks)  # <1 sec

# Ask questions (no re-embedding needed)
answer, context = pipeline.ask("What are macronutrients?")  # 5-30 sec
```

---

This guide provides a complete map of where every function is located and how it's called!
