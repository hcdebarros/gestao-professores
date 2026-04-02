import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

class CalendarService:
    def __init__(self):
        self.scope = ['https://www.googleapis.com/auth/calendar']
        self.creds = Credentials.from_service_account_file(
            "credentials.json", 
            scopes=self.scope
        )
        self.service = build('calendar', 'v3', credentials=self.creds)
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID")

    def agendar_aula(self, nome_aluno, data_inicio, horas, recorrencia=None):
        """
        Agenda uma aula. 
        recorrencia: pode ser 'MO', 'TU', 'WE', 'TH', 'FR' ou None para aula única.
        """
        try:
            data_fim = data_inicio + timedelta(hours=horas)
            
            # Estrutura base do evento
            event = {
                'summary': f'📚 Aula: {nome_aluno}',
                'description': 'Registrado via Bot de Gestão.',
                'start': {
                    'dateTime': data_inicio.isoformat(),
                    'timeZone': 'America/Recife', # Ajuste se necessário
                },
                'end': {
                    'dateTime': data_fim.isoformat(),
                    'timeZone': 'America/Recife',
                },
            }

            # Se houver recorrência (ex: 'MO' para segunda), adicionamos a regra
            if recorrencia:
                event['recurrence'] = [f'RRULE:FREQ=WEEKLY;BYDAY={recorrencia}']
                event['summary'] = f'🔁 Aula Fixa: {nome_aluno}'

            event_result = self.service.events().insert(
                calendarId=self.calendar_id, 
                body=event
            ).execute()
            
            return event_result.get('htmlLink')
        except Exception as e:
            print(f"Erro no Calendar: {e}")
            return None
        
    def cancelar_aula(self, nome_aluno: str, data_pesquisa: datetime = None, todas: bool = False):
        """
        Busca e remove aulas. 
        - Se todas=True: remove a série recorrente inteira.
        - Se todas=False: remove apenas a instância da data_pesquisa.
        """
        try:
            # 1. Se não passou data, assume hoje
            data_alvo = data_pesquisa or datetime.now()
            
            # Se for para apagar TUDO, não limitamos a busca por data
            t_min = None if todas else data_alvo.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
            t_max = None if todas else data_alvo.replace(hour=23, minute=59, second=59).isoformat() + 'Z'

            events_result = self.service.events().list(
                calendarId=self.calendar_id, 
                timeMin=t_min, 
                timeMax=t_max,
                q=nome_aluno,
                singleEvents=False if todas else True # Se quer todas, buscamos o 'pai' da recorrência
            ).execute()

            events = events_result.get('items', [])

            if not events:
                return False, f"Não encontrei nenhuma aula para '{nome_aluno}'."

            # 2. Deleta o evento encontrado
            for ev in events:
                self.service.events().delete(calendarId=self.calendar_id, eventId=ev['id']).execute()
                msg = f"Todas as aulas de {nome_aluno} foram removidas." if todas else f"Aula de {nome_aluno} em {data_alvo.strftime('%d/%m')} removida."
                return True, msg

        except Exception as e:
            return False, f"Erro: {e}"

        except Exception as e:
            print(f"Erro ao cancelar: {e}")
            return False, f"Erro técnico ao cancelar: {e}"