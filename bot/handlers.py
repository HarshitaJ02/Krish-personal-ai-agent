#used as a postman for routing

from telegram import Update
from telegram.ext import ContextTypes
from agent.core import run_agent

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    bot = context.bot
    chat_id = str(update.message.chat_id)
    response = await run_agent(user_message, bot=bot, chat_id=chat_id)
    await update.message.reply_text(response)

async def handle_start(update:Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey! I'm Krish, your personal AI assistant.\n\n"
        "I'm not fully set up yet — onboarding coming soon!\n\n"
        "For now just send me a message and let's talk."
    )

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Here's what I can do:\n\n"
        "🔍 *Web Search* — ask me anything current\n"
        "💻 *GitHub* — list repos, create issues\n"
        "📝 *Notion* — append notes, create pages\n"
        "⏰ *Reminders* — 'remind me at 7pm to...'\n"
        "📢 *Send messages* — 'send to the group: ...'\n\n"
        "Commands:\n"
        "/help — show this message\n"
        "/memory — show what I remember about you\n"
        "/clear — clear our conversation history",
        parse_mode="Markdown"
    )

async def handle_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from memory.store import read_file
    memory = read_file("MEMORY.md")
    if memory:
        await update.message.reply_text(f"Here's what I remember:\n\n{memory}")
    else:
        await update.message.reply_text("I don't have anything stored in memory yet.")
        
async def handle_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from agent.core import conversation_history
    conversation_history.clear()
    await update.message.reply_text("Conversation history cleared!")