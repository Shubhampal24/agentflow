"""
AgentFlow — Retrieval Service (RAG Stub)
Extension point for future pgvector / RAG implementation.

Phase 1: Returns empty context — does not block the agent.
Phase 2: Implement semantic search with pgvector.

Interface contract: search(query, top_k) -> list of context strings.
"""
from __future__ import annotations

import logging
from typing import List

logger = logging.getLogger(__name__)


async def search(query: str, top_k: int = 5) -> List[str]:
    """
    Search for relevant context given a query.

    Phase 1: Returns empty list — RAG not yet implemented.
    Phase 2: Query pgvector with an embedding of `query`.

    To add RAG:
    1. Install pgvector extension in Supabase
    2. Create documents, document_chunks, embeddings tables
    3. Use an embedding model to encode `query`
    4. Run: SELECT content FROM document_chunks ORDER BY embedding <=> $1 LIMIT $2
    5. Return the top_k content strings
    """
    logger.debug(f"retrieval_service.search called (stub). query_length={len(query)}")
    return []
