import os
import re
import logging

from telegram import Update, ChatPermissions
from telegram.ext import Application, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

CHINESE_REGEX = re.compile(r"[\u4e00-\u9fff]")

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not found")


def contains_chinese(text: str) -> bool:
    return bool(CHINESE_REGEX.search(text))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text or ""

    if contains_chinese(text):
        try:
            user = update.effective_user
            chat = update.effective_chat

            logger.info(
                f"Deleting message and permanently muting "
                f"{user.username or user.id} in {chat.title or chat.id}: {text}"
            )

            await update.message.delete()

            await context.bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=user.id,
                permissions=ChatPermissions()
            )

        except Exception as e:
            logger.error(f"Failed to moderate user: {e}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    logger.info("Bot started")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
