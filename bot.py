from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "8100918560:AAFO3g_J19HMRfDIWOlULKJN6_PVwCUYkV4"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "നമസ്കാരം 🙏\n"
        "ഞാൻ ആശാ സഹായി.\n"
        "നിങ്ങളെ സഹായിക്കാൻ ഞാൻ ഇവിടെ ഉണ്ട്. \n"
        "എന്ത് സഹായം വേണമെന്ന് പറയൂ."
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

print("🤖 ASHA Sahayi bot is running...")
app.run_polling()
