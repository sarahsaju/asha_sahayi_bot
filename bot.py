import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from google import genai

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "നമസ്കാരം 🙏\n"
        "ഞാൻ ASHA സഹായി.\n"
        "ആരോഗ്യ  സംബന്ധമായ വിവരങ്ങൾക്ക് ഞാൻ നിങ്ങളെ സഹായിക്കും. \n"
        "എന്ത് സഹായം വേണമെന്ന് പറയൂ."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=user_text
        )
        reply = response.text

    except Exception:
        reply = (
            "ക്ഷമിക്കണം 🙏\n"
            "ഇപ്പോൾ വിവരങ്ങൾ ലഭ്യമല്ല.\n"
            "ദയവായി കുറച്ച് സമയം കഴിഞ്ഞ് വീണ്ടും ശ്രമിക്കുക."
        )

    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 ASHA Sahayi bot with Gemini is running...")
app.run_polling()
