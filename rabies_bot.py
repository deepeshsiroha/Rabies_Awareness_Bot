# rabies_bot.py
#
# This version of the bot is simplified to be FAQ-only.
# After language selection, it goes directly to the question list.
# This version has been updated to correctly parse Markdown for bold/italic text.
#
# To run this bot:
# 1. Install the library: pip install python-telegram-bot
# 2. Create a file named 'content.json' in the same directory and paste the JSON content into it.
# 3. Get a bot token from Telegram's @BotFather.
# 4. Replace 'YOUR_TELEGRAM_BOT_TOKEN' below with your actual token.
# 5. Run the script: python rabies_bot.py

import json
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, CallbackQuery
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
# --- FIX: Import ParseMode ---
from telegram.constants import ParseMode

# --- Setup Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Load Content ---
try:
    with open("content.json", "r", encoding="utf-8") as f:
        content = json.load(f)
except FileNotFoundError:
    print("Error: content.json not found. Please create it.")
    exit()
except json.JSONDecodeError:
    print("Error: Could not decode content.json. Please check its format.")
    exit()

# --- Define Conversation States ---
SELECTING_LANG, FAQ_PATH = range(2)

# === Helper Functions ===

def get_text(key: str, lang: str = "en") -> str:
    """Fetches a text string from the content dictionary for the selected language."""
    return content.get(lang, {}).get(key, f"Error: Key '{key}' not found.")

def get_button_text(key: str, lang: str = "en") -> str:
    """Fetches a button text string."""
    return content.get(lang, {}).get("buttons", {}).get(key, f"Error: Btn '{key}' not found.")

def get_button_text_from_callback(query: CallbackQuery) -> str:
    """Finds the text of the button that was pressed from the query's reply_markup."""
    if not query.message or not query.message.reply_markup:
        return ""
    for row in query.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data == query.data:
                return button.text
    return ""

# === Bot Command and Message Handlers ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user to select a language."""
    welcome_text = (
        f"{get_text('welcome', 'en')}\n\n"
        f"{get_text('welcome', 'hi')}\n\n"
        f"{get_text('select_language', 'en')} / {get_text('select_language', 'hi')}"
    )
    keyboard = [
        [
            InlineKeyboardButton(get_button_text('lang_en', 'en'), callback_data='lang_en'),
            InlineKeyboardButton(get_button_text('lang_hi', 'hi'), callback_data='lang_hi'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        # --- FIX: Added parse_mode ---
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    elif update.callback_query:
        # --- FIX: Added parse_mode ---
        await update.callback_query.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

    return SELECTING_LANG

async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes the language selection and goes directly to the FAQ list."""
    query = update.callback_query
    await query.answer()
    lang = query.data.split('_')[1]
    context.user_data['lang'] = lang

    button_text = get_button_text_from_callback(query)
    
    await query.edit_message_reply_markup(reply_markup=None)
    if button_text:
        # --- FIX: Added parse_mode ---
        await query.edit_message_text(text=f"*{get_text('selection_confirmation', lang)}* {button_text}", parse_mode=ParseMode.MARKDOWN)

    # Directly call the function to show the FAQ list
    return await faq_path_start(update, context)


async def faq_path_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays the list of frequently asked questions."""
    query = update.callback_query
    lang = context.user_data.get('lang', 'en')
    faq_content = get_text('faq', lang)

    keyboard = [
        [InlineKeyboardButton(faq_content.get('what_is_rabies_q'), callback_data='faq_what_is_rabies')],
        [InlineKeyboardButton(faq_content.get('first_aid_q'), callback_data='faq_first_aid')],
        [InlineKeyboardButton(faq_content.get('prevention_q'), callback_data='faq_prevention')],
        [InlineKeyboardButton(faq_content.get('myths_facts_q'), callback_data='faq_myths_facts')],
        [InlineKeyboardButton(faq_content.get('emergency_assistance_q'), callback_data='faq_emergency_assistance')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_text = get_text('faq_prompt', lang)
    
    # Send a new message with the FAQ list
    # --- FIX: Added parse_mode ---
    await query.message.reply_text(text=message_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    return FAQ_PATH

async def faq_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Provides an answer to a selected FAQ."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'en')

    button_text = get_button_text_from_callback(query)
    await query.edit_message_reply_markup(reply_markup=None)
    if button_text:
        # --- FIX: Added parse_mode ---
        await query.message.reply_text(f"*{get_text('selection_confirmation', lang)}* {button_text}", parse_mode=ParseMode.MARKDOWN)
    
    question_key = query.data.replace('faq_', '') + '_a'
    answer_text = get_text('faq', lang).get(question_key, "Sorry, I don't have an answer for that.")

    keyboard = [
        [InlineKeyboardButton(get_button_text('ask_another', lang), callback_data='faq_menu')],
        [InlineKeyboardButton(get_button_text('end_chat', lang), callback_data='end_chat')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # --- FIX: Added parse_mode ---
    await query.message.reply_text(text=answer_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    return FAQ_PATH

async def end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ends the conversation."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'en')

    button_text = get_button_text_from_callback(query)
    await query.edit_message_reply_markup(reply_markup=None)
    if button_text:
        # --- FIX: Added parse_mode ---
        await query.message.reply_text(f"*{get_text('selection_confirmation', lang)}* {button_text}", parse_mode=ParseMode.MARKDOWN)
    
    # --- FIX: Added parse_mode ---
    await query.message.reply_text(text=get_text('end_chat_message', lang), parse_mode=ParseMode.MARKDOWN)
    return ConversationHandler.END

async def text_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles any text input from the user when they should be clicking buttons."""
    lang = context.user_data.get('lang', 'en')
    # --- FIX: Added parse_mode ---
    await update.message.reply_text(get_text('error_handler', lang), parse_mode=ParseMode.MARKDOWN)

def main() -> None:
    """Run the bot."""
    application = Application.builder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_LANG: [CallbackQueryHandler(select_language, pattern="^lang_")],
            FAQ_PATH: [
                CallbackQueryHandler(faq_path_start, pattern="^faq_menu$"),
                CallbackQueryHandler(faq_answer, pattern="^faq_"),
                CallbackQueryHandler(end_chat, pattern="^end_chat$"),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, text_fallback)
        ],
    )

    application.add_handler(conv_handler)

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
