# Code Flow - Quick Visual Reference Card

Fast visual reference for understanding the code flow at a glance.

---

## 🎯 Main Flows in One Page

### Flow 1: Upload PDF (5 Steps)

```
┌──────────────┐
│  Upload PDF  │
└──────┬───────┘
       │
       ▼
┌─────────────────────────┐
│ Save File               │
│ initialize_pipeline()   │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ PDFProcessor            │
│ ├─ Open PDF (fitz)      │
│ ├─ Extract text         │
│ ├─ Format & clean       │
│ ├─ Split sentences      │
│ └─ Group into chunks    │
│                         │
│ RESULT: 245 chunks      │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ EmbeddingManager        │
│ ├─ Load model           │
│ ├─ Embed each chunk     │
│ │  (768-dim vectors)    │
│ └─ Store embeddings     │
│                         │
│ RESULT: chunks + vecs   │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ SemanticRetriever       │
│ ├─ Store embeddings     │
│ ├─ Prepare search index │
│ └─ Ready for queries    │
│                         │
│ STATUS: ✅ Ready        │
└─────────────────────────┘
```

### Flow 2: Ask Question (4 Steps)

```
┌──────────────┐
│  User Query  │
│ "What is     │
│  this about?"│
└──────┬───────┘
       │
       ▼
┌──────────────────────────┐
│ Embed Query              │
│ ├─ Use same model        │
│ └─ Get 768-dim vector    │
│                          │
│ RESULT: [0.23, -0.56...]│
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Find Similar Chunks      │
│ ├─ Cosine similarity     │
│ ├─ Sort by score         │
│ └─ Get top-5             │
│                          │
│ RESULT: [chunk1, chunk2] │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Format Prompt            │
│ ├─ Add context chunks    │
│ ├─ Add user query        │
│ └─ Create prompt string  │
│                          │
│ RESULT: formatted prompt │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Groq API Call            │
│ ├─ Model: llama-3.3-70b  │
│ ├─ Temperature: 0.7      │
│ ├─ Max tokens: 512       │
│ └─ Get response          │
│                          │
│ RESULT: answer text      │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Display Results          │
│ ├─ Answer                │
│ ├─ Context (optional)    │
│ ├─ Similarity scores     │
│ └─ Update chat history   │
└──────────────────────────┘
```

---

## 🔄 Component Interactions

```
                    ┌──────────────────────┐
                    │  streamlit_app.py    │
                    │  (Web UI)            │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼──────────┐
                    │  RAGPipeline        │
                    │  (Orchestrator)     │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
   ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
   │PDFProcessor │    │Embedding     │    │Semantic         │
   │             │    │Manager       │    │Retriever        │
   │- Read PDF   │    │              │    │                 │
   │- Extract    │    │- Load model  │    │- Store chunks   │
   │  text       │    │- Generate    │    │- Find similar   │
   │- Chunk      │    │  embeddings  │    │  chunks         │
   └─────────────┘    └──────────────┘    └─────────────────┘
                             ▲
                             │ uses
                             │
                      ┌──────┴───────┐
                      │              │
                      ▼              ▼
                   ┌─────────┐   ┌──────────────┐
                   │all-mpnet│   │ Embedding    │
                   │base-v2  │   │ Manager      │
                   │(model)  │   │ (generates)  │
                   └─────────┘   └──────────────┘

                    ┌──────────────┐
                    │ LLMHandler   │
                    │              │
                    │- Format      │
                    │  prompt with │
                    │  context     │
                    │- Call Groq   │
                    │  API         │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Groq Cloud   │
                    │ API          │
                    │              │
                    │llama-3.3-70b │
                    └──────────────┘
```

---

## 📊 Data Transformations

### Upload Path

```
PDF File (document.pdf)
         │
         ├─→ Pages [0-50] ──→ [Text 0, Text 1, ...] ──→ Clean text
         │
         ├─→ Chunks ──→ [Sentence 1-10, Sent 11-20, ...]
         │
         ├─→ Embeddings ──→ [Vec(768), Vec(768), ...] (245 vectors)
         │
         └─→ Retriever ──→ Ready for similarity search
```

### Query Path

```
User Query: "What is this?"
         │
         ├─→ Embed: [0.23, -0.56, ..., 0.04] (768-dim)
         │
         ├─→ Similarity: [0.92, 0.87, 0.78, 0.65, 0.61, ...] (vs all chunks)
         │
         ├─→ Top-5 chunks: [(chunk₂, 0.92), (chunk₀, 0.87), ...]
         │
         ├─→ Prompt: "Context:\n[Top chunks]\n\nQuestion: What is this?\n\nAnswer:"
         │
         ├─→ Groq API: Process with llama-3.3-70b
         │
         └─→ Response: "This document is about..." (512 tokens max)
```

---

## ⏱️ Timing Breakdown

### PDF Upload
```
Extraction:        100ms  ◼
Cleaning:          100ms  ◼
Chunking:          200ms  ◼◼
Embedding:        1500ms  ◼◼◼◼◼◼◼◼◼◼◼◼◼◼◼
Retriever setup:   100ms  ◼
                  ─────────────
TOTAL:           2000ms  (2 seconds typical)
```

