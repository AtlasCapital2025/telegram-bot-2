import logging
import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InputFile
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
import telegram

TOKEN = os.environ.get("TOKEN", "your-token-here")
CHANNEL_USERNAME = "@atlascapitalnews"
GUIDE_FILE_PATH = "Словарь инвестора.pdf"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton("Старт")]],
    resize_keyboard=True
)

async def show_start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Приветствуем Вас! Нажмите «Старт», чтобы открыть меню.",
        reply_markup=reply_keyboard
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_start_menu(update, context)

async def handle_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inline_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Получить «Словарь инвестора»", callback_data="get_guide")],
        [InlineKeyboardButton("📲 Подписаться", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_subscription")]
    ])

    await update.message.reply_text("Выберите действие:", reply_markup=inline_keyboard)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    await check_subscription(query.message, context, user.id)

async def check_subscription_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    await check_subscription(query.message, context, user.id)

async def check_subscription(target, context, user_id):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            with open(GUIDE_FILE_PATH, "rb") as pdf_file:
                await target.reply_document(
                    document=InputFile(pdf_file, filename="Словарь инвестора.pdf")
                )
            await target.reply_text(
                "Благодарим за подписку! \n"
                "Высылаем вам «Словарь инвестора»\n\n"
                "Следите за свежими новостями и аналитикой финансового рынка в нашем канале."
            )
        else:
            raise telegram.error.BadRequest("User not subscribed")
    except telegram.error.BadRequest:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📲 Подписаться", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
            [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_subscription")]
        ])
        await target.reply_text(
            "📌 Чтобы получить гайд, подпишитесь на канал и нажмите «Проверить подписку».",
            reply_markup=keyboard
        )

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button, pattern="get_guide"))
    application.add_handler(CallbackQueryHandler(check_subscription_button, pattern="check_subscription"))

    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Старт$"), handle_start_button))

    application.add_handler(MessageHandler(
        filters.TEXT & filters.ChatType.PRIVATE & ~filters.Regex("^Старт$"),
        show_start_menu
    ))

    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
