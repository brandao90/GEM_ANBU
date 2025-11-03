from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os, threading

# --- Flask app (para o Render e o UptimeRobot)
app = Flask(__name__)

@app.route('/')
def home():
    return "GEM_ANBU v8.1 24/7 ATIVO"

@app.route('/healthz')
def healthz():
    return "OK", 200

# --- Bot Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 GEM_ANBU está ativo e monitorando 24/7!")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Comandos disponíveis:\n/start - Inicia o bot\n/help - Ajuda")

def run_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ Erro: TELEGRAM_BOT_TOKEN não encontrado!")
        return

    app_telegram = ApplicationBuilder().token(token).build()
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CommandHandler("help", help))

    print("🤖 Bot Telegram iniciado com sucesso!")
    app_telegram.run_polling()

# --- Executa o bot em uma thread separada
if os.getenv("KEEP_ALIVE", "False") == "True":
    threading.Thread(target=run_bot).start()
    print("✅ Thread do bot iniciada")

# --- Executa o Flask (Render inicia por aqui)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
