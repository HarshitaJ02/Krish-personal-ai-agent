from groq import Groq
import config
import re
import json
from config import MODEL_MAIN, MODEL_CLASSIFIER

client = Groq(api_key=config.GROQ_API_KEY)


def get_llm_response(messages: list, tools: list = None, force_tool: bool = False, use_classifier_model: bool = False) -> dict:
    if tools:
        model = MODEL_MAIN
    else:
        model = MODEL_CLASSIFIER if use_classifier_model else MODEL_MAIN

    print(f"[LLM CALL] model={model}, tools={[t['function']['name'] for t in tools] if tools else None}")

    kwargs = {
        "model": model,
        "messages": messages,
        "max_tokens": 1024,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
        kwargs["parallel_tool_calls"] = False

    try:
        response = client.chat.completions.create(**kwargs)
        message = response.choices[0].message

        if message.tool_calls:
            tool_call = message.tool_calls[0]
            try:
                arguments = json.loads(tool_call.function.arguments)
            except Exception:
                arguments = {}
            print(f"[LLM] Tool call returned: {tool_call.function.name}")
            return {
                "type": "tool_call",
                "name": tool_call.function.name,
                "arguments": arguments
            }
        
        print(f"[LLM] Text returned: {str(message.content or '')[:80]}")

        return {
            "type": "text",
            "content": message.content or "",
        }

    except Exception as e:
        print(f"[LLM EXCEPTION] {str(e)}")
        error_str = str(e)
        if "failed_generation" in error_str:
            xml_match = re.search(r'<function=(\w+).*?(\{.*?\})', error_str, re.DOTALL)
            if xml_match:
                tool_name = xml_match.group(1)
                try:
                    arguments = json.loads(xml_match.group(2))
                    print(f"[LLM] XML fallback recovered: {tool_name} with {arguments}")
                    return {"type": "tool_call", "name": tool_name, "arguments": arguments}
                except json.JSONDecodeError as je:
                    print(f"[LLM] XML fallback JSON parse failed: {je}")
        return {"type": "text", "content": "Something went wrong."}
    
# def get_llm_response(messages:list, tools: list = None, force_tool:bool= False, use_classifier_model: bool = False) ->dict:
#     """
#     Send messages to Groq and return response.
    
#     Returns a dict with either:
#     - {"type": "text", "content": "response text"}
#     - {"type": "tool_call", "name": "tool_name", "arguments": {...}}
    
#     """
#     if tools:
#         model = MODEL_CLASSIFIER
#     else:
#         model = MODEL_CLASSIFIER if use_classifier_model else MODEL_MAIN

#     kwargs = {
#         "model": model,
#         "messages": messages,
#         "max_tokens": 1024,
#     }
#     if tools:
#         kwargs["tools"] = tools
#         # kwargs["tool_choice"] = "required" if force_tool else "auto"
#         kwargs["tool_choice"] = "auto"
#         kwargs["parallel_tool_calls"] = False 
    
#     try:
#         response = client.chat.completions.create(**kwargs)
#     message = response.choices[0].message

#     if message.tool_calls:
#         tool_call = message.tool_calls[0]
#         import json
#         try:
#             arguments = json.loads(tool_call.function.arguments)
#         except Exception:
#             arguments = {}
#         return {
#             "type": "tool_call",
#             "name": tool_call.function.name,
#             "arguments": arguments
#         }
    
#     return {
#         "type": "text",
#         "content": message.content or "",
#     }