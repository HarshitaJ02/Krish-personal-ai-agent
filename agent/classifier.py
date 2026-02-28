#this part of the project needs to look at a user message and return as score for each intent dimension so that the rest of the system knows what context to inject and whether to use a tool.

#imports
import json
from agent.llm import get_llm_response
import re

CASUAL_EXACT = {
    "hi", "hello", "hey", "thanks", "thank you", "ok", "okay", "k",
    "lol", "haha", "hehe", "bye", "goodbye", "good morning", "good night",
    "good evening", "sup", "yes", "no", "sure", "alright", "great",
    "cool", "nice", "got it", "noted", "hmm", "oh", "ah", "yep", "nope"
}

TOOL_EXACT_PHRASES = [
    "weather in", "weather at", "weather today", "weather tomorrow","weather of", "now",
    "temperature in", "forecast for",
    "news about", "latest news", "breaking news",
    "score of", "cricket score", "match score", "ipl score",
    "price of", "stock price", "current price",
    "what time is it", "what's the time", "current time",
    "what's today's date", "today's date", "current date",
    "search for", "look up",
]

PERSONAL_PHRASES = [
    "you said", "we talked", "we discussed", "last time", "yesterday", "discussed", "talked about",
    "last week", "remember when", "you mentioned", "i told you",
    "do you remember", "what did we", "earlier you", "before you said",
    "remind me", "again like you did", "what do you know about me", "who am i", "what are my goals",
    "what is my name", "do you know me", "do you know my name",
    "what do you know", "tell me about me", "my background",
    "what have i told you", "what do you remember about me",
]

def quick_triage(message: str) -> dict | None:
    msg = message.lower().strip()

    if msg in CASUAL_EXACT:
        return {"casual": 1.0, "tool": 0.0, "personal": 0.0, "knowledge": 0.0}
    if len(msg.split()) <= 2 and "?" not in msg:
        return {"casual": 0.9, "tool": 0.0, "personal": 0.0, "knowledge": 0.1}
    if any(phrase in msg for phrase in TOOL_EXACT_PHRASES):
        return {"casual": 0.0, "tool": 1.0, "personal": 0.0, "knowledge": 0.0}
    if any(phrase in msg for phrase in PERSONAL_PHRASES):
        return {"casual": 0.0, "tool": 0.0, "personal": 0.8, "knowledge": 0.5} #hybrid handling
    
    return None

def llm_score_intent(message: str) -> dict:
    scorer_prompt = [
        {
            "role": "system",
            "content": """You are an intent scorer. Given a user message, return a JSON object with scores from 0.0 to 1.0 for each dimension. Scores can overlap.

Dimensions:
- casual: small talk, greetings, acknowledgments, no real information need
- tool: requires calling an external service or API - includes web search, setting reminders, saving to Notion, sending messages to Telegram groups or chats, GitHub operations, or any request to DO something in an external system. If the user wants an ACTION performed on an external system, score tool 0.9 or higher.
- personal: references past conversations, user's own life, memory, things said before
- knowledge: needs reasoning, explanation, general facts, analysis

Return ONLY valid JSON with exactly these four keys. No explanation, no markdown.
Example: {"casual": 0.1, "tool": 0.8, "personal": 0.2, "knowledge": 0.3}"""
        },
        {
            "role": "user",
            "content": f"Score this message:\n{message}"
        }
    ]

    try:
        response = get_llm_response(scorer_prompt, use_classifier_model=True)
        raw = response.get("content", "").strip()
        raw = re.sub(r"```json|```", "", raw).strip()

        scores = json.loads(raw)

        keys = ["casual", "tool", "personal", "knowledge"]
        return {k: max(0.0, min(1.0, float(scores.get(k, 0.0)))) for k in keys}
    except Exception:
        return {"casual": 0.0, "tool":0.0, "personal":0.0, "knowledge": 1.0}
    
def classify_message(message:str) -> dict:
    scores = quick_triage(message)
    if scores is not None:
        return scores
    return llm_score_intent(message)