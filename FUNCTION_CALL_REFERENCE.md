# Function Call Graph & Dependencies

A detailed reference of all function calls, signatures, and how they relate to each other.

---

## Function Call Hierarchy

### Level 1: Entry Points (User Interface)

```
streamlit_app.py::main()
├─ Called at: startup
├─ Initializes: Session state, logging, configuration
└─ Renders: Web interface
```

### Level 2: User Actions

```
[ACTION 1] User uploads PDF
│
└─ streamlit_app.py::main() [Line 170-200]
   │
   └─ RAGPipeline.pipeline(pdf_path, save_embeddings=True)
      ├─ Returns: {"status": "success", "chunks_processed": 245, ...}
      └─ Side effect: Sets up retriever for queries


[ACTION 2] User asks question
│
└─ streamlit_app.py::main() [Line 245-270]
   │
   └─ RAGPipeline.ask(query, top_k=5, temperature=0.7, max_new_tokens=512, return_context=True)
      ├─ Returns: (answer_text, [context_chunks])
      └─ Side effect: Displays answer and context in UI
```

---

## Complete Call Graph

### PDF Upload & Processing Chain

```
main()
│
├─ PDFProcessor.__init__()
│  └─ Load spaCy English model with sentencizer
│
└─ RAGPipeline.pipeline(pdf_path)
   │
   ├─►  RAGPipeline.process_pdf(pdf_path)
   │    │
   │    └─► PDFProcessor.process_pdf(pdf_path)
   │        │
   │        ├─► PDFProcessor.extract_text_from_pdf(pdf_path)
   │        │   ├─ Open PDF with fitz (PyMuPDF)
   │        │   ├─ Iterate through all pages
   │        │   ├─ Extract text from each page
   │        │   └─ Return: [{"page_num": 0, "text": "..."}, ...]
   │        │
   │        ├─► PDFProcessor.text_formatter(text) [for each page]
   │        │   ├─ Replace newlines with spaces
   │        │   ├─ Remove extra whitespace
   │        │   └─ Return: cleaned text
   │        │
   │        ├─► PDFProcessor.split_text_into_sentences(text)
   │        │   ├─ Use spaCy nlp(text).sents
   │        │   ├─ Extract sentence boundaries
   │        │   └─ Return: [sent1, sent2, ...]
   │        │
   │        └─► PDFProcessor.combine_sentences_into_chunks(sentences)
   │            ├─ Group sentences (SENTENCE_CHUNK_SIZE=10)
   │            ├─ Add token counts (via tokenizer)
   │            ├─ Filter by MIN_CHUNK_TOKENS
   │            └─ Return: [{"sentence_chunk": "...", "chunk_token_count": 25, "page_number": 0}, ...]
   │
   ├─►  RAGPipeline.embed_chunks(chunks)
   │    │
   │    └─► EmbeddingManager.embed_chunks(chunks)
   │        │
   │        ├─► Extract texts: [chunk["sentence_chunk"] for chunk in chunks]
   │        │
   │        ├─► EmbeddingManager.generate_embeddings(texts, batch_size=32)
   │        │   │
   │        │   ├─ Load model: SentenceTransformer('all-mpnet-base-v2')
   │        │   ├─ Encode texts in batches
   │        │   │   └─ Each text → 768-dimensional vector
   │        │   └─ Return: np.array shape (num_texts, 768)
   │        │
   │        ├─► Add embeddings to chunks:
   │        │   for i, chunk in enumerate(chunks):
   │        │       chunk["embedding"] = embeddings[i]
   │        │
   │        └─ Return: chunks (with "embedding" field added)
   │
   └─►  RAGPipeline.setup_retriever(chunks, top_k=5)
        │
        └─► SemanticRetriever.__init__(chunks_with_embeddings, embedding_manager, config)
            │
            ├─► Store chunks and embedding manager
            │
            └─► SemanticRetriever._prepare_embeddings()
                ├─ Extract "embedding" from each chunk
                ├─ Convert numpy arrays to torch tensors
                ├─ Stack into single tensor: shape (num_chunks, 768)
                └─ Store as self.embeddings
```

### Query & Answer Chain

