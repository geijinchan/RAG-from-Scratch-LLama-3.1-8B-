"""
LLM Handler Module
Manages language model inference using Groq Cloud API.
"""

import logging
from typing import List, Dict, Any, Optional, Generator
from groq import Groq
from config.settings import (
    GROQ_MODEL,
    GROQ_API_KEY,
    LLM_TEMPERATURE,
    LLM_MAX_NEW_TOKENS,
    GROQ_API_TIMEOUT
)

logger = logging.getLogger(__name__)


class LLMHandler:
    """
    Manages inference with language models using Groq Cloud API.
    No local model loading required - all inference is done via API.
    """
    
    def __init__(
        self,
        model_id: str = GROQ_MODEL,
        api_key: str = GROQ_API_KEY,
        temperature: float = LLM_TEMPERATURE,
        max_tokens: int = LLM_MAX_NEW_TOKENS
    ):
        """
        Initialize Groq LLM handler.
        
        Args:
            model_id: Groq model ID
            api_key: Groq API key
            temperature: Default temperature for generation
            max_tokens: Default max tokens for generation
            
        Raises:
            ValueError: If api_key is not provided
        """
        if not api_key:
            raise ValueError("GROQ_API_KEY is required. Set it in .env or pass it as api_key parameter.")
        
        self.model_id = model_id
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize Groq client
        self.client = Groq(api_key=api_key)
        
        logger.info(f"Initialized Groq LLM Handler with model: {model_id}")
        logger.info(f"Default temperature: {temperature}, max_tokens: {max_tokens}")
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        **kwargs
    ) -> str:
        """
        Generate text from prompt using Groq API.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (optional, uses default if not specified)
            max_tokens: Maximum tokens to generate (optional, uses default if not specified)
            top_p: Nucleus sampling parameter
            **kwargs: Additional parameters to pass to API
            
        Returns:
            Generated text
            
        Raises:
            RuntimeError: If API call fails
        """
        try:
            temp = temperature if temperature is not None else self.temperature
            max_tok = max_tokens if max_tokens is not None else self.max_tokens
            
            logger.info(f"Generating text with Groq (temp={temp}, max_tokens={max_tok})")
            
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temp,
                max_tokens=max_tok,
                top_p=top_p,
                **kwargs
            )
            
            generated_text = response.choices[0].message.content
            logger.info("Generation successful")
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error during generation: {str(e)}")
            raise RuntimeError(f"Failed to generate text: {str(e)}")
    
    def generate_streaming(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Generate text with streaming output using Groq API.
        Yields tokens as they're generated.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (optional, uses default if not specified)
            max_tokens: Maximum tokens to generate (optional, uses default if not specified)
            top_p: Nucleus sampling parameter
            **kwargs: Additional parameters to pass to API
            
        Yields:
            Generated text chunks
            
        Raises:
            RuntimeError: If API call fails
        """
        try:
            temp = temperature if temperature is not None else self.temperature
            max_tok = max_tokens if max_tokens is not None else self.max_tokens
            
            logger.info(f"Starting streaming generation with Groq (temp={temp}, max_tokens={max_tok})")
            
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temp,
                max_tokens=max_tok,
                top_p=top_p,
                stream=True,  # Enable streaming
                **kwargs
            )
            
            # Yield chunks as they arrive
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
            logger.info("Streaming generation complete")
            
        except Exception as e:
            logger.error(f"Error during streaming generation: {str(e)}")
            raise RuntimeError(f"Failed to generate text stream: {str(e)}")
    
    def format_prompt_with_context(
        self,
        query: str,
        context_items: List[Dict[str, Any]]
    ) -> str:
        """
        Format prompt with retrieved context for Groq API.
        
        Args:
            query: User query
            context_items: Retrieved context chunks
            
        Returns:
            Formatted prompt for LLM
        """
        # Create context string
        context = "- " + "\n- ".join([
            item.get("sentence_chunk", item.get("text", ""))
            for item in context_items
        ])
        
        # Base prompt with RAG context
        base_prompt = """Based on the following context items, please answer the query.
Give yourself room to think by extracting relevant passages from the context before answering the query.
Don't return the thinking, only return the answer.
Make sure your answers are as explanatory as possible.

Context:
{context}

User Query: {query}

Answer:"""
        
        formatted_prompt = base_prompt.format(context=context, query=query)
        logger.debug(f"Formatted prompt (length: {len(formatted_prompt)} chars)")
        
        return formatted_prompt
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the Groq model.
        
        Returns:
            Model information dictionary
        """
        return {
            "model_id": self.model_id,
            "provider": "Groq Cloud API",
            "type": "Hosted LLM (No local download required)",
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "inference_type": "API-based"
        }