### Query Processing
```
Embed query:       100ms  ◼
Find similar:      100ms  ◼
Format prompt:      50ms  
Groq API call:    1000ms  ◼◼◼◼◼◼◼◼◼◼
Display:           100ms  ◼
                  ─────────────
TOTAL:           1350ms  (1-2 seconds typical)
```

---

## 🗂️ File Organization

```
RAG System
│
├── 📱 Web UI
│   └── app/streamlit_app.py
│
├── 🧠 Core Logic
│   └── src/rag_pipeline.py (orchestrator)
│
├── 📄 Components
│   ├── src/pdf_processor.py (PDF → chunks)
│   ├── src/embedding_manager.py (text → vectors)
│   ├── src/retrieval.py (similarity search)
│   └── src/llm_handler.py (Groq API)
│
├── ⚙️ Configuration
│   └── config/settings.py (all settings)
│
└── 🧪 Tests
    ├── tests/test_llm_handler_groq.py
    ├── tests/test_rag_pipeline.py
    ├── tests/test_retrieval.py
    └── ...
```

---

## 🔑 Key Variables & Types

```
Chunk:
  {
    "sentence_chunk": str,          # The text
    "chunk_token_count": int,       # Number of tokens
    "page_number": int,             # Which page
    "embedding": np.array(768),     # Vector representation
    "similarity_score": float        # (added during retrieval)
  }

Query Embedding:
  torch.Tensor(1, 768)              # Single query vector

Similarity Scores:
  [0.92, 0.87, 0.78, 0.65, 0.61]  # Relationship to all chunks

Generated Answer:
  str                               # Response from Groq API
```

---

## 🔍 Critical Check Points

When debugging, check these in order:

```
❓ PDF not uploading?
  ↓
  → streamlit_app.py line 170: file_uploader check
  → PDFProcessor.process_pdf() returning chunks?
  
❓ No search results?
  ↓
  → EmbeddingManager loaded model?
  → Embeddings generated correctly? (shape should be 245×768)
  → SemanticRetriever initialized with embeddings?
  
❓ Wrong answers from LLM?
  ↓
  → Correct chunks retrieved? (check similarity_score)
  → Prompt formatted correctly?
  → API key valid?
  → Groq API accessible?
  
❓ Slow performance?
  ↓
  → Check embedding generation time (should be <2s)
  → Check Groq API latency (monitor.groq.com)
  → Check retrieval similarity calc (should be <100ms)
```

---

## 🚀 Quick Execution Summary

### Step 1: Initialize
```python
pipeline = RAGPipeline(load_llm=True)
# Creates: PDFProcessor, EmbeddingManager, LLMHandler
# Time: ~100ms
```

### Step 2: Process PDF
```python
result = pipeline.pipeline(pdf_path="doc.pdf")
# Does: Extract → Chunk → Embed → Setup Retriever
# Time: ~2000ms
```

### Step 3: Answer Question
```python
answer, context = pipeline.ask("What is this?")
# Does: Embed Query → Find Similar → Format → Generate
# Time: ~1000-2000ms
```

---

## 📌 Function Quick Reference

| Function | Input | Output | Time |
|----------|-------|--------|------|
| `pipeline.pipeline()` | pdf_path | status dict | 2s |
| `pipeline.retrieve()` | query | [chunks] | 0.1s |
| `pipeline.generate()` | query, chunks | answer | 1s |
| `pipeline.ask()` | query | answer, chunks | 1.1s |
| `pdf_processor.process_pdf()` | pdf_path | [chunks] | 0.5s |
| `embedding_manager.embed_chunks()` | [chunks] | [chunks+vecs] | 1.5s |
| `retriever.retrieve_with_metadata()` | query | [top5_chunks] | 0.1s |
| `llm_handler.generate()` | prompt | answer | 1s |

---

## 🎯 Debug Template

When something doesn't work, trace it:

```
USER ACTION: [describe what they're trying to do]

EXPECTED FLOW:
1. Component A calls function X()
   └─ Input: [what goes in]
   └─ Output: [what should come out]
2. Component B receives output
   └─ Uses it for: [what operation]
3. Result displayed to user

ACTUAL BEHAVIOR:
[what happened instead]

CHECK:
- [ ] Log statements show where execution stopped
- [ ] Exception message indicates which function failed
- [ ] Input data is valid?
- [ ] Output data shape/type correct?
- [ ] Next component received correct input?
```

---

## 💡 Tips for Understanding

1. **Start from the UI** → Follow the click handler down
2. **Trace the data** → See how text becomes embeddings becomes answers
3. **Check the timing** → Profile each step to find bottlenecks
4. **Read the logs** → Every operation is logged
5. **Test each component** → Unit tests show expected behavior

---

## 📚 Related Documentation

- **[CODE_FLOW_EXPLANATION.md](CODE_FLOW_EXPLANATION.md)** - Detailed flow with examples
- **[FUNCTION_CALL_REFERENCE.md](FUNCTION_CALL_REFERENCE.md)** - Complete function signatures
- **[TEST_GUIDE.md](TEST_GUIDE.md)** - How to test each component