```
main()
│
└─ RAGPipeline.ask(query, top_k=5, temperature=0.7, max_new_tokens=512, return_context=True)
   │
   ├─►  RAGPipeline.retrieve(query, top_k=5)
   │    │
   │    └─► SemanticRetriever.retrieve_with_metadata(query, top_k=5)
   │        │
   │        ├─► EmbeddingManager.generate_embeddings(query)
   │        │   ├─ Load same 'all-mpnet-base-v2' model
   │        │   ├─ Encode query text
   │        │   └─ Return: torch.Tensor shape (1, 768)
   │        │
   │        ├─► Calculate similarity:
   │        │   util.cos_sim(query_embedding, self.embeddings)
   │        │   └─ Return: scores shape (1, num_chunks)
   │        │
   │        ├─► Sort and select top-k:
   │        │   cos_sim[0].argsort(descending=True)[:top_k]
   │        │   └─ Return: indices of top 5 chunks
   │        │
   │        └─► Build result list:
   │            for idx in top_k_indices:
   │                chunk = self.chunks[idx].copy()
   │                chunk["similarity_score"] = cos_sim[0][idx].item()
   │                append to results
   │            └─ Return: [chunk_with_scores, ...]
   │
   └─►  RAGPipeline.generate(query, context_chunks, temperature=0.7, max_new_tokens=512)
        │
        ├─► LLMHandler.format_prompt_with_context(query, context_chunks)
        │   │
        │   ├─ Build context string:
        │   │  context_string = ""
        │   │  for i, chunk in enumerate(context_chunks):
        │   │      context_string += f"[Chunk {i} from Page {chunk['page_number']}]:\n{chunk['sentence_chunk']}\n"
        │   │
        │   └─ Return formatted prompt:
        │      f"""Use the following context to answer the question.
        │      
        │      Context:
        │      {context_string}
        │      
        │      Question: {query}
        │      
        │      Answer:"""
        │
        └─► LLMHandler.generate(prompt, temperature=0.7, max_new_tokens=512)
            │
            ├─ Validate API key (if not set, raise ValueError)
            │
            ├─► Call Groq API:
            │   self.client.chat.completions.create(
            │       model="llama-3.3-70b-versatile",
            │       messages=[{"role": "user", "content": prompt}],
            │       temperature=0.7,
            │       max_tokens=512,
            │       top_p=1.0
            │   )
            │   │
            │   ├─ HTTP POST to Groq servers
            │   ├─ Process by llama-3.3-70b-versatile
            │   └─ Return response object
            │
            ├─ Extract text:
            │  generated_text = response.choices[0].message.content
            │
            └─ Return: "This document is a comprehensive guide..."
```

---

## Function Signatures Reference

### RAGPipeline Class

```python
class RAGPipeline:
    
    def __init__(
        embedding_model: str = "all-mpnet-base-v2",
        groq_model: str = "llama-3.3-70b-versatile",
        device: str = "cpu",
        load_llm: bool = True
    ) -> None
    
    def process_pdf(self, pdf_path: str) -> List[Dict[str, Any]]
        # Returns: [{"sentence_chunk": "...", "chunk_token_count": 25, "page_number": 0}, ...]
    
    def embed_chunks(self, chunks: List[Dict]) -> List[Dict[str, Any]]
        # Returns: chunks with added "embedding" field (numpy array)
    
    def setup_retriever(self, chunks: List[Dict], top_k: int = 5) -> None
        # Side effect: Initializes self.retriever
    
    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]
        # Returns: [{"sentence_chunk": "...", "similarity_score": 0.92, ...}, ...]
    
    def generate(
        self,
        query: str,
        context_chunks: List[Dict],
        temperature: float = 0.7,
        max_new_tokens: int = 2048
    ) -> str
        # Returns: "This document is about..."
    
    def ask(
        self,
        query: str,
        top_k: int = 5,
        temperature: float = 0.7,
        max_new_tokens: int = 2048,
        return_context: bool = False
    ) -> Union[str, Tuple[str, List[Dict]]]
        # Returns: answer_text or (answer_text, context_chunks)
    
    def pipeline(
        self,
        pdf_path: str,
        query: str = None,
        save_embeddings: bool = True
    ) -> Dict[str, Any]
        # Returns: {"status": "success", "chunks_processed": 245, ...}
```

