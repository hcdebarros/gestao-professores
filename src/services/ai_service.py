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
        Você é um assistente de gestão de aulas particulares e agenda.
        Sua resposta deve ser ESTRITAMENTE um objeto JSON válido.
        
        CONTEXTO TEMPORAL:
        - Hoje é {dia_semana}, {data_hoje}.
        - Se o usuário disser "hoje", use {data_hoje}.
        - Se o usuário disser "amanhã", calcule a data correta baseada em {data_hoje}.
        - Se o usuário disser "semana que vem", calcule a data correta baseada em {data_hoje}.

        IDENTIFIQUE A INTENÇÃO:
        1. "configurar": Definir valor/hora do aluno (ex: 'Bruno 100 reais').
        2. "aula": Registrar aula que JÁ OCORREU no passado ou hoje para fins financeiros (Sheets).
        3. "faturamento": Consultar ganhos (ex: 'Quanto recebo do Bruno em outubro?').
        4. "listar_aulas": Listar datas de aulas dadas.
        5. "agendar_fixo": Agendar aula FUTURA na agenda (Calendar). Pode ser única ou recorrente.
        6. "cancelar": Remover aula(s) da agenda (Calendar).

        REGRAS DE EXTRAÇÃO:
        - "agendar_fixo": 
            - Se for recorrente (ex: 'toda segunda'), preencha 'dia_semana' (MO, TU, WE, TH, FR, SA, SU) e deixe 'data' nulo.
            - Se for data específica (ex: 'dia 7'), preencha 'data' (DD/MM/YYYY) e deixe 'dia_semana' nulo.
            - Sempre tente extrair 'horario' (HH:MM). Se não houver, use "14:00".
            - Se a duração não for dita, use 'horas': 1.0.
        - "cancelar":
            - Identifique o nome do aluno. Se o usuário disser "cancelar todas", "tudo" ou usar o plural, a intenção é "cancelar".

        FORMATO DE RETORNO (JSON):
        {{
            "intencao": "configurar" | "aula" | "faturamento" | "listar_aulas" | "agendar_fixo" | "cancelar",
            "dados": {{
                "nome": "string",
                "valor_hora": float,
                "data": "DD/MM/YYYY" | null,
                "horario": "HH:MM",
                "horas": float,
                "dia_semana": "MO" | "TU" | "WE" | "TH" | "FR" | "SA" | "SU" | null,
                "mes": integer,
                "ano": integer
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