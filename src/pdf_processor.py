"""
PDF Document Processing Module
Handles PDF extraction, text formatting, and chunking.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
import re
from tqdm.auto import tqdm
from spacy.lang.en import English
import pandas as pd
from config.settings import (
    DOCUMENTS_DIR,
    MIN_CHUNK_TOKENS,
    SENTENCE_CHUNK_SIZE,
    EMBEDDINGS_DIR,
    MAX_PDF_SIZE_BYTES
)

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Processes PDF documents: extraction, text formatting, and chunking.
    """
    
    def __init__(self):
        """Initialize PDF processor with spaCy NLP pipeline"""
        self.nlp = English()
        self.nlp.add_pipe("sentencizer")
        self.min_chunk_tokens = MIN_CHUNK_TOKENS
        self.sentence_chunk_size = SENTENCE_CHUNK_SIZE
        logger.info("PDFProcessor initialized")
    
    @staticmethod
    def text_formatter(text: str) -> str:
        """
        Performs text formatting and cleaning.
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Formatted text
        """
        cleaned_text = text.replace("\n", " ").strip()
        # Remove extra spaces
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        return cleaned_text
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from PDF and organize by pages.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dictionaries containing page metadata and text
        """
        pdf_path = Path(pdf_path)
        
        # Validate file
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if pdf_path.stat().st_size > MAX_PDF_SIZE_BYTES:
            logger.error(f"PDF file too large: {pdf_path.stat().st_size} bytes")
            raise ValueError(f"PDF file exceeds maximum size of {MAX_PDF_SIZE_BYTES} bytes")
        
        logger.info(f"Extracting text from PDF: {pdf_path}")
        
        try:
            doc = fitz.open(pdf_path)
            pages_and_texts = []
            
            for page_number, page in enumerate(tqdm(doc, desc="Extracting PDF pages")):
                text = page.get_text()
                text = self.text_formatter(text=text)
                
                pages_and_texts.append({
                    "page_number": page_number,
                    "page_char_count": len(text),
                    "page_sentence_count_raw": len(text.split(". ")),
                    "page_token_count": len(text) / 4,  # 1 token ~= 4 characters
                    "text": text
                })
            
            logger.info(f"Successfully extracted {len(pages_and_texts)} pages from PDF")
            return pages_and_texts
            
        except Exception as e:
            logger.error(f"Error extracting PDF: {str(e)}")
            raise
    
    def split_into_sentences(self, pages_and_texts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Split pages into sentences using spaCy.
        
        Args:
            pages_and_texts: List of page dictionaries
            
        Returns:
            Updated list with sentence information
        """
        logger.info("Splitting text into sentences")
        
        for item in tqdm(pages_and_texts, desc="Processing sentences"):
            doc = self.nlp(item["text"])
            item["sentences"] = [str(sentence) for sentence in doc.sents]
            item["page_sentence_count_spacy"] = len(item["sentences"])
        
        return pages_and_texts
    
    def chunk_sentences(self, pages_and_texts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Group sentences into chunks.
        
        Args:
            pages_and_texts: List of page dictionaries with sentences
            
        Returns:
            Updated list with chunked sentences
        """
        logger.info(f"Chunking sentences into groups of {self.sentence_chunk_size}")
        
        for item in tqdm(pages_and_texts, desc="Chunking sentences"):
            item["sentence_chunks"] = self._split_list(
                item["sentences"],
                slice_size=self.sentence_chunk_size
            )
            item["num_chunks"] = len(item["sentence_chunks"])
        
        return pages_and_texts
    
    @staticmethod
    def _split_list(input_list: List[str], slice_size: int) -> List[List[str]]:
        """
        Split a list into chunks of specified size.
        
        Args:
            input_list: List to split
            slice_size: Size of each chunk
            
        Returns:
            List of chunks
        """
        return [input_list[i:i+slice_size] for i in range(0, len(input_list), slice_size)]
    
    def create_chunks(self, pages_and_texts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create individual chunk dictionaries from chunked sentences.
        
        Args:
            pages_and_texts: List of page dictionaries with chunks
            
        Returns:
            List of chunk dictionaries
        """
        logger.info("Creating individual chunks")
        
        pages_and_chunks = []
        
        for item in tqdm(pages_and_texts, desc="Creating chunks"):
            for sentence_chunk in item["sentence_chunks"]:
                chunk_dict = {
                    "page_number": item["page_number"],
                }
                
                # Join sentences into paragraph
                joined_sentence_chunk = "".join(sentence_chunk).replace("  ", " ").strip()
                joined_sentence_chunk = re.sub(r'\.([A-Z])', r'. \1', joined_sentence_chunk)
                
                chunk_dict["sentence_chunk"] = joined_sentence_chunk
                chunk_dict["chunk_char_count"] = len(joined_sentence_chunk)
                chunk_dict["chunk_word_count"] = len(joined_sentence_chunk.split(" "))
                chunk_dict["chunk_token_count"] = len(joined_sentence_chunk) / 4
                
                pages_and_chunks.append(chunk_dict)
        
        logger.info(f"Created {len(pages_and_chunks)} chunks")
        return pages_and_chunks
    
    def filter_chunks(self, pages_and_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out short chunks with low token counts.
        
        Args:
            pages_and_chunks: List of chunks
            
        Returns:
            Filtered list of chunks
        """
        logger.info(f"Filtering chunks with less than {self.min_chunk_tokens} tokens")
        
        df = pd.DataFrame(pages_and_chunks)
        filtered_chunks = df[df["chunk_token_count"] > self.min_chunk_tokens].to_dict(orient="records")
        
        logger.info(f"Removed {len(pages_and_chunks) - len(filtered_chunks)} short chunks")
        logger.info(f"Retained {len(filtered_chunks)} chunks for embedding")
        
        return filtered_chunks
    
    def process_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Complete PDF processing pipeline.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of processed and filtered chunks
        """
        logger.info(f"Starting complete PDF processing pipeline for: {pdf_path}")
        
        try:
            # Extract text from PDF
            pages_and_texts = self.extract_text_from_pdf(pdf_path)
            
            # Split into sentences
            pages_and_texts = self.split_into_sentences(pages_and_texts)
            
            # Chunk sentences
            pages_and_texts = self.chunk_sentences(pages_and_texts)
            
            # Create chunks
            pages_and_chunks = self.create_chunks(pages_and_texts)
            
            # Filter chunks
            filtered_chunks = self.filter_chunks(pages_and_chunks)
            
            logger.info(f"PDF processing complete: {len(filtered_chunks)} chunks ready for embedding")
            return filtered_chunks
            
        except Exception as e:
            logger.error(f"PDF processing failed: {str(e)}")
            raise


# Utility function for backward compatibility
def process_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Standalone function to process PDF.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        List of processed chunks
    """
    processor = PDFProcessor()
    return processor.process_pdf(pdf_path)