### PDFProcessor Class

```python
class PDFProcessor:
    
    def __init__(self) -> None
    
    @staticmethod
    def text_formatter(text: str) -> str
        # Returns: cleaned text (removes newlines, extra spaces)
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]
        # Returns: [{"page_num": 0, "text": "..."}, {"page_num": 1, "text": "..."}, ...]
    
    def process_pdf(self, pdf_path: str) -> List[Dict[str, Any]]
        # Returns: [{"sentence_chunk": "...", "chunk_token_count": 25, "page_number": 0}, ...]
```

### EmbeddingManager Class

```python
class EmbeddingManager:
    
    def __init__(
        model_name: str = "all-mpnet-base-v2",
        device: str = "cpu"
    ) -> None
    
    def generate_embeddings(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        convert_to_tensor: bool = True,
        convert_to_numpy: bool = False,
        show_progress_bar: bool = True
    ) -> Union[np.ndarray, torch.Tensor]
        # Returns: array of shape (num_texts, 768)
    
    def embed_chunks(
        self,
        chunks: List[Dict]
    ) -> List[Dict[str, Any]]
        # Returns: chunks with "embedding" field added
```

### SemanticRetriever Class

```python
class SemanticRetriever:
    
    def __init__(
        chunks_with_embeddings: List[Dict],
        embedding_manager: EmbeddingManager,
        config: RetrieverConfig = None
    ) -> None
    
    def retrieve(
        self,
        query: str,
        top_k: int = None,
        return_scores: bool = True,
        print_time: bool = False
    ) -> Tuple[List[Dict], List[float]]
        # Returns: ([chunks], [scores])
    
    def retrieve_with_metadata(
        self,
        query: str,
        top_k: int = None
    ) -> List[Dict[str, Any]]
        # Returns: [{"sentence_chunk": "...", "similarity_score": 0.92, "page_number": 0}, ...]
```

### LLMHandler Class

```python
class LLMHandler:
    
    def __init__(
        model_id: str = "llama-3.3-70b-versatile",
        api_key: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> None
        # Raises: ValueError if api_key is not provided
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        **kwargs
    ) -> str
        # Returns: generated text
        # Raises: RuntimeError if API call fails
    
    def generate_streaming(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        **kwargs
    ) -> Generator[str, None, None]
        # Yields: text chunks as they stream from API
    
    def format_prompt_with_context(
        self,
        query: str,
        context_chunks: List[Dict]
    ) -> str
        # Returns: formatted prompt string with context
    
    def get_model_info(self) -> Dict[str, Any]
        # Returns: {"model_id": "...", "provider": "Groq Cloud API", ...}
```

---

## Data Flow Types

### Chunk Structure

```python
# After PDFProcessor.process_pdf()
chunk = {
    "sentence_chunk": "The quick brown fox jumps over the lazy dog.",
    "chunk_token_count": 12,
    "page_number": 0
}

# After EmbeddingManager.embed_chunks()
chunk = {
    "sentence_chunk": "The quick brown fox jumps over the lazy dog.",
    "chunk_token_count": 12,
    "page_number": 0,
    "embedding": np.array([0.123, -0.456, ..., 0.042])  # 768 dimensions
}

# After SemanticRetriever.retrieve_with_metadata()
retrieved_chunk = {
    "sentence_chunk": "The quick brown fox jumps over the lazy dog.",
    "chunk_token_count": 12,
    "page_number": 0,
    "embedding": np.array([0.123, -0.456, ..., 0.042]),
    "similarity_score": 0.92  # Added by retriever
}
```

### Response Types

```python
# LLMHandler.generate() returns
answer: str
# "This document is a comprehensive guide to artificial intelligence,
#  covering machine learning, deep learning, and practical applications."

# RAGPipeline.retrieve() returns
context_chunks: List[Dict[str, Any]]
# [
#     {"sentence_chunk": "...", "similarity_score": 0.92, "page_number": 0},
#     {"sentence_chunk": "...", "similarity_score": 0.87, "page_number": 1},
#     ...  (5 total)
# ]

# RAGPipeline.ask() with return_context=True returns
answer, context = Tuple[str, List[Dict]]
```

