import os
from dotenv import load_dotenv
from db import init_db, save_visit, get_all_visits
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
    context.user_data.clear()
    await update.message.reply_text(
        "നമസ്കാരം 🙏\n"
        "ഞാൻ ASHA സഹായി.\n"
        "ആരോഗ്യ സംബന്ധമായ വിവരങ്ങൾക്ക് ഞാൻ നിങ്ങളെ സഹായിക്കും.\n"
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
async def log_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "worker_id" not in context.user_data:
        await update.message.reply_text(
            "ആദ്യം Worker ID സെറ്റ് ചെയ്യുക.\nഉദാ: /setworker ASHA_12"
        )
        return

    context.user_data["log"] = {}
    context.user_data["log_step"] = 0

    await update.message.reply_text(
        "📝 Patient Visit Logging ആരംഭിക്കുന്നു.\n\n"
        "രോഗിയെ തിരിച്ചറിയാൻ ഒരു ലേബൽ നൽകുക (ഉദാ: Amma veedu / R.K):"
    )

async def log_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "log" not in context.user_data:
        return

    step = context.user_data["log_step"]
    field = LOGGING_STEPS[step]

    context.user_data["log"][field] = update.message.text
    context.user_data["log_step"] += 1

    if context.user_data["log_step"] < len(LOGGING_STEPS):
        next_field = LOGGING_STEPS[context.user_data["log_step"]]

        prompts = {
            "age_group": "വയസ് വിഭാഗം (0–5 / 6–18 / Adult):",
            "complaint": "പ്രധാന പരാതിയ്‌ക്ക് ഒരു വാക്ക്:",
            "danger_signs": "അപകട സൂചനകൾ ഉണ്ടോ? (ഉണ്ട് / ഇല്ല):",
            "referral": "PHC റഫറൽ നൽകിയോ? (അതെ / ഇല്ല):",
            "notes": "കുറിപ്പുകൾ (ഐച്ഛികം):"
        }

        await update.message.reply_text(prompts.get(next_field, "അടുത്ത വിവരങ്ങൾ നൽകുക:"))
        return

    # Save to DB
    data = context.user_data["log"]
    worker_id = context.user_data["worker_id"]
    save_visit(
        worker_id,
        data["visit_date"],
        data["patient_label"],
        data["age_group"],
        data["complaint"],
        data["danger_signs"],
        data["referral"],
        data["notes"]
        )
    context.user_data.pop("log", None)
    context.user_data.pop("log_step", None)

    await update.message.reply_text(
        "✅ സന്ദർശന വിവരങ്ങൾ സുരക്ഷിതമായി സേവ് ചെയ്തു."
        )


    


async def set_worker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        context.user_data["worker_id"] = context.args[0]
        await update.message.reply_text(
            f"✅ Worker ID set: {context.args[0]}"
        )
    else:
        await update.message.reply_text(
            "ദയവായി Worker ID നൽകുക.\nഉദാ: /setworker ASHA_12"
        )
async def view_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = get_all_visits()

    if not rows:
        await update.message.reply_text("ഇപ്പോൾ ലോഗുകൾ ഇല്ല.")
        return

    message = "📋 Visit Logs:\n\n"
    for row in rows[-5:]:
        message += (
            f"Worker: {row[1]}, "
            f"Date: {row[2]}, "
            f"Patient: {row[3]}, "
            f"Issue: {row[5]}, "
            f"Referral: {row[7]}\n"
        )

    await update.message.reply_text(message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 🚫 If logging is active, AI must stay silent
    if "log" in context.user_data:
        return

    if not update.message or not update.message.text:
        return

    user_text = update.message.text.strip()

    # 🔴 Medication safety filter
    if is_medication_query(user_text):
        context.user_data.clear()
        await update.message.reply_text(medication_refusal_message())
        return

    # 🟡 Ask-before-advise
    clarification = needs_clarification(user_text, context.user_data)
    if clarification:
        await update.message.reply_text(
            clarification + "\n\n"
            "ഈ വിവരങ്ങൾ ലഭിച്ചാൽ കൂടുതൽ സുരക്ഷിതമായി മാർഗ്ഗനിർദ്ദേശം നൽകാൻ കഴിയും."
        )
        return

    # 🟢 Safe AI guidance
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


LOGGING_STEPS = [
    "patient_label",
    "visit_date",
    "age_group",
    "complaint",
    "danger_signs",
    "referral",
    "notes"
]

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("setworker", set_worker))
app.add_handler(CommandHandler("log", log_start))
app.add_handler(CommandHandler("logs", view_logs))

# Group 0 → logging flow (higher priority)
app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, log_handler),
    group=0
)

# Group 1 → AI fallback (lower priority)
app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
    group=1
)

print("🤖 ASHA Sahayi bot with Gemini is running...")
init_db()
app.run_polling()
