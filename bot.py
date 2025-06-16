# 🤖 CRYPTOBOT: Roda automaticamente todos os dias
import requests
from binance.client import Client
import time
import schedule
import datetime
import os
import threading
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Carrega variáveis do .env
load_dotenv()

# 🔐 Credenciais
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# 🔗 Conecta com Binance
client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)

# 📲 Envia mensagem no Telegram (modo requests)
def send_telegram_message(msg):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': msg}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

# 💰 Operação simulada de trade
def simular_trade_diaria(par='BTCUSDT', investimento=5, lucro_esperado=1):
    try:
        preco_atual = float(client.get_symbol_ticker(symbol=par)['price'])
    except Exception as e:
        send_telegram_message(f"❌ Erro ao obter o preço da Binance para {par}")
        return

    preco_compra = preco_atual
    preco_venda = preco_compra + lucro_esperado / investimento

    send_telegram_message(f'📅 {datetime.datetime.now().strftime("%d/%m %H:%M")} - Operação com {par} iniciada')
    send_telegram_message(f'🟢 Compra simulada a ${preco_compra:.2f}')
    send_telegram_message(f'🎯 Alvo de venda: ${preco_venda:.2f}')

    tentativas = 0
    while True:
        try:
            preco_atual = float(client.get_symbol_ticker(symbol=par)['price'])
            tentativas += 1
            print(f'[{tentativas}] Verificando preço: ${preco_atual:.2f}')
        except Exception as e:
            print("Erro ao verificar preço:", e)
            time.sleep(10)
            continue

        if preco_atual >= preco_venda:
            send_telegram_message(f'✅ VENDA simulada a ${preco_atual:.2f}! Lucro de $1 realizado.')
            break

        if tentativas > 288:  # 24 horas
            send_telegram_message("⌛ Tempo excedido. Operação encerrada sem atingir o alvo.")
            break

        time.sleep(300)

# 🎯 Comandos do Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 CRYPTOBOT está online e pronto para operar!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now().strftime("%d/%m %H:%M")
    await update.message.reply_text(f"📈 Bot ativo - {now}")

async def preco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("❗ Use: /preco BTCUSDT")
        return
    par = context.args[0].upper()
    try:
        preco_atual = float(client.get_symbol_ticker(symbol=par)['price'])
        await update.message.reply_text(f"💲 Preço atual de {par}: ${preco_atual:.2f}")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao buscar preço de {par}")

# ✅ Novo comando: /simular
async def simular(update: Update, context: ContextTypes.DEFAULT_TYPE):
    par = context.args[0].upper() if context.args else 'BTCUSDT'
    await update.message.reply_text(f"🚀 Iniciando simulação com {par}. Acompanhe as atualizações no grupo.")
    threading.Thread(target=simular_trade_diaria, args=(par,), daemon=True).start()

# 🔄 Loop de agendamento
def executar_agendamentos():
    schedule.every().day.at("09:00").do(simular_trade_diaria)
    send_telegram_message("🤖 CRYPTOBOT AUTÔNOMO INICIADO!")

    while True:
        schedule.run_pending()
        time.sleep(1)

# 🚀 Início
if __name__ == '__main__':
    threading.Thread(target=executar_agendamentos, daemon=True).start()

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("preco", preco))
    app.add_handler(CommandHandler("simular", simular))

    app.run_polling()
