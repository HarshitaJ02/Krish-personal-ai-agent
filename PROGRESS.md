# Project Progress

## Phase 1 — COMPLETE
- Telegram bot connected and running (kr_assistant_bot)
- Groq LLM (Llama 3.3 70b) integrated
- Basic message handling working
- Files built: config.py, agent/llm.py, bot/handlers.py, main.py

## Next — Phase 2
- Build the memory system
- MEMORY.md, USER.md, SOUL.md, TOOLS.md read/write logic
- Daily logs in memory/logs/
- Inject memory into system message via agent/core.py

## Known Optimizations (Post-v1)
- File caching for SOUL.md and USER.md with TTL invalidation
- Batched memory extraction instead of per-message
- Mem0 integration to replace manual memory extraction
- Strategy 3 hybrid conversation summarization

### Design Decisions Made

| Decision | Choice | Alternative Considered | Reason for Choice |
|---|---|---|---|
| Embedding model | sentence-transformers (local) | OpenAI embeddings API | Free, fast, offline, sufficient quality for conversational retrieval |
| Vector database | ChromaDB (local) | Pinecone, Qdrant, Weaviate | Zero setup, in-process, perfect for development scale |
| Indexing strategy | Batch from logs | Real-time per message | Separation of concerns, easier debugging, re-indexable |
| Retrieval count | top_k=5 | Dynamic based on similarity | Simple, token-efficient, relevance drops after top 5 |
| Duplicate handling | upsert | Manual checking | Atomic, idempotent, simpler code |