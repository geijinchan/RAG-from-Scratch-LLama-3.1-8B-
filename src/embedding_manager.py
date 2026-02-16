"""
Embedding Management Module
Handles text embeddings generation, storage, and retrieval.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
import pickle
import json
from tqdm.auto import tqdm
from config.settings import (
    EMBEDDINGS_DIR,
    EMBEDDING_MODEL,
    DEVICE,
    EMBEDDING_BATCH_SIZE,
    CACHE_EMBEDDING_MODEL
)

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """
    Manages text embeddings: generation, storage, and caching.
    """
    
    def __init__(self, model_name: str = EMBEDDING_MODEL, device: str = DEVICE):
        """
        Initialize embedding manager with SentenceTransformers.
        
        Args:
            model_name: Name of the embedding model
            device: Device to load model on ('cuda' or 'cpu')
        """
        self.model_name = model_name
        self.device = device
        self.model: Optional[SentenceTransformer] = None
        self.embeddings_dir = EMBEDDINGS_DIR
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initializing EmbeddingManager with model: {model_name}")
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name} on device: {self.device}")
            self.model = SentenceTransformer(
                model_name_or_path=self.model_name,
                device=self.device,
                cache_folder=str(self.embeddings_dir) if CACHE_EMBEDDING_MODEL else None
            )
            logger.info(f"Successfully loaded embedding model")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise
    
    def generate_embeddings(
        self,
        texts: Union[str, List[str]],
        batch_size: int = EMBEDDING_BATCH_SIZE,
        convert_to_tensor: bool = True,
        convert_to_numpy: bool = False,
        show_progress_bar: bool = True
    ) -> Union[np.ndarray, torch.Tensor]:
        """
        Generate embeddings for text(s).
        
        Args:
            texts: Single text or list of texts to embed
            batch_size: Batch size for processing
            convert_to_tensor: Return as torch tensor
            convert_to_numpy: Return as numpy array
            show_progress_bar: Show progress bar
            
        Returns:
            Embeddings as tensor or numpy array
        """
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            logger.warning("No texts provided for embedding")
            raise ValueError("No texts provided for embedding")
        
        try:
            logger.info(f"Generating embeddings for {len(texts)} text(s) with batch size {batch_size}")
            
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_tensor=convert_to_tensor,
                convert_to_numpy=convert_to_numpy,
                show_progress_bar=show_progress_bar
            )
            
            logger.info(f"Successfully generated embeddings with shape: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def embed_chunks(
        self,
        chunks: List[Dict[str, Any]],
        batch_size: int = EMBEDDING_BATCH_SIZE
    ) -> List[Dict[str, Any]]:
        """
        Generate embeddings for list of chunks.
        
        Args:
            chunks: List of chunk dictionaries
            batch_size: Batch size for processing
            
        Returns:
            Chunks with embeddings added
        """
        if not chunks:
            logger.warning("No chunks provided for embedding")
            return chunks
        
        logger.info(f"Embedding {len(chunks)} chunks")
        
        # Extract texts from chunks
        texts = [chunk["sentence_chunk"] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.generate_embeddings(
            texts,
            batch_size=batch_size,
            convert_to_tensor=True
        )
        
        # Add embeddings to chunks
        for chunk, embedding in tqdm(zip(chunks, embeddings), desc="Attaching embeddings", total=len(chunks)):
            chunk["embedding"] = embedding.cpu().numpy()
        
        logger.info(f"Successfully embedded {len(chunks)} chunks")
        return chunks
    
    def save_embeddings(
        self,
        chunks: List[Dict[str, Any]],
        filename: str = "embeddings.pkl",
        metadata_filename: str = "embeddings_metadata.json"
    ) -> Path:
        """
        Save embeddings and metadata to disk.
        
        Args:
            chunks: List of chunks with embeddings
            filename: Pickle file to save embeddings
            metadata_filename: JSON file to save metadata
            
        Returns:
            Path to saved embeddings file
        """
        try:
            embeddings_path = self.embeddings_dir / filename
            metadata_path = self.embeddings_dir / metadata_filename
            
            logger.info(f"Saving embeddings to: {embeddings_path}")
            
            # Save chunks with embeddings
            with open(embeddings_path, 'wb') as f:
                pickle.dump(chunks, f)
            
            # Save metadata
            metadata = {
                "num_chunks": len(chunks),
                "model": self.model_name,
                "filename": filename,
                "chunk_stats": {
                    "avg_tokens": np.mean([c.get("chunk_token_count", 0) for c in chunks]),
                    "max_tokens": np.max([c.get("chunk_token_count", 0) for c in chunks]),
                    "min_tokens": np.min([c.get("chunk_token_count", 0) for c in chunks]),
                }
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            logger.info(f"Successfully saved {len(chunks)} embeddings")
            return embeddings_path
            
        except Exception as e:
            logger.error(f"Error saving embeddings: {str(e)}")
            raise
    
    def load_embeddings(self, embeddings_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Load embeddings from disk.
        
        Args:
            embeddings_path: Path to embeddings file
            
        Returns:
            List of chunks with embeddings
        """
        embeddings_path = Path(embeddings_path)
        
        if not embeddings_path.exists():
            logger.error(f"Embeddings file not found: {embeddings_path}")
            raise FileNotFoundError(f"Embeddings file not found: {embeddings_path}")
        
        try:
            logger.info(f"Loading embeddings from: {embeddings_path}")
            
            with open(embeddings_path, 'rb') as f:
                chunks = pickle.load(f)
            
            logger.info(f"Successfully loaded {len(chunks)} chunks with embeddings")
            return chunks
            
        except Exception as e:
            logger.error(f"Error loading embeddings: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings.
        
        Returns:
            Embedding dimension
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        return self.model.get_sentence_embedding_dimension()


# Utility function for backward compatibility
def embed_texts(texts: Union[str, List[str]], model_name: str = EMBEDDING_MODEL) -> np.ndarray:
    """
    Standalone function to embed texts.
    
    Args:
        texts: Text(s) to embed
        model_name: Embedding model name
        
    Returns:
        Embeddings
    """
    manager = EmbeddingManager(model_name=model_name)
    return manager.generate_embeddings(texts, convert_to_numpy=True)
