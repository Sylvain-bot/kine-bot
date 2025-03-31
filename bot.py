import asyncio
import os
import json
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from sheets_helper import find_patient, find_patient_by_phone
from openai_helper import generate_response

# 🔐 Token sécurisé via variables d’environnement
TOKEN = os.environ.get("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_button = KeyboardButton("📱 Partager mon numéro", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Pour vous identifier automatiquement, veuillez partager votre numéro 👇", reply_markup=reply_markup)

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_number = update.message.contact.phone_number
    chat_id = update.effective_chat.id
    print(f"📲 Numéro reçu : {phone_number} (chat ID: {chat_id})")

    patient = find_patient_by_phone(phone_number)
    if patient:
        context.user_data["patient"] = patient
        response = (
            f"👋 Bonjour {patient['prenom']} !\n"
            f"✅ Vous avez été identifié automatiquement.\n\n"
            f"📅 Exercice du jour : {patient['exercice_du_jour']}\n"
            f"📌 Remarques : {patient['remarques']}"
        )
    else:
        response = "Veuillez d’abord m’indiquer votre prénom ou partager votre numéro de téléphone 📱."

    await update.message.reply_text(response)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    chat_id = update.effective_chat.id
    print(f"📩 [{chat_id}] Message reçu :", user_input)

    patient = find_patient(user_input)
    if patient:
        context.user_data["patient"] = patient
        response = (
            f"👋 Bonjour {patient['prenom']} !\n\n"
            f"📅 Exercice du jour : {patient['exercice_du_jour']}\n"
            f"📌 Remarques : {patient['remarques']}\n\n"
            f"❓ Vous pouvez maintenant me poser une question."
        )
    else:
        patient = context.user_data.get("patient")
        if patient:
            contexte = patient.get("contexte_patient", "")
            nom_fichier = f"history_{patient['prenom'].lower()}.json"
            response = generate_response(contexte, user_input, nom_fichier)
        else:
            response = ask_anythingllm(user_input)

    await update.message.reply_text(response)

if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()

    async def main():
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        print("✅ Bot démarré sur Render")
        await app.run_polling()

    asyncio.get_event_loop().run_until_complete(main())
