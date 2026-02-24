from pathlib import Path
from datetime import datetime
from sentence_transformers import SentenceTransformer
import chromadb

BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR.parent/"memory"/"logs"
CHROMA_DIR = BASE_DIR.parent/".chroma"

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path= str(CHROMA_DIR))

collection = chroma_client.get_or_create_collection(
    name = "telegram_messages",
    metadata={"description": "All Telegram conversation messages"}
)

def parse_log_file(log_file_path:Path) -> list:
    """Parse a daily log file and return a list of messages."""
    if not log_file_path.exists():
        return []
    
    content = log_file_path.read_text(encoding="utf-8")
    messages = []

    for line in content.strip().split('\n'):
        if not line.strip():
            continue

        if line.startswith('[') and ']' in line:
            timestamp_end = line.index(']')
            timestamp = line[1:timestamp_end]
            rest = line[timestamp_end+ 2:]

            if ':' in rest:
                role, message = rest.split(':', 1)
                role = role.strip()
                message = message.strip()

                date = log_file_path.stem

                messages.append({
                    "date": date,
                    "timestamp": timestamp,
                    "role": role,
                    "content": message,
                    "id": f"{date}_{timestamp}_{role}"
                })
    return messages

def index_all_logs():
    """Index all messages from daily logs into ChromaDB."""
    log_files = sorted(LOGS_DIR.glob("*.md"))

    if not log_files:
        print("No log files found.")
        return
    
    existing = collection.get(include=[])
    existing_ids = set(existing["ids"]) if existing["ids"] else set()

    new_messages = []
    for log_file in log_files:
        messages = parse_log_file(log_file)
        for msg in messages:
            if msg["id"] not in existing_ids:
                new_messages.append(msg)

    if not new_messages:
        print(f"ChromaDB up to date ({len(existing_ids)} messages already indexed).")
        return
    
    ids = [msg["id"] for msg in new_messages]
    documents = [msg["content"] for msg in new_messages]
    metadatas = [
        {
            "date": msg["date"],
            "timestamp": msg["timestamp"],
            "role": msg["role"]
        }
        for msg in new_messages
    ]

    embeddings = embedding_model.encode(documents).tolist()

    collection.upsert(
        ids= ids,
        embeddings=embeddings,
        documents= documents,
        metadatas=metadatas
    )

    print(f"Indexed {len(new_messages)} new messages. Total: {len(existing_ids) + len(new_messages)}")


if __name__ == "__main__":
    index_all_logs()
