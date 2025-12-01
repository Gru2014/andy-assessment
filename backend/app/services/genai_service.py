import os
from typing import List, Dict, Any, Optional
from openai import OpenAI
import numpy as np
from functools import lru_cache

class GenAIService:
    """Abstraction layer for GenAI calls (LLM and embeddings)"""
    
    def __init__(self):
        self._client = None
        self.llm_model = os.getenv('LLM_MODEL', 'gpt-4o-mini')
        self.embedding_model = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
        self.temperature = float(os.getenv('LLM_TEMPERATURE', '0.7'))
        self.max_tokens = int(os.getenv('LLM_MAX_TOKENS', '2000'))
    
    @property
    def client(self):
        """Lazy initialization of OpenAI client"""
        if self._client is None:
            api_key = os.getenv('OPENAI_API_KEY')
            base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
            
            # Initialize client with only valid parameters
            client_kwargs = {}
            if api_key:
                client_kwargs['api_key'] = api_key
            if base_url:
                client_kwargs['base_url'] = base_url
            
            self._client = OpenAI(**client_kwargs)
        return self._client
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text string"""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Failed to get embedding: {str(e)}")
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts"""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            raise Exception(f"Failed to get embeddings batch: {str(e)}")
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Make a chat completion call"""
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens)
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Failed to get chat completion: {str(e)}")
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

