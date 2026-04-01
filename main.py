import os
import logging 
from dotenv import load_dotenv 
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Importando handlers
from src.bot.handlers import start_handler, cadastro_manual_handler, agent_handler, voice_handler

# Configuração de logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if __name__ == '__main__':
    if not TOKEN:
        logging.error("TELEGRAM_TOKEN não encontrado no arquivo .env")
        exit(1)

    # Cria a aplicação do bot
    application = ApplicationBuilder().token(TOKEN).build()

    # Registra os comandos e respostas
    # IMPORTANTE: Use 'start' em minúsculo
    application.add_handler(CommandHandler('start', start_handler))
    application.add_handler(CommandHandler('cadastrar', cadastro_manual_handler))
    
    # Handler para mensagens de texto (IA)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), agent_handler))
    
    # Handler para mensagens de voz
    application.add_handler(MessageHandler(filters.VOICE, voice_handler))
    
    print("🚀 Bot iniciado com sucesso! Pressione Control+C para parar.")
    application.run_polling()