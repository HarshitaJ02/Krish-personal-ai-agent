#openai defined this type of schema
import json
import config
import requests

WEB_SEARCH_TOOL = {
        "type":"function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information. ONLY use 'web_search' tool for searching. Never invent other tool names. ALWAYS use this tool for: weather forecasts, news, sports scores, stock prices, current events, or any question about 'now' or 'today'. Do NOT answer these questions from memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query":{
                        "type": "string",
                        "description": "The search query. be specific and concise."
                    }
                },
                "required": ["query"]
            }
        }
    }

GITHUB_LIST_TOOL = {
        "type":"function",
        "function": {
            "name": "github_list_repos",
            "description":  "List all GitHub repositories for the user. Use when asked to show, list, or find GitHub repos.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }

GITHUB_CREATE_TOOL = {
        "type":"function",
        "function": {
            "name": "github_create_issue",
            "description": "Create a GitHub issue in a specific repository. Use when asked to create, add, or raise an issue or bug report.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "The repository name to create the issue in."
                    },
                    "title": {
                        "type": "string",
                        "description": "The title of the issue."
                    },
                    "body": {
                        "type": "string",
                        "description": "The detailed description of the issue."
                    }
                },
                "required": ["repo","title", "body"]
            }
        }
    }

NOTION_APPEND_TOOL = {
    "type": "function",
    "function": {
        "name": "notion_append",
        "description": "Append a note to Notion. ONLY use when user explicitly asks to save or add something to Notion. Never use proactively.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The text content to append to Notion."
                }
            },
            "required": ["content"]
        }
    }
}

NOTION_CREATE_TOOL = {
    "type": "function",
    "function": {
        "name": "notion_create_page",
        "description": "Create a new Notion page with a title and content. Use when asked to create a new page or document in Notion.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title of the new page."
                },
                "content": {
                    "type": "string",
                    "description": "The content of the new page."
                }
            },
            "required": ["title", "content"]
        }
    }
}

SET_REMINDER_TOOL = {
    "type": "function",
    "function": {
        "name": "set_reminder",
        "description": "Set a time-based reminder. Tool name is 'set_reminder'. ALWAYS use EXACTLY 'set_reminder' as tool name. Use when user says remind me, set a reminder, don't forget.",
        "parameters": {
            "type": "object",
            "properties": {
                "reminder_text": {
                    "type": "string",
                    "description": "The reminder request exactly as the user stated it. Example: 'call Mom at 6pm today'. Never put confirmation messages here."
                }
            },
            "required": ["reminder_text"]
        }
    }
}

TODOIST_LIST_TOOL = {
    "type": "function",
    "function": {
        "name": "todoist_list_tasks",
        "description": "List all pending tasks from Todoist. Use when user asks what tasks they have or what's pending. ALWAYS use EXACTLY 'todoist_list_tasks' as tool name.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

SEND_MESSAGE_TOOL = {
    "type": "function",
    "function": {
        "name": "send_telegram_message",
        "description": "Send a Telegram message to a known chat or group. Use when user says 'send a message to', 'announce to', 'tell the group'. Known recipients: 'me', 'group'. Execute immediately, do NOT ask for confirmation. Call this tool ONCE only. After sending, stop.",
        "parameters": {
            "type": "object",
            "properties": {
                "recipient": {
                    "type": "string",
                    "description": "Who to send to. Must be one of the known chats: 'me', 'group'."
                },
                "message": {
                    "type": "string",
                    "description": "The message content to send."
                }
            },
            "required": ["recipient", "message"]
        }
    }
}


async def execute_tool(tool_name: str, arguments: dict,  bot=None, chat_id: str = None) -> str:
    
    """Execute a tool and return as a string."""

    if tool_name == "web_search":
        return web_search(arguments.get("query", ""))
    if tool_name == "github_list_repos":
        return github_list_repos()
    if tool_name == "github_create_issue":
        return github_create_issue(
            arguments.get("repo", ""),
            arguments.get("title", ""),
            arguments.get("body", ""),
        )    
    if tool_name == "notion_append":
        return append_to_notion_page(arguments.get("content", ""))
    if tool_name == "notion_create_page":
        return create_notion_page(
            arguments.get("title", ""),
            arguments.get("content", "")
        )
    if tool_name == "set_reminder":
        return set_reminder(bot, chat_id, arguments.get("reminder_text", ""))
    
    if tool_name == "send_telegram_message":
        return await send_telegram_message(
            bot,
            arguments.get("recipient", ""),
            arguments.get("message", "")
        )
    
    return  f"Unknown tool: {tool_name}"

def web_search(query:str) ->str:
    """
    Perform a web search and return the results.
    """
    try:
        from serpapi import GoogleSearch
        import config

        search = GoogleSearch({
            "q": query,
            "api_key": config.SERPAPI_KEY,
            "num": 3
        })
        
        results = search.get_dict()

        original_results = results.get("organic_results", [])
        if not original_results:
            return "No search results found."
        
        formatted = []
        for i, result in enumerate(original_results[:3], 1):
            title = result.get("title", "No title")
            snippet = result.get("snippet", "No description")
            link = result.get("link", "")

            formatted.append(f"{i}. {title}\n {snippet}\n {link}")
        
        return "\n\n".join(formatted)
    
    except Exception as e:
        return f"Search failed: {str(e)}"

def github_list_repos() -> str:
    headers = {
    "Authorization": f"Bearer {config.GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/users/{config.GITHUB_USERNAME}/repos"
    
    try:
        response = requests.get(url,headers=headers)
        repos = response.json()

        formatted = []
    
        for repo in repos:
            name = repo["name"] 
            description = repo.get("description", "No description")
            formatted.append(f"- {name}: {description}")

        return "\n".join(formatted)
    except Exception as e:
        return f"Failed to fetch repos: {str(e)}"

def github_create_issue(repo:str, title:str, body:str) -> str:
    headers = {
    "Authorization": f"Bearer {config.GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
    }
    
    url = f"https://api.github.com/repos/{config.GITHUB_USERNAME}/{repo}/issues"
    
    try:
        response = requests.post(url, headers=headers, json = {"title": title, "body": body})
        
        return f"Issue created: {response.json()['html_url']}"
    except Exception as e:
        return f"Failed to create issue: {str(e)}"
   
def append_to_notion_page(content:str)->str:
    headers = {
        "Authorization": f"Bearer {config.NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": config.NOTION_VERSION 
    }

    url = f"https://api.notion.com/v1/blocks/{config.NOTION_PAGE_ID}/children"

    body = {
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": content}
                    }]
                }
            }
        ]
    }
    
    try:
        response = requests.patch(url, headers=headers, json=body)
        if response.status_code == 200:
            return f"Saved to your Krish Notes page. You can find it at notion.so/{config.NOTION_PAGE_ID}"
        else:
            return f"Notion error: {response.text}"
    except Exception as e:
        return f"Failed to append to Notion: {str(e)}"
    
