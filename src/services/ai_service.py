import os
import json
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini" # Rápido e barato para extração

    def interpretar_mensagem(self, texto_usuario: str):
        # Pega a data exata do sistema no momento da mensagem
        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        dia_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"][agora.weekday()]
        
        prompt_sistema = f"""
        Você é um assistente de gestão financeira de aulas particulares.
        Sua resposta deve ser ESTRITAMENTE um objeto JSON válido.
        
        CONTEXTO TEMPORAL:
        - Hoje é {dia_semana}, {data_hoje}.
        - Se o usuário disser "hoje", use {data_hoje}.
        - Se o usuário disser "ontem", calcule a data correta baseada em {data_hoje}.
        - Para as intenções "faturamento" ou "listar_aulas", se o mês/ano não forem ditos, use o mês/ano de {data_hoje}.

        IDENTIFIQUE A INTENÇÃO:
        1. "configurar": Definir valor/hora do aluno (ex: 'Bruno 100 reais').
        2. "aula": Registrar aula dada (ex: 'Aula com Bruno hoje 2h').
        3. "faturamento": Somar quanto vai receber no mês (ex: 'Quanto recebo do Bruno em outubro?').
        4. "listar_aulas": Listar os dias de aula (ex: 'Quais dias dei aula para o Bruno mês passado?').

        FORMATO DE RETORNO (JSON):
        {{
            "intencao": "configurar" | "aula" | "faturamento" | "listar_aulas",
            "dados": {{
                "nome": "string (nome do aluno)",
                "valor_hora": float,
                "data": "DD/MM/YYYY",
                "horas": float,
                "mes": integer (1-12),
                "ano": integer (ex: 2026)
            }}
        }}
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": texto_usuario}
            ],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)
    
    def transcrever_audio(self, arquivo_audio_path: str):
        """
        Envia o arquivo de áudio para a OpenAI Whisper e retorna o texto.
        """
        try:
            with open(arquivo_audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
                return transcript.text
        except Exception as e:
            print(f"Erro na transcrição: {e}")
            return None