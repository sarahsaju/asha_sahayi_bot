from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8100918560:AAFO3g_J19HMRfDIWOlULKJN6_PVwCUYkV4"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "നമസ്കാരം 🙏\n"
        "ഞാൻ ASHA സഹായി ആണ്.\n"
        "ആരോഗ്യ വിവരങ്ങൾക്ക് ഞാൻ നിങ്ങളെ സഹായിക്കും. \n"
        "എന്ത് സഹായം വേണമെന്ന് പറയൂ."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    reply = (
        "നിങ്ങളുടെ സന്ദേശം ലഭിച്ചു.\n"
        "ഇപ്പോൾ ഞാൻ പരിശീലന ഘട്ടത്തിലാണ്.\n"
        "ഉടൻ തന്നെ ആരോഗ്യ വിവരങ്ങൾ നൽകാൻ കഴിയും."
    )

    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 ASHA Sahayi bot is running...")
app.run_polling()
