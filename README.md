# 🤖 Gestão de Aulas Particulares — Bot para Telegram + IA + Google Services

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![Google Sheets](https://img.shields.io/badge/Google%20Sheets-API-34A853?style=for-the-badge&logo=googlesheets&logoColor=white)
![Google Calendar](https://img.shields.io/badge/Google%20Calendar-API-4285F4?style=for-the-badge&logo=googlecalendar&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?style=for-the-badge&logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange?style=for-the-badge)

</div>  

---

## 📖 Sobre o Projeto

Bot para Telegram desenvolvido para facilitar a gestão de aulas particulares. A ferramenta permite registrar e organizar aulas diretamente pelo Telegram, utilizando **comandos de voz ou texto**, com integração ao **Google Calendar** para agendamentos e ao **Google Sheets** para histórico financeiro e de sessões.

### O que o bot faz

- **Cadastrar alunos** com valor de hora/aula definido
- **Agendar aulas recorrentes** (ex: toda terça às 17h) diretamente no Google Calendar
- **Agendar aulas avulsas** em datas específicas
- **Registrar aulas dadas**, calculando automaticamente o valor total
- **Desmarcar aulas** pontuais ou cancelar recorrências
- **Consultar histórico** — quais dias foram ministradas aulas para um determinado aluno
- **Consultar o financeiro** — total a receber por aluno em um determinado mês

---

## 🎬 Demonstração

> Exemplos reais do bot em funcionamento via Telegram:

**Registrando um aluno e agendando aula recorrente:**

![Demo 1](docs/demo1.png)

**Registrando aulas e consultando histórico:**

![Demo 2](docs/demo2.png)

**Desmarcando uma aula:**

![Demo 3](docs/demo3.png)

---
---

## 🚀 Funcionalidades

- 🎙️ Aceita comandos por **áudio ou texto**
- 🧠 Interpretação de linguagem natural via **IA (Claude)**
- 📅 Criação e remoção de eventos no **Google Calendar**
- 📊 Registro e consulta de aulas no **Google Sheets**
- ⚙️ Arquitetura modular com separação entre handlers e services

---

## 📁 Estrutura do Projeto
```
├── src/
│   ├── bot/              # Lógica dos handlers do Telegram
│   ├── services/         # Integrações (AI, Sheets, Calendar)
│   └── main.py           # Ponto de entrada do bot
├── docs/                 # Imagens do funcionamento
├── README.md             # Readme do projeto
├── .gitignore            # Arquivos não versionados
├── .env.example          # Exemplo de env
├── requirements.txt      # Dependências do projeto
├── .env                  # Variáveis de ambiente (não versionado)
└── credentials.json      # Credenciais do Google Cloud (não versionado)
```

---

## 🧰 Pré-requisitos


- Python 3.10 ou superior  
- Conta no Telegram  
- Conta no Google Cloud  com as APIs ativadas
- Chave de API de IA (ex: OpenAI)  

---

## ⚙️ Configuração do Ambiente

### 1. Clone o repositório
```
git clone https://github.com/hcdebarros/gestao-professores.git
cd gestao-professores
```
### 2. Crie um ambiente virtual
```
python -m venv venv
```
### 3. Ative o ambiente virtual

#### Windows
```
venv\Scripts\activate
```

#### Linux
```
source venv/bin/activate
```

### 4. Instale as dependências
```
pip install -r requirements.txt
```

---

## 🔐 Configuração das Variáveis de Ambiente
- Crie um arquivo .env na raiz do projeto:
```
TELEGRAM_TOKEN=seu_token_aqui
OPENAI_API_KEY=sua_chave_aqui
GOOGLE_CALENDAR_ID=seu_id_aqui
```
---

## 🤖 Configuração do Telegram
1. Abra o Telegram
2. Procure por @BotFather
3. Crie um bot com o comando:
```
  /newbot
  ```
4. Siga as instruções
5. Copie o token gerado
6. Cole no arquivo .env

---

## ☁️ Configuração do Google Cloud
1. Acesse o Google Cloud Console
2. Crie um novo projeto
3. Ative as APIs:  
   - Google Sheets API  
   - Google Calendar API  
4. Vá em "Credenciais"
5. Crie uma Conta de Serviço
6. Gere uma chave no formato JSON
7. Renomeie para credentials.json
8. Coloque o arquivo na raiz do projeto
   
> ⚠️ Lembre-se de compartilhar a planilha e a agenda com o e-mail da conta de serviço gerada.
---

## ▶️ Executando o Projeto
```
python src/main.py
```
Se tudo estiver configurado corretamente, o bot ficará online no Telegram.

---

## 🧪 Testando o Bot
- Abra o Telegram
- Procure pelo seu bot
- Envie uma mensagem
- Verifique se o bot responde

---

## 🛠️ Solução de Problemas

| Problema | Possível causa | Solução |
|----------|---------------|---------|
| Bot não responde | Token inválido ou bot offline | Verifique o `TELEGRAM_TOKEN` e se o processo está rodando |
| Erro nas APIs do Google | Credenciais ou permissões incorretas | Verifique o `credentials.json` e se as APIs estão ativas |
| Erro de dependências | Pacotes desatualizados ou faltando | Execute `pip install --upgrade pip && pip install -r requirements.txt` |
| Áudio não transcrito | Chave da IA inválida | Verifique a `ANTHROPIC_API_KEY` |

---

## 📌 Boas Práticas
- Nunca versionar:
  - .env
  - credentials.json
- Utilize um arquivo .gitignore
- Separe responsabilidades entre bot e services

---

## 📈 Melhorias Futuras

- [ ] Dashboard web para visualização de dados
- [ ] Deploy em cloud (Railway, GCP, AWS)
- [ ] Integração com banco de dados
- [ ] Suporte a múltiplos professores/usuários
- [ ] Relatórios mensais automáticos via Telegram

---

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).




