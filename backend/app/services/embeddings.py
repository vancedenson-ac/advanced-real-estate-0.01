"""Text and image embedding utilities."""
import numpy as np
from typing import Optional, List
import os


def get_text_embedding(text: str) -> np.ndarray:
    """
    Generate text embedding for RAG.
    
    Args:
        text: Input text
        
    Returns:
        numpy array of shape (1536,) for OpenAI embeddings
    """
    # Stub implementation - replace with actual OpenAI API or local model
    # In production, this would call:
    # - OpenAI API: openai.Embedding.create(model="text-embedding-ada-002", input=text)
    # - Or local model: sentence-transformers, etc.
    
    # For now, return a stub embedding
    # In production, use:
    # import openai
    # response = openai.Embedding.create(model="text-embedding-ada-002", input=text)
    # return np.array(response['data'][0]['embedding'])
    
    np.random.seed(hash(text) % 2**32)  # Deterministic for same text
    embedding = np.random.randn(1536).astype(np.float32)
    embedding = embedding / np.linalg.norm(embedding)
    return embedding


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def vector_to_list(vector: np.ndarray) -> List[float]:
    """Convert numpy array to list for JSON serialization."""
    return vector.tolist()


def list_to_vector(lst: List[float]) -> np.ndarray:
    """Convert list to numpy array."""
    return np.array(lst, dtype=np.float32)

