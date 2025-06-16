# 🤖 CRYPTOBOT: Roda automaticamente todos os dias
import requests
from binance.client import Client
import time
import schedule
import datetime
import os
from dotenv import load_dotenv  # Importa dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# 🔐 Pega variáveis de ambiente configuradas no .env
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# 🔗 Conecta com Binance
client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)

# 📲 Envia mensagem no Telegram
def send_telegram_message(msg):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': msg}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

# 💰 Operação simulada diária
def simular_trade_diaria(par='BTCUSDT', investimento=5, lucro_esperado=1):
    try:
        preco_atual = float(client.get_symbol_ticker(symbol=par)['price'])
    except Exception as e:
        send_telegram_message("❌ Erro ao obter o preço da Binance")
        return

    preco_compra = preco_atual
    preco_venda = preco_compra + lucro_esperado / investimento

    send_telegram_message(f'📅 {datetime.datetime.now().strftime("%d/%m %H:%M")} - CRYPTOBOT iniciou operação com {par}')
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

        if tentativas > 288:  # 288 x 5min ≈ 24 horas
            send_telegram_message("⌛ Tempo excedido. Operação encerrada sem atingir o alvo.")
            break

        time.sleep(300)  # Espera 5 minutos entre checagens

# 🕒 Agenda execução diária às 9h da manhã
schedule.every().day.at("09:00").do(simular_trade_diaria)

# 🔄 Loop principal
send_telegram_message("🤖 CRYPTOBOT AUTÔNOMO INICIADO!")

while True:
    schedule.run_pending()
    time.sleep(1)
