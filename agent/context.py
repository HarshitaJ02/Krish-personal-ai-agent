# builds the system message with right context

#imports
import tiktoken
from config import CONTEXT_BUDGETS, MAX_CONTEXT_TOKENS
from memory import store
from rag.retriever import retrieve_context

encoder = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(encoder.encode(text))

def trim_to_budget(text: str, max_tokens: int) -> str:
    tokens = encoder.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return encoder.decode(tokens[:max_tokens])

def compute_budget(scores: dict) -> int:
    raw = (
        CONTEXT_BUDGETS["casual"]    * scores["casual"]    +
        CONTEXT_BUDGETS["tool"]      * scores["tool"]      +
        CONTEXT_BUDGETS["knowledge"] * scores["knowledge"] +
        CONTEXT_BUDGETS["personal"]  * scores["personal"]
    )
    return min(int(raw), MAX_CONTEXT_TOKENS)

def should_use_tools(scores: dict) -> bool:
    tool_score = scores["tool"]
    is_dominant = tool_score == max(scores.values())
    is_meaningful = tool_score > 0.4  # floor to avoid accidental triggers
    return is_dominant and is_meaningful

def build_context(user_message:str, scores:dict)->str:
    budget_tokens = compute_budget(scores)
    pieces = []
    used_tokens = 0

    soul = store.read_soul_core()
    if soul:
        soul_tokens = count_tokens(soul)
        pieces.append(soul)
        used_tokens += soul_tokens
    
    if scores["casual"] > 0.8:
        return "\n\n".join(pieces)
    
    if scores["personal"] > 0.4 or scores["knowledge"] > 0.5:
        user_md = store.read_user_md()
        if user_md:
            user_tokens = count_tokens(user_md)
            if used_tokens + user_tokens < budget_tokens:
                pieces.append(user_md)
                used_tokens += user_tokens
    
    if scores["personal"] > 0.4:
        memory = store.read_memory_chunks(query=user_message, top_k=3)
        if memory:
            memory_tokens = count_tokens(memory)
            if used_tokens + memory_tokens < budget_tokens:
                pieces.append(memory)
                used_tokens += memory_tokens
    if (scores["knowledge"] > 0.5 or scores["personal"] > 0.6) and scores["tool"] < 0.7:
        try:
            rag = retrieve_context(user_message, top_k=3)
            if rag:
                rag_tokens = count_tokens(rag)
                if used_tokens + rag_tokens < budget_tokens:
                    pieces.append(f"## Relevant Past Context\n{rag}")
                    used_tokens += rag_tokens
        except Exception as e:
            print(f"[CONTEXT ERROR] RAG injection failed: {e}")    
            pass  # RAG failure should never break context building
    
    if scores["personal"] > 0.5:
        remaining_tokens = budget_tokens - used_tokens
        if remaining_tokens > 100:  # only worth adding if meaningful space left
            logs = store.read_recent_logs(days=1, max_chars=remaining_tokens * 4)
            if logs:
                # Trim precisely to remaining budget
                logs = trim_to_budget(logs, remaining_tokens)
                pieces.append(f"## Recent Conversation Logs\n{logs}")
    return "\n\n".join(pieces)

def build_system_message(user_message: str, scores: dict) -> str:
    """
    Wraps build_context() output in the full system prompt.
    Response rules are always appended — they're cheap (few tokens)
    and critical for Krish's behavior.
    """
    context = build_context(user_message, scores)

    return f"""You are Krish, a personal AI assistant.
{context}

## Response Rules
- Keep responses SHORT and DIRECT. 2-3 sentences max unless depth is explicitly asked for.
- Never add unnecessary follow-up questions as a habit.
- Never repeat information already stated.
- Get to the point immediately.
- Only ask a follow-up question if genuinely needed.
- Do not address the user by name in every response.
"""



    
    


    