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
import re

def extract_age(text: str) -> int | None:
    """
    Extracts a simple age number from text like:
    '10', '10 വയസ്', '10 years', '10 വർഷം', '10 മാസം', '10 months','10 vayass', etc.
    """
    match = re.search(r"\b(\d{1,2})\b", text)
    if match:
        return int(match.group(1))
    return None

MEDICATION_KEYWORDS = [
    "tablet", "ഗുളിക", "medicine", "മരുന്ന്", "dose", "ഡോസ്",
    "mg", "ml", "എത്ര", "എത്ര mg", "how much", "antibiotic",
    "പാരാസെറ്റമോൾ", "paracetamol", "ibuprofen"
]
NEGATIVE_KEYWORDS = [
    "illa", "ഇല്ല", "no", "illa illa", "illa aanu"
]

def is_medication_query(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in MEDICATION_KEYWORDS)
def medication_refusal_message() -> str:
    return (
        "ക്ഷമിക്കണം 🙏\n\n"
        "മരുന്നുകളുടെ പേര്, ഡോസ്, അല്ലെങ്കിൽ ഏത് ഗുളിക എന്ന് പറയാൻ എനിക്ക് കഴിയില്ല.\n\n"
        "ദയവായി അടുത്തുള്ള PHC / ഡോക്ടറെ സമീപിക്കുക.\n\n"
        "ഇത് ASHA പ്രവർത്തകരുടെ സുരക്ഷയ്ക്കും രോഗികളുടെ സുരക്ഷയ്ക്കുമാണ്."
    )
def needs_clarification(text: str, user_data: dict) -> str | None:
    text = text.lower()

    # AGE
    if "age" not in user_data:
        age = extract_age(text)
        if age:
            user_data["age"] = age
        else:
            return "കുഞ്ഞിന്റെ ഏകദേശം വയസ് എത്രയാണ്?"

    # DURATION
    if "duration" not in user_data:
        duration_keywords = ["ദിവസം", "മണിക്കൂർ", "since", "days", "hours"]
        if any(k in text for k in duration_keywords) or extract_age(text):
            user_data["duration"] = True
        else:
            return "ഈ പ്രശ്നം എത്ര സമയമായി തുടരുന്നു?"

    # DANGER SIGNS
    if "danger_checked" not in user_data:
        danger_keywords = ["ശ്വാസം", "fits", "വയറിളക്കം", "ഛർദ്ദി", "ബോധം"]
        negative_keywords = ["illa", "ഇല്ല", "no"]
        if any(k in text for k in danger_keywords):
            user_data["danger_checked"] = True
        elif any(k in text for k in negative_keywords):
            user_data["danger_checked"] = True
            user_data["no_danger"] = True
        else:
            return "ശ്വാസം എടുക്കാൻ ബുദ്ധിമുട്ട്, ഫിറ്റ്സ്, അല്ലെങ്കിൽ അമിത ക്ഷീണം ഉണ്ടോ?"

    

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
SAFETY_PROMPT = """
You are ASHA Sahayi, a support assistant for ASHA health workers in India.

STRICT RULES:
- Do NOT diagnose any disease
- Do NOT mention medicine names
- Do NOT mention dosages
- Do NOT suggest treatment
- give advice only for common, minor ailments
- give guidance like what we we can do at home for the time being like staying hydrated, rest, etc.
- Give only general guidance and observation points
- Ask to check for danger signs (red flags)
- Always suggest referral to PHC or doctor when needed
- Use simple, respectful Malayalam
- Keep response short and actionable
- Use Indian public health context

Structure your response as:
1. Short reassurance
2. What to observe (2–3 points)
3. Red flag symptoms (bullet points)
4. Clear referral advice
5. Disclaimer sentence

Never break these rules.
"""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # 1️⃣ Medication safety filter
    if is_medication_query(user_text):
        await update.message.reply_text(medication_refusal_message())
        return

    # 2️⃣ Ask-before-advise (minimal)
    clarification = needs_clarification(user_text, context.user_data)

    if clarification:
        await update.message.reply_text(
            clarification + "\n\n"
            "ഈ വിവരങ്ങൾ ലഭിച്ചാൽ കൂടുതൽ സുരക്ഷിതമായി മാർഗ്ഗനിർദ്ദേശം നൽകാൻ കഴിയും."
        )
        return

    # 3️⃣ Safe AI guidance
    try:
        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=SAFETY_PROMPT + "\n\nUser query:\n" + user_text
        )
        reply = response.text.strip()
    except Exception:
        reply = (
            "ക്ഷമിക്കണം 🙏\n"
            "ഇപ്പോൾ വിവരങ്ങൾ ലഭ്യമല്ല.\n"
            "ദയവായി PHC ഡോക്ടറെ സമീപിക്കുക."
        )

    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 ASHA Sahayi bot with Gemini is running...")
app.run_polling()
