#Decide whether to extract memory, and if yes then extract it and write it.

import re
from agent.llm import get_llm_response
from memory import store

DURABLE_INFO_PATTERNS = [
    r'\b[A-Z][a-zA-Z]*[A-Z]\w*\b',  
    r'\bmy (startup|project|company|app|product|repo|idea)\b',
    r'\b(deadline|due date|target date|launch date)\b',
    r'\bi (prefer|like|want|need|hate|love|use|always|never)\b',
    r'\bmy (name is|goal is|plan is|stack is)\b',
]

def contains_durable_info(message: str) -> bool:
    for pattern in DURABLE_INFO_PATTERNS:
        if re.search(pattern, message, re.IGNORECASE):
            return True
    return False

def should_extract_memory(message:str, scores: dict) -> bool:
    if scores["casual"] > 0.8:
        return False
    if scores["personal"] > 0.5:
        return True
    if scores["knowledge"] > 0.5:
        return True
    if scores["tool"] > 0.7 and contains_durable_info(message):
        return True
    return False

def check_for_memory(user_message: str, assistant_response: str) -> None:
    try:
        prompt = [
            {
                "role": "system",
                "content": """You are a memory extraction assistant. Identify facts worth remembering long term in the conversation.
Worth remembering means: decisions made, preferences stated, commitments given, important personal facts.
NOT worth remembering means: casual chat, questions, greetings, generic responses,  things already known from user profile like name or preferred name.

If something is worth remembering, respond with ONLY the fact to remember in one short sentence starting with a bullet point like:
- Hash decided to build portfolio project using Python and FastAPI

If nothing is worth remembering respond with exactly:
NOTHING"""
            },
            {
                "role": "user",
                "content": f"User said: {user_message}\nAssistant responded: {assistant_response}"
            }
        ]
        
        result_dict = get_llm_response(prompt, use_classifier_model=True)
        result = result_dict.get("content", "NOTHING")
        
        
        if result.strip() != "NOTHING":
            store.write_to_memory(result.strip())
        
    except Exception as e:
        print(f"Memory extraction failed: {e}")