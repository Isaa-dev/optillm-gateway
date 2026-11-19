# OptiLLM-Gateway

> Um gateway (proxy) full-stack para APIs de Large Language Models (LLMs), com foco em **controle de custos (FinOps)**, **segurança de dados**, **performance** e **auditoria em tempo real**.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-38BDF8?style=flat-square&logo=tailwind-css)](https://tailwindcss.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Persistence-003B57?style=flat-square&logo=sqlite)](https://www.sqlite.org/)
[![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?style=flat-square&logo=render)](https://render.com/)

---

## 🌟 Principais funcionalidades

1. **FinOps e controle de custos**
   - Cálculo automático do custo de cada requisição com base no modelo (`gpt-4o`, `gpt-3.5-turbo` etc.), separando tokens de *input* e *output* em USD.
   - Métricas de uso e custo atualizadas em tempo real no dashboard.

2. **Segurança e privacidade (mascaramento de dados pessoais)**
   - Detecção e mascaramento automático de e-mails e números de telefone no payload, antes de qualquer dado chegar aos modelos de IA.

3. **Performance com cache de respostas**
   - Cache local em SQLite baseado no hash SHA-256 do prompt: pedidos idênticos são respondidos na hora, sem nova chamada à API e sem custo de tokens.

4. **Resiliência com fallback entre provedores**
   - Tenta primeiro a OpenAI; se ela falhar ou estiver indisponível, troca automaticamente para um provedor alternativo (Groq) ou, sem chaves configuradas, para um modo de simulação.

5. **Roteamento inteligente**
   - Prompts muito curtos enviados ao `gpt-4o` são redirecionados para um modelo mais barato, reduzindo custo sem impacto perceptível.

6. **Rate limiting por cliente**
   - Limite de requisições por minuto (20 RPM) para cada chave de API (`X-API-Key`), com bloqueio automático de excessos (`429 Too Many Requests`).

7. **Dashboard visual**
   - Interface em Tailwind CSS com cartões de KPI em tempo real, um *playground* para testar prompts e uma tabela de auditoria conectada ao backend Flask.

---

## 🛠️ Arquitetura e tecnologias

- **Backend:** Python, Flask, SQLite, Requests, Gunicorn
- **Frontend:** HTML5, Tailwind CSS (via CDN), JavaScript (Fetch API)
- **Estrutura:** rotas REST (`/v1/chat/completions`, `/logs`, `/health`) e templates em `/templates`

---

## 🚀 Como executar localmente

1. **Clone o repositório**

   ```bash
   git clone https://github.com/Isaa-dev/optillm-gateway.git
   cd optillm-gateway
   ```

2. **Crie e ative um ambiente virtual**

   ```bash
   python -m venv venv
   # Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Instale as dependências**

   ```bash
   pip install -r requirements.txt
   ```

4. **(Opcional) Configure as chaves de API**

   Sem chaves, o gateway roda em modo de simulação. Para usar provedores reais:

   ```bash
   export OPENAI_API_KEY="sua-chave"
   export GROQ_API_KEY="sua-chave"   # usada como fallback
   ```

5. **Execute a aplicação**

   ```bash
   python main.py
   ```

6. **Acesse o dashboard** em [http://127.0.0.1:8000](http://127.0.0.1:8000).

Para testar mascaramento e cache, rode `python test_gateway.py` com o servidor ligado.

---

## 🌐 Demonstração ao vivo

A aplicação está publicada no Render.
