import logging
import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InputFile,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import telegram

TOKEN = os.environ.get("TOKEN", "7682858607:AAHRRibwvtX5YnJYA3Z_SFGhdIx9z906eIQ")

CHANNEL_USERNAME = "@atlascapitalnews"
GUIDE_FILE_PATH = "6 советов для начинающего инвестора.pdf"

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

async def send_file_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cwd = os.getcwd()
    await update.message.reply_text(f"Текущая директория: {cwd}")

    file_exists = os.path.isfile(GUIDE_FILE_PATH)
    await update.message.reply_text(f"Файл '{GUIDE_FILE_PATH}' найден: {file_exists}")

    if file_exists:
        try:
            with open(GUIDE_FILE_PATH, "rb") as pdf_file:
                input_file = InputFile(pdf_file, filename="6 советов для начинающего инвестора.pdf")
                await update.message.reply_document(document=input_file)
        except Exception as e:
            await update.message.reply_text(f"Ошибка при отправке файла: {e}")
    else:
        await update.message.reply_text("Файл не найден — проверьте наличие PDF в папке бота.")

async def handle_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    При нажатии текстовой кнопки «Старт» показываем инлайн-клавиатуру.
    """
    inline_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📥 Получить «6 советов для начинающего инвестора»",
                    callback_data="get_guide"
                )
            ],
            [
                InlineKeyboardButton(
                    "📲 Подписаться",
                    url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ Проверить подписку",
                    callback_data="check_subscription"
                )
            ],
        ]
    )
    await update.message.reply_text("Выберите действие:", reply_markup=inline_keyboard)

async def button_get_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    При нажатии «get_guide» подсказываем нажать «Проверить подписку».
    """
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Чтобы получить гайд, нажмите «✅ Проверить подписку».")

async def check_subscription_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка нажатия «check_subscription».
    """
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    await check_subscription(query.message, context, user.id)

async def check_subscription(target, context, user_id):
    """
    Проверяем, подписан ли user_id на канал CHANNEL_USERNAME.
    Если подписан — отправляем PDF, иначе — предлагаем подписаться.
    """
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            # Пользователь подписан — отправляем PDF
            with open(GUIDE_FILE_PATH, "rb") as pdf_file:
                input_file = InputFile(pdf_file, filename="6 советов для начинающего инвестора.pdf")
                await target.reply_document(document=input_file)
            await target.reply_text(
                "Благодарим за подписку!\n"
                "Высылаем вам «6 советов для начинающего инвестора»!\n\n"
                "Следите за свежими новостями и аналитикой финансового рынка в нашем канале."
            )
        else:
            raise telegram.error.BadRequest("User not subscribed")
    except telegram.error.BadRequest:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📲 Подписаться",
                        url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "✅ Проверить подписку",
                        callback_data="check_subscription"
                    )
                ],
            ]
        )
        await target.reply_text(
            "📌 Чтобы получить гайд, подпишитесь на канал и нажмите «Проверить подписку».",
            reply_markup=keyboard
        )

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("filetest", send_file_test))

    application.add_handler(CallbackQueryHandler(button_get_guide, pattern="get_guide"))
    application.add_handler(CallbackQueryHandler(check_subscription_button, pattern="check_subscription"))

    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^Старт$"), handle_start_button)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.ChatType.PRIVATE & ~filters.Regex("^Старт$"),
            start
        )
    )

    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
