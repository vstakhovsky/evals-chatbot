"""Embedding cache verification test."""

import json
import numpy as np
from pathlib import Path

EMBEDDINGS_PATH = Path("01_rag_baseline/data/article_embeddings.npy")
METADATA_PATH = Path("01_rag_baseline/data/article_embeddings.meta.json")


def test_embedding_cache_matches_metadata() -> None:
    """Verify that embeddings.npy matches the metadata contract."""
    if not EMBEDDINGS_PATH.exists():
        print("Skipping: Embeddings cache not found")
        return

    if not METADATA_PATH.exists():
        print("Skipping: Embeddings metadata not found")
        return

    embeddings = np.load(EMBEDDINGS_PATH)
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

    # Verify basic properties
    assert np.isfinite(embeddings).all(), "Embeddings must contain finite values"
    assert embeddings.ndim == 2, "Embeddings must be 2D array"

    # If metadata has article_count, verify it matches
    if metadata.get("article_count"):
        assert embeddings.shape[0] == metadata["article_count"], \
            f"Article count mismatch: {embeddings.shape[0]} vs {metadata['article_count']}"

    # If metadata has embedding_dimensions, verify it matches
    if metadata.get("embedding_dimensions"):
        assert embeddings.shape[1] == metadata["embedding_dimensions"], \
            f"Embedding dimensions mismatch: {embeddings.shape[1]} vs {metadata['embedding_dimensions']}"

    # Verify normalized flag
    assert metadata.get("normalized") == True, "Embeddings must be normalized"

    # Verify model name
    assert metadata.get("embedding_model") == "text-embedding-3-small", \
        f"Embedding model mismatch: {metadata.get('embedding_model')}"

    print("✅ Embedding cache matches metadata contract")


if __name__ == "__main__":
    test_embedding_cache_matches_metadata()
