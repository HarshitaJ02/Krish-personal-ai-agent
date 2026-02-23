import asyncio
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
            return None
    return None

async def run_agent(user_message: str, bot=None, chat_id: str = None) -> str:
    global conversation_history

    store.write_daily_log("user", user_message)

    conversation_history.append({"role":"user", "content": user_message})

    if len(conversation_history)>config.MAX_HISTORY:
        conversation_history = conversation_history[-config.MAX_HISTORY:]
    
    final_response = "Something went wrong."  
    tools_used = []  
    #classify intent
    scores = classify_message(user_message)
    system_msg = build_system_message(user_message, scores)

    if should_use_tools(scores):
        # iterations = 0
        # response = get_llm_response(messages, tools=TOOLS, force_tool= False)
        

        relevant_tools = filter_tools(user_message, scores)
        # response = get_llm_response(messages, tools=relevant_tools, force_tool=True)
        messages = [{"role": "system", "content": system_msg}] +conversation_history
        response = get_llm_response(messages, tools=relevant_tools)

        iterations = 0
        tools_used = []

        while iterations < config.MAX_TOOL_ITERATIONS:

            # --- Handle XML hallucination fallback ---
            if response["type"] == "text" and response.get("content"):
                fallback = _parse_xml_fallback(response["content"])
                if fallback:
                    # Groq returned XML — treat it as a tool call anyway
                    response = {
                        "type": "tool_call",
                        "name": fallback[0],
                        "arguments": fallback[1]
                    }
            if response["type"] != "tool_call":
                # LLM is done reasoning, has a final answer
                break

            tool_name = response["name"]
            tool_args = response["arguments"]
            tools_used.append(tool_name)

            # print(f"Tool call detected: {tool_name}, args: {tool_args}")  # temporary
            tool_result = await execute_tool(
                tool_name, tool_args,
                bot=bot, chat_id=chat_id
            )
            # Append tool interaction to history
            conversation_history.append({
                "role": "assistant",
                "content": f"[Used {tool_name} tool]"
            })
            conversation_history.append({
                "role": "user",
                "content": f"Tool result for {tool_name}: {tool_result}"
            })
            
            if any(word in tool_result.lower() for word in ["sent", "success", "created", "saved", "appended"]):
                messages = [{"role": "system", "content": system_msg}] + conversation_history
                response = get_llm_response(messages)  # no tools, just summarize
                break
            # Update messages and call LLM again
            messages = [{"role": "system", "content": system_msg}] + conversation_history
            # response = get_llm_response(messages, tools=relevant_tools, force_tool = False)
            response = get_llm_response(messages, tools=relevant_tools)
            iterations += 1

        # # LLM returned text — done
        # if response["type"] == "text":
        #     final_response = response.get("content", "Something went wrong.")
        # else:
        #     final_response = "I wasn't able to complete that task."

    else:
        # No tools needed — direct LLM response
        messages = [{"role": "system", "content": system_msg}] + conversation_history
        response = get_llm_response(messages)
        final_response = response.get("content", "Something went wrong.")
        tools_used = []

    # Step 3: Save to history and logs
    conversation_history.append({"role": "assistant", "content": final_response})
    store.write_daily_log("assistant", final_response)

    # Step 4: Memory extraction (skip if it was just a tool operation)
    if should_extract_memory(user_message, scores):
        check_for_memory(user_message, final_response)

    # Step 5: Metrics
    store.write_metrics_log({
        "ts": datetime.now().isoformat(),
        "msg": user_message[:60],
        "scores": scores,
        "tools_used": tools_used,
        "ctx_chars": len(system_msg),
    })

    return final_response