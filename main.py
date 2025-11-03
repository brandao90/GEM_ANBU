from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os, threading, time, datetime

# --- Flask app (para Render + UptimeRobot)
app = Flask(__name__)
start_time = time.time()  # Marca o início da execução

@app.route('/')
def home():
    return "GEM_ANBU v8.2 ✅ Bot + Keep Alive + Status ativo"

@app.route('/healthz')
def healthz():
    return "OK", 200

# --- Funções de Comandos Telegram ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 GEM_ANBU está ativo e monitorando 24/7!")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📜 Comandos disponíveis:\n/start - Inicia o bot\n/help - Ajuda\n/status - Mostra status e uptime")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = str(datetime.timedelta(seconds=int(time.time() - start_time)))
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    msg = (
        "🟢 *Status do GEM_ANBU*\n"
        f"⏰ Hora atual: `{now}`\n"
        f"📶 Uptime: `{uptime}`\n"
        f"✅ Status: *Online e funcionando*"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# --- Bot Telegram ---
def run_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ Erro: TELEGRAM_BOT_TOKEN não encontrado!")
        return

    app_telegram = ApplicationBuilder().token(token).build()
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CommandHandler("help", help))
    app_telegram.add_handler(CommandHandler("status", status))

    print("🤖 Bot Telegram iniciado com sucesso!")
    app_telegram.run_polling()

# --- Executa o bot em thread separada ---
if os.getenv("KEEP_ALIVE", "False") == "True":
    threading.Thread(target=run_bot).start()
    print("✅ Thread do bot iniciada")

# --- Executa o Flask (Render inicia aqui) ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
