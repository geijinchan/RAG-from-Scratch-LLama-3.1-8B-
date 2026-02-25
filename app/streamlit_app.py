"""
Streamlit RAG Application
Main user interface for the RAG system.
"""

import streamlit as st
import logging
from pathlib import Path
import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_pipeline import RAGPipeline
from src.pdf_processor import PDFProcessor
from src.embedding_manager import EmbeddingManager
from config.settings import (
    DEBUG,
    ENVIRONMENT,
    DOCUMENTS_DIR,
    EMBEDDINGS_DIR,
    LOGS_DIR,
    LOG_LEVEL
)

# Configure logging
log_dir = Path(LOGS_DIR)
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"streamlit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="RAG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #0f7d8f; font-weight: bold; }
    .sub-header { font-size: 1.3rem; color: #0f8d9f; }
    .success-box { background-color: #d4edda; border: 1px solid #c3e6cb; padding: 10px; border-radius: 5px; }
    .error-box { background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 5px; }
    .info-box { background-color: #d1ecf1; border: 1px solid #bee5eb; padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "pipeline" not in st.session_state:
    st.session_state.pipeline = None
    st.session_state.pdf_loaded = False
    st.session_state.chat_history = []
    st.session_state.document_info = None
    st.session_state.processed_filename = None  # Track which file was processed

def initialize_pipeline():
    """Initialize the RAG pipeline"""
    try:
        with st.spinner("Loading models... This may take a few minutes on first run."):
            st.session_state.pipeline = RAGPipeline(load_llm=True)
            logger.info("RAG Pipeline initialized successfully")
    except Exception as e:
        st.error(f"Error initializing pipeline: {str(e)}")
        logger.error(f"Pipeline initialization error: {str(e)}")
        st.session_state.pipeline = None


def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown("<h1 class='main-header'>🤖 RAG Assistant</h1>", unsafe_allow_html=True)
    st.markdown("Retrieval-Augmented Generation powered by Local LLMs", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("<h2 class='sub-header'>⚙️ Settings</h2>", unsafe_allow_html=True)
        
        # Environment info
        st.markdown("### Environment Info")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Mode:** {ENVIRONMENT}")
            st.write(f"**Debug:** {DEBUG}")
        with col2:
            st.write(f"**Log Level:** {LOG_LEVEL}")
        
        st.divider()
        
        # Document Upload
        st.markdown("### 📄 Document Management")
        
        uploaded_file = st.file_uploader("Upload PDF Document", type="pdf")
        
        # Only process if it's a NEW file (not already processed)
        if uploaded_file is not None and uploaded_file.name != st.session_state.processed_filename:
            file_path = Path(DOCUMENTS_DIR) / uploaded_file.name
            
            with st.spinner(f"Processing {uploaded_file.name}..."):
                try:
                    # Save file
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    logger.info(f"PDF uploaded: {file_path}")
                    
                    # Initialize pipeline if not already done
                    if st.session_state.pipeline is None:
                        initialize_pipeline()
                    
                    if st.session_state.pipeline:
                        # Process PDF
                        st.info("Processing PDF... This may take a few minutes.")
                        result = st.session_state.pipeline.pipeline(
                            pdf_path=str(file_path),
                            save_embeddings=True
                        )
                        
                        if result.get("status") == "success":
                            st.session_state.pdf_loaded = True
                            st.session_state.processed_filename = uploaded_file.name  # Mark as processed
                            st.session_state.document_info = {
                                "filename": uploaded_file.name,
                                "chunks": result.get("chunks_processed"),
                                "size": uploaded_file.size
                            }
                            st.success(f"✅ Successfully processed {result.get('chunks_processed')} chunks!")
                            logger.info(f"PDF processing successful: {result.get('chunks_processed')} chunks")
                        else:
                            st.error(f"Error processing PDF: {result.get('error')}")
                            logger.error(f"PDF processing failed: {result.get('error')}")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    logger.error(f"Upload error: {str(e)}")
        
        # Document Info
        if st.session_state.document_info:
            st.markdown("### 📊 Document Info")
            st.json(st.session_state.document_info)
        
        st.divider()
        
        # Generation Settings
        st.markdown("### 🎛️ Generation Settings")
        
        temperature = st.slider(
            "Temperature (creativity)",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Lower = more deterministic, Higher = more creative"
        )
        
        max_tokens = st.slider(
            "Max Tokens",
            min_value=100,
            max_value=2048,
            value=512,
            step=100
        )
        
        top_k = st.slider(
            "Retrieval Top-K",
            min_value=1,
            max_value=10,
            value=5,
            help="Number of chunks to retrieve"
        )
        
        st.session_state.generation_config = {
            "temperature": temperature,
            "max_new_tokens": max_tokens,
            "top_k": top_k
        }
    
    # Main content area
    if not st.session_state.pdf_loaded:
        st.info("👈 Please upload a PDF document in the sidebar to get started.")
        st.markdown("""
        ### How it works:
        1. **Upload PDF** - Upload your document in the sidebar
        2. **Processing** - The system extracts, chunks, and embeds the text
        3. **Query** - Ask questions about your document
        4. **Response** - Get AI-powered answers with relevant context
        """)
    else:
        # Chat interface
        st.markdown("<h2 class='sub-header'>💬 Ask Questions</h2>", unsafe_allow_html=True)
        
        # Chat history
        for i, msg in enumerate(st.session_state.chat_history):
            if msg["role"] == "user":
                st.write(f"**You:** {msg['content']}")
            else:
                st.write(f"**Assistant:** {msg['content']}")
            
            if "context" in msg and st.checkbox(f"Show context for message {i}", key=f"context_{i}"):
                with st.expander("Retrieved Context"):
                    for j, chunk in enumerate(msg.get("context", []), 1):
                        st.markdown(f"**Chunk {j}** (Score: {chunk.get('similarity_score', 0):.4f})")
                        st.write(chunk.get("sentence_chunk", "No text"))
                        st.markdown(f"*Page: {chunk.get('page_number', 'N/A')}*")
                        st.divider()
        
        # Query input
        st.divider()
        query = st.text_input("Enter your question:", placeholder="What would you like to know about the document?")
        
        col1, col2 = st.columns([4, 1])
        
        with col2:
            submit = st.button("Ask", type="primary", use_container_width=True)
        
        if submit and query:
            if st.session_state.pipeline is None:
                st.error("Pipeline not initialized. Please upload a document first.")
            else:
                with st.spinner("Retrieving context and generating response..."):
                    try:
                        # Get configuration
                        config = st.session_state.generation_config
                        
                        # Retrieve and generate
                        answer, context = st.session_state.pipeline.ask(
                            query=query,
                            top_k=config["top_k"],
                            temperature=config["temperature"],
                            max_new_tokens=config["max_new_tokens"],
                            return_context=True
                        )
                        
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
                        
                        logger.info(f"Query processed successfully: {query[:50]}...")
                        
                        # Display answer
                        st.markdown("### Answer:")
                        st.write(answer)
                        
                        # Show context
                        with st.expander("📚 Show Retrieved Context"):
                            for i, chunk in enumerate(context, 1):
                                st.markdown(f"**Chunk {i}** (Score: {chunk.get('similarity_score', 0):.4f})")
                                st.write(chunk.get("sentence_chunk", "No text"))
                                st.markdown(f"*Page: {chunk.get('page_number', 'N/A')}*")
                                st.divider()
                        
                        # Rerun to update chat display
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error generating response: {str(e)}")
                        logger.error(f"Query processing error: {str(e)}")
        
        # Actions
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        with col2:
            if st.button("📊 Show Statistics", use_container_width=True):
                st.session_state.show_stats = not st.session_state.get("show_stats", False)
                st.rerun()
        
        # Statistics
        if st.session_state.get("show_stats"):
            st.markdown("### 📈 Pipeline Statistics")
            try:
                stats = st.session_state.pipeline.get_statistics()
                st.json(stats)
            except Exception as e:
                st.error(f"Error retrieving statistics: {str(e)}")


if __name__ == "__main__":
    logger.info(f"Starting Streamlit app - Environment: {ENVIRONMENT}")
    main()
