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

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
TOKEN = os.environ.get("TOKEN", "your-token-here")
CHANNEL_USERNAME = "@atlascapitalnews"
# Обновили имя файла, который будет отправляться пользователю
GUIDE_FILE_PATH = "Словарь инвестора.pdf"

# ----------------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ----------------------------------------------------------------------------
# Keyboards
# ----------------------------------------------------------------------------
reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton("Старт")]],
    resize_keyboard=True
)

# ----------------------------------------------------------------------------
# Handlers
# ----------------------------------------------------------------------------
async def show_start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляем приветственное сообщение и кнопку «Старт»."""
    await update.message.reply_text(
        "Приветствуем Вас! Нажмите «Старт», чтобы открыть меню.",
        reply_markup=reply_keyboard
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_start_menu(update, context)

async def handle_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показываем inline‑меню после нажатия кнопки «Старт»."""
    inline_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Получить «Словарь инвестора»", callback_data="get_guide")],
        [InlineKeyboardButton("📲 Подписаться", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_subscription")]
    ])

    await update.message.reply_text("Выберите действие:", reply_markup=inline_keyboard)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатываем нажатие «Получить гайд»."""
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    await check_subscription(query.message, context, user.id)

async def check_subscription_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатываем нажатие «Проверить подписку»."""
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    await check_subscription(query.message, context, user.id)

async def check_subscription(target, context, user_id):
    """Проверяем подписку и отправляем гайд или просим подписаться."""
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            # Отправляем PDF‑файл «Словарь инвестора»
            await target.reply_document(open(GUIDE_FILE_PATH, "rb"))
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

# ----------------------------------------------------------------------------
# Application entry point
# ----------------------------------------------------------------------------

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Команды
    application.add_handler(CommandHandler("start", start))

    # Inline‑кнопки
    application.add_handler(CallbackQueryHandler(button, pattern="get_guide"))
    application.add_handler(CallbackQueryHandler(check_subscription_button, pattern="check_subscription"))

    # Сообщения
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Старт$"), handle_start_button))

    # Любой другой текст в личном чате — показываем стартовое меню
    application.add_handler(MessageHandler(
        filters.TEXT & filters.ChatType.PRIVATE & ~filters.Regex("^Старт$"),
        show_start_menu
    ))

    print("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()
