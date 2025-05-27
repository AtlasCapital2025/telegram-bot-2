import logging
import os 
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
import telegram

TOKEN = os.environ.get("TOKEN")
CHANNEL_USERNAME = "@atlascapitalnews"
GUIDE_FILE_PATH = "Словарь инвестора 1.pdf"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📥 Получить Словарь инвестора", callback_data="get_guide")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Привет, {user.first_name}! Для получения гида нажми на кнопку ниже.",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user.id)
        if member.status in ["member", "administrator", "creator"]:
            await query.message.reply_document(open(GUIDE_FILE_PATH, "rb"))
            await query.message.reply_text("Спасибо за подписку! Вот ваш Словарь инвестора.")
        else:
            raise telegram.error.BadRequest("User not subscribed")
    except telegram.error.BadRequest:
        keyboard = [
            [InlineKeyboardButton("📲 Подписаться", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "📌 Чтобы получить гайд, подпишитесь на наш канал и отправьте сюда любое сообщение.",
            reply_markup=reply_markup
        )

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()

