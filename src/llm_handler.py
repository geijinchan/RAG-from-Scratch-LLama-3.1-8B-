"""
LLM Handler Module
Manages language model loading and inference.
"""

import logging
from typing import List, Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
from transformers.utils import is_flash_attn_2_available
from threading import Thread
from config.settings import (
    LLM_MODEL_ID,
    DEVICE,
    LLM_TEMPERATURE,
    LLM_MAX_NEW_TOKENS,
    USE_8BIT_QUANTIZATION,
    USE_4BIT_QUANTIZATION,
    CACHE_LLM_MODEL,
    HUGGINGFACE_TOKEN
)

logger = logging.getLogger(__name__)


class LLMHandler:
    """
    Manages loading and inference with language models.
    """
    
    def __init__(
        self,
        model_id: str = LLM_MODEL_ID,
        device: str = DEVICE,
        use_8bit: bool = USE_8BIT_QUANTIZATION,
        use_4bit: bool = USE_4BIT_QUANTIZATION,
        use_flash_attention: bool = True
    ):
        """
        Initialize LLM handler.
        
        Args:
            model_id: Hugging Face model ID
            device: Device to load model on
            use_8bit: Use 8-bit quantization
            use_4bit: Use 4-bit quantization
            use_flash_attention: Use Flash Attention 2 if available
        """
        self.model_id = model_id
        self.device = device
        self.model = None
        self.tokenizer = None
        self.use_flash_attention = use_flash_attention and is_flash_attn_2_available()
        
        logger.info(f"Initializing LLMHandler with model: {model_id}")
        logger.info(f"Device: {device}, 8-bit: {use_8bit}, 4-bit: {use_4bit}")
        
        self._load_model(use_8bit=use_8bit, use_4bit=use_4bit)
    
    def _load_model(self, use_8bit: bool = False, use_4bit: bool = False):
        """
        Load tokenizer and model with quantization if specified.
        
        Args:
            use_8bit: Use 8-bit quantization
            use_4bit: Use 4-bit quantization
        """
        try:
            # Load tokenizer
            logger.info(f"Loading tokenizer for model: {self.model_id}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                token=HUGGINGFACE_TOKEN if HUGGINGFACE_TOKEN else None,
                trust_remote_code=True
            )
            
            # Prepare model kwargs
            model_kwargs = {
                "device_map": "auto" if self.device == "cuda" else None,
                "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
                "trust_remote_code": True,
                "token": HUGGINGFACE_TOKEN if HUGGINGFACE_TOKEN else None,
            }
            
            # Add quantization config if needed
            if use_8bit or use_4bit:
                from transformers import BitsAndBytesConfig
                
                if use_8bit:
                    logger.info("Using 8-bit quantization")
                    model_kwargs["quantization_config"] = BitsAndBytesConfig(
                        load_in_8bit=True,
                        cpu_int8_threshold=0.0,
                    )
                elif use_4bit:
                    logger.info("Using 4-bit quantization")
                    model_kwargs["quantization_config"] = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4",
                    )
            
            # Add Flash Attention if available
            if self.use_flash_attention:
                logger.info("Using Flash Attention 2")
                model_kwargs["attn_implementation"] = "flash_attention_2"
            
            # Load model
            logger.info(f"Loading model: {self.model_id}")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                **model_kwargs
            )
            
            logger.info(f"Successfully loaded model and tokenizer")
            
            # Set pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def generate(
        self,
        prompt: str,
        temperature: float = LLM_TEMPERATURE,
        max_new_tokens: int = LLM_MAX_NEW_TOKENS,
        top_p: float = 0.9,
        do_sample: bool = True,
        **kwargs
    ) -> str:
        """
        Generate text from prompt.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_new_tokens: Maximum new tokens to generate
            top_p: Nucleus sampling parameter
            do_sample: Whether to use sampling
            **kwargs: Additional generation arguments
            
        Returns:
            Generated text
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded")
        
        try:
            logger.info(f"Generating text (temp={temperature}, max_tokens={max_new_tokens})")
            
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    temperature=temperature,
                    max_new_tokens=max_new_tokens,
                    top_p=top_p,
                    do_sample=do_sample,
                    pad_token_id=self.tokenizer.eos_token_id,
                    **kwargs
                )
            
            # Decode output
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove prompt from output
            if prompt in generated_text:
                generated_text = generated_text.replace(prompt, "").strip()
            
            logger.info(f"Generation successful")
            return generated_text
            
        except Exception as e:
            logger.error(f"Error during generation: {str(e)}")
            raise
    
    def generate_streaming(
        self,
        prompt: str,
        temperature: float = LLM_TEMPERATURE,
        max_new_tokens: int = LLM_MAX_NEW_TOKENS,
        top_p: float = 0.9,
        do_sample: bool = True,
    ):
        """
        Generate text with streaming output (yields tokens).
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_new_tokens: Maximum new tokens
            top_p: Nucleus sampling parameter
            do_sample: Whether to use sampling
            
        Yields:
            Generated tokens
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded")
        
        try:
            logger.info("Starting streaming generation")
            
            # Create streamer
            streamer = TextIteratorStreamer(
                self.tokenizer,
                skip_prompt=True,
                skip_special_tokens=True
            )
            
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Generation kwargs
            generation_kwargs = {
                **inputs,
                "streamer": streamer,
                "temperature": temperature,
                "max_new_tokens": max_new_tokens,
                "top_p": top_p,
                "do_sample": do_sample,
                "pad_token_id": self.tokenizer.eos_token_id,
            }
            
            # Run generation in thread
            thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
            thread.start()
            
            # Yield tokens as they're generated
            for token in streamer:
                yield token
            
            thread.join()
            logger.info("Streaming generation complete")
            
        except Exception as e:
            logger.error(f"Error during streaming generation: {str(e)}")
            raise
    
    def format_prompt_with_context(
        self,
        query: str,
        context_items: List[Dict[str, Any]]
    ) -> str:
        """
        Format prompt with retrieved context.
        
        Args:
            query: User query
            context_items: Retrieved context chunks
            
        Returns:
            Formatted prompt
        """
        # Create context string
        context = "- " + "\n- ".join([
            item.get("sentence_chunk", item.get("text", ""))
            for item in context_items
        ])
        
        # Base prompt with examples
        base_prompt = """Based on the following context items, please answer the query.
Give yourself room to think by extracting relevant passages from the context before answering the query.
Don't return the thinking, only return the answer.
Make sure your answers are as explanatory as possible.

Context:
{context}

User Query: {query}

Answer:"""
        
        formatted_prompt = base_prompt.format(context=context, query=query)
        
        # Apply chat template if available
        try:
            dialogue_template = [
                {"role": "user", "content": formatted_prompt}
            ]
            prompt = self.tokenizer.apply_chat_template(
                conversation=dialogue_template,
                tokenize=False,
                add_generation_prompt=True
            )
            return prompt
        except Exception as e:
            logger.warning(f"Could not apply chat template: {str(e)}, using plain prompt")
            return formatted_prompt
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Model information
        """
        if self.model is None:
            return {}
        
        return {
            "model_id": self.model_id,
            "device": self.device,
            "parameters": sum(p.numel() for p in self.model.parameters()),
            "trainable_parameters": sum(p.numel() for p in self.model.parameters() if p.requires_grad),
            "vocab_size": self.tokenizer.vocab_size if self.tokenizer else None,
            "max_position_embeddings": getattr(self.model.config, "max_position_embeddings", None),
        }
