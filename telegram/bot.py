import os
import zipfile
import tempfile
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🟢 نقرأ التوكن من متغير بيئة بدل كتابته في الكود مباشرة
TOKEN = os.environ["TOKEN"]

PROJECTS_DIR = "codes"  # مجلد المشاريع

# /start - عرض المشاريع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    projects = [f for f in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, f))]

    if not projects:
        await update.message.reply_text("🚫 لا توجد مشاريع حالياً.")
        return

    buttons = [[p] for p in projects]
    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("👋 اختر مشروع لتحميل ملفاته:", reply_markup=markup)

# إرسال المشروع كملف zip
async def send_project_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    project_name = update.message.text.strip()
    project_path = os.path.join(PROJECTS_DIR, project_name)

    if not os.path.isdir(project_path):
        await update.message.reply_text("⚠️ لم يتم العثور على المشروع!")
        return

    # إنشاء ملف zip مؤقت
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        zip_path = tmp.name
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, _, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, project_path)
                    zipf.write(file_path, arcname)

    # إرسال الملف
    await update.message.reply_document(document=open(zip_path, "rb"), filename=f"{project_name}.zip")
    os.remove(zip_path)

# إعداد وتشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_project_zip))

if __name__ == "__main__":
    app.run_polling()
