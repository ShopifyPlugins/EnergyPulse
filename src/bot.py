import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.config import TELEGRAM_BOT_TOKEN, BUSINESS_NAME, ADMIN_PASSWORD
from src import db
from src.knowledge_base import KnowledgeBase
from src.ai_engine import AIEngine

logger = logging.getLogger(__name__)

kb = KnowledgeBase()
engine = AIEngine(kb)

# Pending admin actions: chat_id -> {"action": ..., ...}
_pending: dict[int, dict] = {}


# ---- Customer Commands ----


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    greeting = db.get_setting(
        "greeting",
        f"Welcome to {BUSINESS_NAME}! I'm an AI assistant here to help you.\n"
        "Just type your question and I'll do my best to answer.\n\n"
        "Type /human if you'd like to speak with a team member.",
    )
    await update.message.reply_text(greeting)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Just send me a message and I'll try to help!\n\n"
        "/human \u2014 Request to speak with a human\n"
        "/start \u2014 Show welcome message"
    )


async def cmd_human(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Escalate to a human agent and notify admins."""
    chat_id = update.effective_chat.id
    db.save_message(chat_id, "user", "[Requested human agent]")

    user = update.effective_user
    name = user.full_name or user.username or str(chat_id)
    for admin_id in db.get_admin_ids():
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"[ESCALATION] {name} (ID: {chat_id}) is requesting human assistance.",
            )
        except Exception:
            pass

    await update.message.reply_text(
        "I've notified the team. A human agent will get back to you shortly."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle free-text messages — admin pending actions or AI reply."""
    chat_id = update.effective_chat.id
    text = update.message.text

    # Check if admin has a pending action
    if chat_id in _pending:
        await _handle_pending(update, context)
        return

    # Regular customer flow: save → AI → reply
    db.save_message(chat_id, "user", text)
    reply = engine.generate_reply(chat_id, text)
    db.save_message(chat_id, "assistant", reply)

    await update.message.reply_text(reply)


# ---- Admin Commands ----


async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if db.is_admin(chat_id):
        await update.message.reply_text(
            "You are logged in as admin.\n\n"
            "/add <title> \u2014 Add knowledge entry\n"
            "/list \u2014 List knowledge base\n"
            "/delete <id> \u2014 Delete an entry\n"
            "/stats \u2014 View statistics\n"
            "/setprompt \u2014 Set custom AI instructions\n"
            "/setgreeting \u2014 Set welcome message"
        )
        return

    if not context.args:
        await update.message.reply_text("Usage: /admin <password>")
        return

    if " ".join(context.args) == ADMIN_PASSWORD:
        db.add_admin(chat_id)
        await update.message.reply_text("Admin access granted.")
    else:
        await update.message.reply_text("Incorrect password.")


async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not db.is_admin(chat_id):
        return
    if not context.args:
        await update.message.reply_text(
            "Usage: /add <title>\nThen send the content in the next message."
        )
        return
    title = " ".join(context.args)
    _pending[chat_id] = {"action": "add_knowledge", "title": title}
    await update.message.reply_text(
        f"Title: {title}\n\nNow send the content."
    )


async def _handle_pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    action = _pending.pop(chat_id)

    if action["action"] == "add_knowledge":
        content = update.message.text
        entry_id = db.add_knowledge(action["title"], content)
        kb.rebuild()
        await update.message.reply_text(
            f"Knowledge entry #{entry_id} added ({len(content)} chars). Index rebuilt."
        )
    elif action["action"] == "set_prompt":
        db.set_setting("system_prompt", update.message.text)
        await update.message.reply_text("Custom system prompt updated.")
    elif action["action"] == "set_greeting":
        db.set_setting("greeting", update.message.text)
        await update.message.reply_text("Welcome message updated.")


async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not db.is_admin(chat_id):
        return
    entries = db.list_knowledge()
    if not entries:
        await update.message.reply_text(
            "Knowledge base is empty. Use /add <title> to add entries."
        )
        return
    lines = [f"#{e['id']} \u2014 {e['title']} ({e['chars']} chars)" for e in entries]
    await update.message.reply_text("Knowledge base:\n\n" + "\n".join(lines))


async def cmd_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not db.is_admin(chat_id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /delete <id>")
        return
    try:
        entry_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID must be a number.")
        return
    if db.delete_knowledge(entry_id):
        kb.rebuild()
        await update.message.reply_text(f"Entry #{entry_id} deleted. Index rebuilt.")
    else:
        await update.message.reply_text(f"Entry #{entry_id} not found.")


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not db.is_admin(chat_id):
        return
    stats = db.get_stats()
    await update.message.reply_text(
        f"Total messages: {stats['total_messages']}\n"
        f"Today: {stats['today_messages']}\n"
        f"Unique users: {stats['unique_users']}\n"
        f"Knowledge entries: {stats['kb_entries']}"
    )


async def cmd_setprompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not db.is_admin(chat_id):
        return
    _pending[chat_id] = {"action": "set_prompt"}
    await update.message.reply_text(
        "Send the custom system prompt for the AI assistant."
    )


async def cmd_setgreeting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not db.is_admin(chat_id):
        return
    _pending[chat_id] = {"action": "set_greeting"}
    await update.message.reply_text("Send the new welcome message for customers.")


def create_bot() -> Application:
    """Build and configure the Telegram bot application."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Customer commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("human", cmd_human))

    # Admin commands
    app.add_handler(CommandHandler("admin", cmd_admin))
    app.add_handler(CommandHandler("add", cmd_add))
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(CommandHandler("delete", cmd_delete))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("setprompt", cmd_setprompt))
    app.add_handler(CommandHandler("setgreeting", cmd_setgreeting))

    # Free-text handler (must be last)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app
