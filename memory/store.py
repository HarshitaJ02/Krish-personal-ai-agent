from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
ROOT_DIR = BASE_DIR.parent
LOGS_DIR = BASE_DIR/ "logs"

LOGS_DIR.mkdir(exist_ok=True)

def read_file(filename:str) -> str:
    filepath = ROOT_DIR/filename
    if not filepath.exists():
        return ""
    return filepath.read_text(encoding="utf-8")

def read_context() -> str:
    soul = read_file("SOUL.md")
    user = read_file("USER.md")
    memory = read_file("MEMORY.md")
    
    context = ""
    if soul:
        context += f"## Your Personality and Guidelines\n{soul}\n\n"
    if user:
        context += f"## User Profile\n{user}\n\n"
    if memory:
        context += f"## What You Remember\n{memory}\n\n"
    
    return context

def read_soul_core() -> str:
    """
    Returns SOUL.md content.
    Always injected — defines Krish's personality and response rules.
    Kept short (~200-300 tokens). Trim SOUL.md if it grows large.
    """
    soul = read_file("SOUL.md")
    if not soul:
        return ""
    return f"## Personality & Response Rules\n{soul}"

def read_user_md() -> str:
    """
    Returns USER.md content.
    Injected only for personal/knowledge queries, not casual or tool queries.
    """
    user = read_file("USER.md")
    if not user:
        return ""
    return f"## User Profile\n{user}"

def read_memory_chunks(query: str = "", top_k: int = 3) -> str:
    """
    Returns relevant chunks from MEMORY.md instead of the full file.
    Splits MEMORY.md by bullet points, scores by keyword overlap with query,
    returns top_k most relevant chunks.
    Falls back to returning full MEMORY.md if query is empty.
    """
    memory_content = read_file("MEMORY.md")
    if not memory_content:
        return ""

    # If no query provided, return full memory (fallback)
    if not query:
        return f"## What You Remember\n{memory_content}"

    # Split into chunks by bullet point lines
    lines = memory_content.strip().split("\n")
    chunks = [line.strip() for line in lines if line.strip().startswith("-")]

    if not chunks:
        return f"## What You Remember\n{memory_content}"

    # Score each chunk by word overlap with query
    query_words = set(query.lower().split())

    def score_chunk(chunk: str) -> int:
        chunk_words = set(chunk.lower().split())
        return len(query_words & chunk_words)

    scored = sorted(chunks, key=score_chunk, reverse=True)
    top_chunks = scored[:top_k]

    # Always include at least the most recent 2 chunks for continuity
    recent_chunks = chunks[-2:] if len(chunks) >= 2 else chunks
    combined = list(dict.fromkeys(top_chunks + recent_chunks))  # dedup, preserve order

    result = "\n".join(combined)
    return f"## What You Remember\n{result}"


def write_to_memory(content: str) -> None:
    memory_file = ROOT_DIR/ "MEMORY.md"
    with open(memory_file, "a", encoding= "utf-8") as f:
        f.write(f"\n{content}")

def update_user_profile(content: str) -> None:
    user_file = ROOT_DIR / "USER.md"
    with open(user_file, "w", encoding="utf-8") as f:
        f.write(content)

def write_daily_log(role:str, content:str) -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR/ f"{today}.md"
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n[{timestamp}] {role}: {content}")


def write_metrics_log(entry: dict) -> None:
    """
    Appends a metrics entry to memory/logs/metrics.jsonl.
    Used for observability — track category distribution, token usage, routing.
    Analyze later to detect misrouting patterns and memory bloat.
    """
    import json
    metrics_file = LOGS_DIR / "metrics.jsonl"
    with open(metrics_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

# def read_recent_logs(days: int = 3) -> str:
#     log_files = sorted(LOGS_DIR.glob("*.md"))[-days:]
#     combined = ""
#     for log_file in log_files:
#         combined += f"\n\n--- {log_file.stem} ---\n"
#         combined += log_file.read_text(encoding="utf-8")

#     return combined

def read_recent_logs(days: int = 1, max_chars: int = 2000) -> str:
    """
    Returns recent daily logs, capped at max_chars.
    Cap prevents log bloat from inflating context on every message.
    Keeps most recent content (tail of log, not head).
    """
    log_files = sorted(LOGS_DIR.glob("*.md"))[-days:]
    combined = ""
    for log_file in log_files:
        combined += f"\n\n--- {log_file.stem} ---\n"
        combined += log_file.read_text(encoding="utf-8")

    # Keep most recent content within budget
    if len(combined) > max_chars:
        combined = combined[-max_chars:]

    return combined

