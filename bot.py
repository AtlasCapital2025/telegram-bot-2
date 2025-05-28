import logging
import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
import telegram

TOKEN = os.environ.get("TOKEN", "your-token-here")
CHANNEL_USERNAME = "@atlascapitalnews"
GUIDE_FILE_PATH = "Словарь инвестора 1.pdf"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("Старт")]],
        resize_keyboard=True
    )

    inline_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Получить Словарь инвестора", callback_data="get_guide")]
    ])

    await update.message.reply_text(
        f"Привет, {user.first_name}! Для получения гида нажми на кнопку ниже.",
        reply_markup=reply_keyboard
    )

    await update.message.reply_text("⬇️", reply_markup=inline_keyboard)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    await check_subscription(query.message, context, user.id)

async def handle_check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await check_subscription(update.message, context, user.id)

async def check_subscription(target, context, user_id):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            await target.reply_document(open(GUIDE_FILE_PATH, "rb"))
            await target.reply_text("Спасибо за подписку! Вот ваш Словарь инвестора.")
        else:
            raise telegram.error.BadRequest("User not subscribed")
    except telegram.error.BadRequest:
        keyboard = [
            [InlineKeyboardButton("📲 Подписаться", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
            [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await target.reply_text(
            "📌 Чтобы получить гайд, подпишитесь на канал и нажмите «Проверить подписку».",
            reply_markup=reply_markup
        )

async def check_subscription_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    await check_subscription(query.message, context, user.id)

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button, pattern="get_guide"))
    application.add_handler(CallbackQueryHandler(check_subscription_button, pattern="check_subscription"))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Старт$"), handle_check_subscription))

    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