---

## Error Handling Flow

```
Error Scenarios & Handling:

1. API Key Missing
   LLMHandler.__init__()
   └─ if not api_key:
      └─ raise ValueError("GROQ_API_KEY is required...")


2. PDF File Not Found
   PDFProcessor.extract_text_from_pdf()
   └─ if not pdf_path.exists():
      └─ raise FileNotFoundError(...)


3. PDF File Too Large
   PDFProcessor.extract_text_from_pdf()
   └─ if file_size > MAX_PDF_SIZE_BYTES:
      └─ raise ValueError(...)


4. Retriever Not Initialized
   RAGPipeline.retrieve()
   └─ if self.retriever is None:
      └─ raise RuntimeError("Retriever not initialized...")


5. LLM Not Loaded
   RAGPipeline.generate()
   └─ if self.llm_handler is None:
      └─ raise RuntimeError("LLM not loaded...")


6. Groq API Error
   LLMHandler.generate()
   └─ try:
         response = self.client.chat.completions.create(...)
      except Exception as e:
         raise RuntimeError(f"Groq API error: {str(e)}")


7. All errors caught and logged
   Every function wraps operations in try/except
   └─ logger.error(f"Error: {str(e)}")
```

---

## Dependency Relationships

```
streamlit_app.py (Entry Point)
│
├─ Imports: RAGPipeline, PDFProcessor, EmbeddingManager
│
├─ Depends on: config.settings (configuration)
│
└─ Creates: RAGPipeline instance


RAGPipeline (Orchestrator)
│
├─ Contains: PDFProcessor, EmbeddingManager, SemanticRetriever, LLMHandler
│
├─ PDFProcessor
│  └─ Depends on: spacy, fitz (PyMuPDF), regex
│
├─ EmbeddingManager
│  └─ Depends on: sentence_transformers, torch
│
├─ SemanticRetriever
│  ├─ Depends on: numpy, torch, EmbeddingManager
│  └─ Uses: sentence_transformers.util for cosine similarity
│
└─ LLMHandler
   └─ Depends on: groq (Groq API client)


All modules depend on:
└─ config.settings (centralized configuration)
```

---

## Call Sequence Summary

### PDF Upload (User clicks "Upload PDF")
```
1. Streamlit detects file upload
2. Save file to disk
3. RAGPipeline.pipeline() called
   3.1. PDFProcessor.process_pdf()
        ├─ Extract text from each page
        ├─ Clean and format
        ├─ Split into sentences
        └─ Combine into chunks
   3.2. EmbeddingManager.embed_chunks()
        ├─ Load embedding model
        └─ Generate 768-dim embeddings
   3.3. SemanticRetriever initialized with chunks + embeddings
4. Return success to UI
5. Render confirmation message
```

### Query Processing (User types question & clicks "Ask")
```
1. Streamlit receives query
2. RAGPipeline.ask() called
   2.1. SemanticRetriever.retrieve_with_metadata()
        ├─ Generate embedding for query
        ├─ Calculate similarity with all chunks
        └─ Return top-5 chunks
   2.2. LLMHandler.format_prompt_with_context()
        └─ Create prompt with retrieved context
   2.3. LLMHandler.generate()
        ├─ Call Groq API
        ├─ Receive generated answer
        └─ Return text
3. Return answer + context chunks to UI
4. Display answer and optional context
5. Add to chat history
6. Rerun UI with updated messages
```

---

## Performance Notes

- **Embedding Generation**: O(n) where n = number of chunks (~1-2 seconds for 200 chunks)
- **Similarity Search**: O(n) matrix multiplication, very fast with GPU (~50-100ms)
- **API Call**: Depends on Groq servers (~500-2000ms typically)
- **Total Query**: ~700-2500ms end-to-end

---

## Key Design Patterns

1. **Pipeline Pattern**: RAGPipeline orchestrates entire workflow
2. **Component Separation**: Each task has dedicated class
3. **Lazy Initialization**: LLM loaded only when needed
4. **Configuration Centralization**: All settings in config.settings
5. **Error Handling**: Try-except-log pattern throughout
6. **Logging**: Every major operation logged for debugging

