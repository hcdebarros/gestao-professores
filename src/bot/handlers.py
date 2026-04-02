import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from src.services.sheets_service import SheetsService
from src.services.calendar_service import CalendarService
from src.services.ai_service import AIService

# Inicialização dos serviços
sheets = SheetsService("aulas")
ai_assistant = AIService()
calendar = CalendarService()
load_dotenv()

MEU_ID = int(os.getenv("MEU_ID_TELEGRAM", 0))

def usuario_autorizado(update: Update) -> bool:
    """Verifica se quem mandou a mensagem é o dono do bot."""
    return update.effective_user.id == MEU_ID

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not usuario_autorizado(update):
        await update.message.reply_text("⛔ Desculpe, este é um bot de gestão privada. Acesso negado.")
        return # Encerra a função aqui mesmo

    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Olá {user_name}! Sou seu assistente de gestão.\n\n"
        "🎙️ Pode me mandar um áudio ou texto"
    )

async def cadastro_manual_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Versão corrigida para usar o sistema de valor fixo.
    Formato: /cadastrar Nome, DD/MM/AAAA, Horas
    """
    if not usuario_autorizado(update):
        await update.message.reply_text("⛔ Desculpe, este é um bot de gestão privada. Acesso negado.")
        return # Encerra a função aqui mesmo
    
    texto = " ".join(context.args)
    if not texto:
        await update.message.reply_text("⚠️ Use: /cadastrar Nome, Data, Horas\nEx: /cadastrar Bruno, 01/04/2026, 2")
        return

    try:
        partes = [p.strip() for p in texto.split(",")]
        if len(partes) < 3: raise ValueError("Faltam dados.")

        nome, data_str, horas = partes[0], partes[1], float(partes[2])
        data_obj = datetime.strptime(data_str, "%d/%m/%Y")

        # USANDO O MÉTODO NOVO (Busca valor fixo automaticamente)
        sucesso, info = sheets.cadastrar_aula_aluno(nome, data_obj, horas)
        
        if sucesso:
            await update.message.reply_text(f"✅ Registrado: {nome} | {horas}h (Valor/h: R${info})")
        elif info == "valor_nao_encontrado":
            await update.message.reply_text(f"⚠️ Aluno {nome} sem valor fixo cadastrado.")
        else:
            await update.message.reply_text(f"❌ Erro: {info}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Erro de formato: {e}")

async def agent_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not usuario_autorizado(update):
        await update.message.reply_text("⛔ Desculpe, este é um bot de gestão privada. Acesso negado.")
        return # Encerra a função aqui mesmo
    
    await processar_texto_e_salvar(update.message.text, update, context)

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not usuario_autorizado(update):
        await update.message.reply_text("⛔ Acesso negado. Este bot é privado.")
        return
    
    await update.message.reply_chat_action("record_voice")
    try:
        file_id = update.message.voice.file_id
        new_file = await context.bot.get_file(file_id)
        os.makedirs("temp", exist_ok=True)
        path_audio = f"temp/{file_id}.ogg"
        await new_file.download_to_drive(path_audio)
        
        texto_transcrito = ai_assistant.transcrever_audio(path_audio)
        
        if texto_transcrito:
            await update.message.reply_text(f"🎤 Entendi: \"{texto_transcrito}\"")
            await processar_texto_e_salvar(texto_transcrito, update, context)
        else:
            await update.message.reply_text("❌ Não consegui transcrever o áudio.")
    except Exception as e:
        print(f"DEBUG VOICE: {e}")
        await update.message.reply_text("❌ Erro ao processar voz.")
    finally:
        if 'path_audio' in locals() and os.path.exists(path_audio):
            os.remove(path_audio)

async def processar_texto_e_salvar(texto, update, context):
    """
    Função central que conecta a IA (Texto/Voz) aos serviços de Sheets e Mensagens.
    """
    try:
        # 1. Feedback visual no Telegram
        await update.message.reply_chat_action("typing")

        # 2. IA interpreta o que foi dito
        resultado = ai_assistant.interpretar_mensagem(texto)
        
        # IMPORTANTE: Esse print tem que aparecer no seu terminal!
        print(f"DEBUG IA: {resultado}")

        intencao = resultado.get("intencao")
        dados = resultado.get("dados", {})

        # --- CASO 1: DEFINIR PREÇO DO ALUNO ---
        if intencao == "configurar":
            nome = dados.get("nome", "Desconhecido").strip().title()
            valor = float(dados.get("valor_hora", 0))
            
            sucesso = sheets.definir_valor_aluno(nome, valor)
            if sucesso:
                await update.message.reply_text(f"✅ Valor de R$ {valor:.2f}/h fixado para {nome}.")
            else:
                await update.message.reply_text("❌ Erro ao salvar configuração na planilha.")

        # --- CASO 2: REGISTRAR UMA AULA ---
        elif intencao == "aula":
            nome = dados.get("nome", "Desconhecido").strip().title()
            horas = float(dados.get("horas", 0))
            
            # Tratamento de data (usa hoje como padrão)
            data_str = dados.get("data")
            try:
                data_obj = datetime.strptime(data_str, "%d/%m/%Y") if data_str else datetime.now()
            except:
                data_obj = datetime.now()

            # Chama o service que busca o valor fixo automaticamente
            sucesso, info = sheets.cadastrar_aula_aluno(nome, data_obj, horas)

            if sucesso:
                valor_usado = float(info)
                total = valor_usado * horas
                await update.message.reply_text(
                    f"✅ **Aula Registrada!**\n"
                    f"👤 Aluno: {nome}\n"
                    f"⏱️ Horas: {horas}h\n"
                    f"💰 Valor/h: R$ {valor_usado:.2f}\n"
                    f"💵 **Total: R$ {total:.2f}**"
                )
            elif info == "valor_nao_encontrado":
                await update.message.reply_text(
                    f"⚠️ Não achei o valor da hora de **{nome}**.\n"
                    f"Diga primeiro: 'Definir valor do {nome} como 100 reais'."
                )
            else:
                await update.message.reply_text(f"❌ Erro no Sheets: {info}")

        # --- CASO 3: CONSULTAR FATURAMENTO ---
        elif intencao == "faturamento":
            nome = dados.get("nome", "Desconhecido").strip().title()
            mes = int(dados.get("mes", datetime.now().month))
            ano = int(dados.get("ano", datetime.now().year))
            
            total_receber = sheets.calcular_faturamento_aluno(nome, mes, ano)
            
            if total_receber is None:
                await update.message.reply_text(f"❓ Aluno {nome} não encontrado ou sem aulas.")
            else:
                await update.message.reply_text(
                    f"📊 **Resumo Financeiro**\n"
                    f"👤 Aluno: {nome}\n"
                    f"📅 Mês: {mes}/{ano}\n"
                    f"💰 **Total: R$ {total_receber:.2f}**"
                )
        # --- CASO 4: VERIFICAR AULAS DADAS ---
        elif intencao == "listar_aulas":
            nome = dados.get("nome").strip().title()
            mes = int(dados.get("mes", datetime.now().month))
            ano = int(dados.get("ano", datetime.now().year))
            
            # Chamando o novo método que traz os detalhes
            aulas = sheets.listar_detalhes_aulas(nome, mes, ano)
            
            if aulas is None:
                await update.message.reply_text(f"❓ Aluno {nome} não encontrado.")
            elif not aulas:
                await update.message.reply_text(f"🗓️ Nenhuma aula registrada para {nome} em {mes}/{ano}.")
            else:
                linhas_relatorio = []
                total_horas_mes = 0.0
                
                for aula in aulas:
                    h = float(aula['horas'].replace(',', '.'))
                    linhas_relatorio.append(f"• {aula['data']}: {h}h")
                    total_horas_mes += h
                
                corpo_mensagem = "\n".join(linhas_relatorio)
                
                await update.message.reply_text(
                    f"📋 **Extrato de Aulas: {nome}**\n"
                    f"📅 Período: {mes}/{ano}\n\n"
                    f"{corpo_mensagem}\n\n"
                    f"📊 **Total do mês: {total_horas_mes:.1f} horas**\n"
                    f"✅ {len(aulas)} sessões registradas."
                )
        
        # --- CASO 5: AGENDAR NA AGENDA (FIXO OU ÚNICO) ---
        elif intencao == "agendar_fixo":
            nome = dados.get("nome", "Aluno").strip().title()
            dia_cod = dados.get("dia_semana") # MO, TU, etc. (Vem se for recorrente)
            data_str = dados.get("data")      # DD/MM/YYYY (Vem se for aula única)
            horario_raw = str(dados.get("horario", "14:00")).lower()
            
            valor_duracao = dados.get("horas") or dados.get("duracao")
            duracao = float(valor_duracao) if valor_duracao is not None else 1.0
            
            try:
                # 1. Normalização do Horário
                horario_limpo = horario_raw.replace("horas", "").replace("h", "").strip()
                hora_f, min_f = (map(int, horario_limpo.split(':')) if ":" in horario_limpo else (int(horario_limpo), 0))

                # 2. Define a Data de Início
                if data_str:
                    # Aula única: usa a data que você falou
                    data_base = datetime.strptime(data_str, "%d/%m/%Y")
                elif dia_cod:
                    # Aula recorrente: Precisamos encontrar a PRÓXIMA ocorrência desse dia
                    dias_map = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}
                    dia_alvo = dias_map[dia_cod]
                    
                    agora = datetime.now()
                    hoje_dia_semana = agora.weekday() # 0=Segunda, 2=Quarta...
                    
                    # Calcula quantos dias faltam para o próximo dia escolhido
                    dias_para_frente = (dia_alvo - hoje_dia_semana) % 7
                    
                    # Se o dia escolhido for HOJE, mas o horário já passou, pula para a semana que vem
                    # (Opcional, mas evita criar evento no passado do mesmo dia)
                    data_base = agora + timedelta(days=dias_para_frente)
                else:
                    data_base = datetime.now()

                data_inicio = data_base.replace(hour=hora_f, minute=min_f, second=0, microsecond=0)
                
                # 3. CHAMADA INTELIGENTE:
                # Se 'dia_cod' existir, é recorrente. Se não, é aula única (recorrencia=None)
                link = calendar.agendar_aula(nome, data_inicio, duracao, recorrencia=dia_cod)
                
                if link:
                    tipo_msg = f"🔁 Toda {dia_cod}" if dia_cod else f"📍 Dia {data_inicio.strftime('%d/%m')}"
                    await update.message.reply_text(
                        f"🗓️ **Evento Criado na Agenda!**\n"
                        f"👤 Aluno: {nome}\n"
                        f"📅 {tipo_msg}\n"
                        f"⏰ Às {hora_f:02d}:{min_f:02d}\n\n"
                        f"🔗 [Ver na Agenda]({link})",
                        parse_mode="Markdown"
                    )
                else:
                    await update.message.reply_text("❌ Erro ao agendar no Google Calendar.")
            
            except Exception as e:
                await update.message.reply_text(f"❌ Erro ao processar o agendamento: {e}")

        # --- CASO 6: CANCELAR AULA ---
        elif intencao == "cancelar":
            nome = dados.get("nome", "Aluno").strip().title()
            # Verifica se a IA identificou que é para apagar tudo (ajuste o prompt para isso)
            apagar_tudo = "todas" in texto.lower() or "tudo" in texto.lower()
            
            data_str = dados.get("data")
            data_obj = datetime.strptime(data_str, "%d/%m/%Y") if data_str else datetime.now()

            sucesso, mensagem = calendar.cancelar_aula(nome, data_obj, todas=apagar_tudo)
            await update.message.reply_text(f"{'🗑️' if sucesso else '⚠️'} {mensagem}")

    except Exception as e:
        print(f"❌ ERRO CRÍTICO no processar_texto_e_salvar: {e}")
        await update.message.reply_text(f"❌ Ocorreu um erro interno: {e}")