def create_notion_page(title: str, content: str) -> str:
    headers = {
        "Authorization": f"Bearer {config.NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": config.NOTION_VERSION
    }
    
    url = "https://api.notion.com/v1/pages"
    
    body = {
        "parent": {"page_id": config.NOTION_PAGE_ID},
        "properties": {
            "title": {
                "title": [{
                    "type": "text",
                    "text": {"content": title}
                }]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": content}
                    }]
                }
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            return f"Notion page created: {response.json()['url']}"
        else:
            return f"Notion error: {response.text}"
    except Exception as e:
        return f"Failed to create Notion page: {str(e)}"
    
def set_reminder(bot, chat_id: str, reminder_text: str) -> str:
    """Parse natural language reminder and schedule it."""
    from scheduler.jobs import parse_reminder_datetime, add_reminder
    from datetime import datetime
    from zoneinfo import ZoneInfo
    
    parsed = parse_reminder_datetime(reminder_text)
    
    if not parsed or not parsed.get("datetime"):
        return "I couldn't understand the reminder time. Please be more specific like 'tomorrow at 10am'."
    
    try:
        run_date = datetime.strptime(parsed["datetime"], "%Y-%m-%d %H:%M:%S")
        # Prevent past reminders
        now = datetime.now()
        if run_date <= now:
            return "You can't set a reminder in the past."
        
        message = parsed.get("message", reminder_text)
        result = add_reminder(bot, chat_id, message, run_date)
        return result
        
    except Exception as e:
        print(f"Reminder error: {e}")
        return "Something went wrong while setting the reminder."

async def send_telegram_message(bot, recipient: str, message: str) -> str:
    chat_id = config.KNOWN_CHATS.get(recipient.lower())
    if not chat_id:
        available = ", ".join(config.KNOWN_CHATS.keys())
        return f"Unknown recipient '{recipient}'. Known chats: {available}"
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        return f"Message successfully sent to {recipient}. Task complete, no further action needed."

    except Exception as e:
        return f"Failed to send message: {str(e)}"

TOOLS = [
    WEB_SEARCH_TOOL,
    GITHUB_LIST_TOOL,
    GITHUB_CREATE_TOOL,
    NOTION_APPEND_TOOL,
    NOTION_CREATE_TOOL,
    SET_REMINDER_TOOL,
    SEND_MESSAGE_TOOL,
]

def filter_tools(message: str, scores: dict) -> list:
    msg = message.lower()
    tools = []
    
    if scores["tool"] > 0.4:
        tools.append(WEB_SEARCH_TOOL)
    
    if "github" in msg or "repo" in msg or "issue" in msg:
        tools.append(GITHUB_LIST_TOOL)
        tools.append(GITHUB_CREATE_TOOL)
    
    if "notion" in msg or "note" in msg or "save" in msg or "page" in msg:
        tools.append(NOTION_APPEND_TOOL)
        tools.append(NOTION_CREATE_TOOL)
    
    if "remind" in msg or "reminder" in msg or "forget" in msg:
        tools.append(SET_REMINDER_TOOL)

    if "send" in msg or "announce" in msg or "tell the group" in msg or "message to" in msg:
        tools.append(SEND_MESSAGE_TOOL)
    
    return tools if tools else [WEB_SEARCH_TOOL]

