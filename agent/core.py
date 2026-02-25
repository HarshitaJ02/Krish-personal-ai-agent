import json
from datetime import datetime
from agent.classifier import classify_message
from agent.context import build_system_message, should_use_tools
from agent.llm import get_llm_response
from agent.tools import filter_tools, execute_tool
from agent.memory_ops import should_extract_memory, check_for_memory
from memory import store
import config
import re

conversation_history = []

ERROR_WORDS = ["failed", "error", "exception", "invalid", "unknown tool"]

def _parse_xml_fallback(content: str) -> tuple | None:
    if not content:
        return None
    match = re.search(r'<function=(\w+)>(.*?)(?:</function>|<function>|$)', content, re.DOTALL)
    if match:
        tool_name = match.group(1)
        try:
            arguments = json.loads(match.group(2).strip())
            return tool_name, arguments
        except json.JSONDecodeError:
            print(f"[XML FALLBACK] Could not parse: {match.group(2)[:100]}")
            return None
    return None

def _safe_llm_call(messages: list, tools: list = None) -> dict:
    """Single wrapper for all LLM calls. Logs errors, never crashes."""
    try:
        return get_llm_response(messages, tools=tools)
    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return {"type": "text", "content": None}

async def run_agent(user_message: str, bot=None, chat_id: str = None) -> str:
    global conversation_history

    store.write_daily_log("user", user_message)
    conversation_history.append({"role": "user", "content": user_message})

    if len(conversation_history) > config.MAX_HISTORY:
        conversation_history = conversation_history[-config.MAX_HISTORY:]

    final_response = "I'm having trouble right now. Please try again."
    tools_used = []

    scores = classify_message(user_message)
    system_msg = build_system_message(user_message, scores)
    messages = [{"role": "system", "content": system_msg}] + conversation_history

    if should_use_tools(scores):
        relevant_tools = filter_tools(user_message, scores)
        response = _safe_llm_call(messages, tools=relevant_tools)
        iterations = 0

        while iterations < config.MAX_TOOL_ITERATIONS:

            # Handle XML hallucination
            if response["type"] == "text" and response.get("content"):
                fallback = _parse_xml_fallback(response["content"])
                if fallback:
                    response = {
                        "type": "tool_call",
                        "name": fallback[0],
                        "arguments": fallback[1]
                    }

            # LLM has a final answer — done
            if response["type"] != "tool_call":
                break

            tool_name = response["name"]
            tool_args = response["arguments"]
            tools_used.append(tool_name)

            # Execute tool
            try:
                tool_result = await execute_tool(tool_name, tool_args, bot=bot, chat_id=chat_id)
            except Exception as e:
                print(f"[TOOL ERROR] {tool_name} failed: {e}")
                tool_result = f"Tool {tool_name} failed: {e}"

            conversation_history.append({
                "role": "assistant",
                "content": f"I used the {tool_name} tool."
            })
            conversation_history.append({
                "role": "user",
                "content": f"Tool result for {tool_name}: {tool_result}"
            })

            messages = [{"role": "system", "content": system_msg}] + conversation_history

            # Tool succeeded — get final response without tools
            # Tool failed — retry with tools so LLM can try differently
            tool_succeeded = not any(word in tool_result.lower() for word in ERROR_WORDS)
            if tool_succeeded:
                response = _safe_llm_call(messages)
                break
            else:
                response = _safe_llm_call(messages, tools=relevant_tools)

            iterations += 1

        final_response = response.get("content") or "I wasn't able to complete that."

    else:
        response = _safe_llm_call(messages)
        final_response = response.get("content") or "I wasn't able to complete that."

    conversation_history.append({"role": "assistant", "content": final_response})
    store.write_daily_log("assistant", final_response)

    if should_extract_memory(user_message, scores):
        check_for_memory(user_message, final_response)

    store.write_metrics_log({
        "ts": datetime.now().isoformat(),
        "msg": user_message[:60],
        "scores": scores,
        "tools_used": tools_used,
        "ctx_chars": len(system_msg),
    })

    return final_response