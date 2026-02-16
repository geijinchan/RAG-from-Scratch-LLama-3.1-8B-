"""
Utility functions for the RAG system.
"""

import textwrap
from typing import List, Dict, Any
import json


def print_wrapped(text: str, width: int = 80):
    """
    Print text with word wrapping.
    
    Args:
        text: Text to print
        width: Column width
    """
    wrapped = textwrap.fill(text, width=width)
    print(wrapped)


def format_chunk_text(chunk: Dict[str, Any], max_length: int = 200) -> str:
    """
    Format chunk text for display.
    
    Args:
        chunk: Chunk dictionary
        max_length: Maximum text length
        
    Returns:
        Formatted text
    """
    text = chunk.get("sentence_chunk", "")
    if len(text) > max_length:
        text = text[:max_length] + "..."
    return text


def format_search_results(
    results: List[Dict[str, Any]],
    max_results: int = 5
) -> str:
    """
    Format search results for display.
    
    Args:
        results: List of result chunks
        max_results: Maximum results to show
        
    Returns:
        Formatted string
    """
    output = "Search Results:\n"
    output += "=" * 50 + "\n"
    
    for i, result in enumerate(results[:max_results], 1):
        score = result.get("similarity_score", 0)
        text = format_chunk_text(result, max_length=100)
        page = result.get("page_number", "N/A")
        
        output += f"\n[{i}] Score: {score:.4f} | Page: {page}\n"
        output += f"    {text}\n"
    
    return output


def chunk_to_dict(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert chunk to serializable dictionary.
    
    Args:
        chunk: Chunk dictionary
        
    Returns:
        Serializable dictionary
    """
    result = {}
    for key, value in chunk.items():
        if key == "embedding":
            # Don't include embeddings in output
            continue
        elif hasattr(value, 'tolist'):  # numpy array
            result[key] = value.tolist()
        elif hasattr(value, 'item'):  # torch tensor
            result[key] = value.item()
        else:
            result[key] = value
    return result


def save_results_to_json(
    query: str,
    answer: str,
    context: List[Dict[str, Any]],
    filename: str = "results.json"
) -> str:
    """
    Save query results to JSON file.
    
    Args:
        query: Query string
        answer: Generated answer
        context: Context chunks
        filename: Output filename
        
    Returns:
        Path to saved file
    """
    results = {
        "query": query,
        "answer": answer,
        "context": [chunk_to_dict(c) for c in context]
    }
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    return filename


def validate_pdf_path(pdf_path: str) -> bool:
    """
    Validate PDF file path.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        True if valid, False otherwise
    """
    from pathlib import Path
    path = Path(pdf_path)
    
    if not path.exists():
        return False
    
    if not path.suffix.lower() == ".pdf":
        return False
    
    if not path.is_file():
        return False
    
    return True
