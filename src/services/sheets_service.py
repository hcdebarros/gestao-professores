import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from gspread.exceptions import WorksheetNotFound

class SheetsService:
    def __init__(self, sheet_name: str):
        """
        Inicializa a conexão com o Google Sheets e garante as abas básicas.
        """
        # 1. Configuração de Credenciais
        self.scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Ajuste o caminho se o seu arquivo tiver outro nome
        self.creds = Credentials.from_service_account_file(
            "credentials.json", 
            scopes=self.scope
        )
        self.client = gspread.authorize(self.creds)

        try:
            # 2. Abre a planilha principal
            self.spreadsheet = self.client.open(sheet_name)
            
            # 3. Garante a existência da aba 'Alunos' (onde ficam os valores/hora)
            try:
                self.sheet_config = self.spreadsheet.worksheet("Alunos")
            except WorksheetNotFound:
                # Se não existir, cria com o cabeçalho correto
                self.sheet_config = self.spreadsheet.add_worksheet(
                    title="Alunos", 
                    rows="100", 
                    cols="5"
                )
                self.sheet_config.append_row(["Aluno", "Valor_Hora"])
                print("✅ Aba 'Alunos' criada com sucesso.")

        except Exception as e:
            print(f"❌ Erro ao iniciar SheetsService: {e}")
            raise e

    def cadastrar_aula_aluno(self, nome: str, data: datetime, horas: float):
        """Agora o valor_hora é buscado automaticamente."""
        nome = nome.strip().title()
        valor_hora = self.obter_valor_hora(nome)
        
        if not valor_hora:
            return False, "valor_nao_encontrado"

        try:
            try:
                worksheet = self.spreadsheet.worksheet(nome)
            except WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(title=nome, rows="500", cols="5")
                worksheet.append_row(["Aluno", "Data", "Valor/h", "Horas", "Total"])

            data_formatada = data.strftime('%d/%m/%Y')
            proxima_linha = len(worksheet.get_all_values()) + 1
            formula_total = f"=C{proxima_linha}*D{proxima_linha}"
            
            nova_linha = [nome, data_formatada, valor_hora, horas, formula_total]
            worksheet.append_row(nova_linha, value_input_option="USER_ENTERED")
            return True, valor_hora
        except Exception as e:
            print(f"Erro: {e}")
            return False, str(e)
        
    def definir_valor_aluno(self, nome: str, valor_hora: float):
        nome = nome.strip().title()
        try:
            celula = self.sheet_config.find(nome)
            if celula:
                self.sheet_config.update_cell(celula.row, 2, valor_hora)
            else:
                self.sheet_config.append_row([nome, valor_hora])
                return True
        except Exception as e:
            return False

    def obter_valor_hora(self, nome: str):
            """Busca o valor da hora do aluno. Retorna None se não encontrar."""
            nome = nome.strip().title()
            try:
                celula = self.sheet_config.find(nome)
                if celula:
                    return float(self.sheet_config.cell(celula.row, 2).value)
            except:
                return None
            
    def calcular_faturamento_aluno(self, nome: str, mes: int, ano: int):
        """
        Soma o faturamento com tratamento de limpeza de dados.
        """
        nome = nome.strip().title()
        try:
            worksheet = self.spreadsheet.worksheet(nome)
            # Pegamos todos os valores brutos para evitar problemas com o cabeçalho
            dados = worksheet.get_all_values()
            
            if len(dados) <= 1: # Só tem o cabeçalho
                return 0.0

            cabecalho = [c.strip().lower() for c in dados[0]] # Normaliza o cabeçalho
            try:
                idx_data = cabecalho.index("data")
                idx_total = cabecalho.index("total")
            except ValueError:
                return 0.0

            total_periodo = 0.0
            
            # Percorre as linhas pulando o cabeçalho
            for linha in dados[1:]:
                try:
                    data_str = linha[idx_data].strip()
                    valor_str = linha[idx_total].strip()

                    if not data_str: continue

                    # Converte a data para comparar mês e ano
                    data_aula = datetime.strptime(data_str, '%d/%m/%Y')
                    
                    
                    if data_aula.month == mes and data_aula.year == ano:
                        # Limpeza do valor: remove R$, espaços e troca vírgula por ponto
                        valor_limpo = valor_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
                        total_periodo += float(valor_limpo)
                except Exception as e:
                    continue
            
            return total_periodo
        except WorksheetNotFound:
            return None
        except Exception as e:
            print(f"Erro na consulta: {e}")
            return 0.0

    def listar_detalhes_aulas(self, nome: str, mes: int, ano: int):
        """
        Retorna uma lista de objetos com data e horas de cada aula no mês/ano.
        """
        nome = nome.strip().title()
        try:
            worksheet = self.spreadsheet.worksheet(nome)
            dados = worksheet.get_all_values()
            
            if len(dados) <= 1: return []

            cabecalho = [c.strip().lower() for c in dados[0]]
            idx_data = cabecalho.index("data")
            idx_horas = cabecalho.index("horas") # Precisamos do índice da coluna de horas
            
            detalhes_aulas = []
            
            for linha in dados[1:]:
                try:
                    data_str = linha[idx_data].strip()
                    horas_val = linha[idx_horas].strip()
                    if not data_str: continue
                    
                    data_aula = datetime.strptime(data_str, '%d/%m/%Y')
                    
                    if data_aula.month == int(mes) and data_aula.year == int(ano):
                        detalhes_aulas.append({
                            "data": data_str,
                            "horas": horas_val
                        })
                except:
                    continue
                    
            # Ordena as aulas pela data cronologicamente
            detalhes_aulas.sort(key=lambda x: datetime.strptime(x['data'], '%d/%m/%Y'))
            return detalhes_aulas
        except WorksheetNotFound:
            return None