import os
import zipfile
import tempfile
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask
from threading import Thread

TOKEN = "7626980768:AAHHU8CT1YXKcVkEbOVStY04D4DxNSwe29M"
PROJECTS_DIR = "codes"  # Projects folder

# ====== (1) Web server to keep Replit alive ======
app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot is alive!"

def run():
    app_web.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ====== (2) Telegram bot handlers ======

# /start - show projects
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    projects = [f for f in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, f))]

    if not projects:
        await update.message.reply_text("🚫 No projects available currently.")
        return

    buttons = [[p] for p in projects]
    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("👋 Please select a project to download its files:", reply_markup=markup)

# Send the project as a zip file
async def send_project_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    project_name = update.message.text.strip()
    project_path = os.path.join(PROJECTS_DIR, project_name)

    if not os.path.isdir(project_path):
        await update.message.reply_text("⚠️ Project not found!")
        return

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        zip_path = tmp.name
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, _, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, project_path)
                    zipf.write(file_path, arcname)

    await update.message.reply_document(document=open(zip_path, "rb"), filename=f"{project_name}.zip")
    os.remove(zip_path)

# ====== (3) Run everything ======

if __name__ == "__main__":
    keep_alive()  # start the Flask web server
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_project_zip))
    app.run_polling()
