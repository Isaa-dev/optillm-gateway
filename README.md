# OptiLLM-Gateway 🚀

> Um proxy gateway full-stack e de nível corporativo para Large Language Models (LLMs), projetado com foco em **FinOps**, **Cibersegurança**, **Performance** e **Auditoria em Tempo Real**.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-38BDF8?style=flat-square&logo=tailwind-css)](https://tailwindcss.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Persistence-003B57?style=flat-square&logo=sqlite)](https://www.sqlite.org/)
[![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?style=flat-square&logo=render)](https://render.com/)

---

## 🌟 Principais Funcionalidades

1. **FinOps & Controlo de Custos**:
   - Cálculo automático de custos por requisição com base no modelo (`gpt-4o`, `gpt-3.5-turbo`, etc.), discriminando tokens de *input* e *output* em USD.
   - Monitorização de orçamento e métricas em tempo real.

2. **Cibersegurança & Guardiões de Privacidade (PII Redaction)**:
   - Deteção e mascaramento automático de dados sensíveis (e-mails e números de telefone) diretamente no payload antes de atingirem os modelos de IA.

3. **Performance & Cache Semântico**:
   - Sistema de cache local baseado em hash de prompts utilizando SQLite para garantir respostas instantâneas a pedidos duplicados, reduzindo a latência para menos de `0.001s` e gerando poupança de tokens a custo zero.

4. **Resiliência & Multi-Provider Fallback**:
   - Mecanismo de redundância inteligente que tenta primariamente a OpenAI e, em caso de indisponibilidade ou falha, comuta automaticamente para um provedor alternativo (como a Groq) ou para um modo de simulação corporativa.

5. **Rate Limiting & Controlo Multi-Tenant**:
   - Proteção de quotas por cada chave de API (`X-API-Key`) com limitação de pedidos por minuto (RPM) e bloqueio automático de excessos (`429 Too Many Requests`).

6. **Dashboard Visual Moderno (Frontend Full-Stack)**:
   - Interface interativa desenvolvida com **Tailwind CSS**, apresentando cartões de KPI em tempo real, um *Playground* para testes de prompt integrados e uma tabela de auditoria viva conectada ao backend Flask.

---

## 🛠️ Arquitetura e Tecnologias

- **Backend**: Python, Flask, SQLite, Requests, Gunicorn.
- **Frontend**: HTML5, Tailwind CSS (via CDN), JavaScript assíncrono (Fetch API).
- **Arquitetura**: Estrutura modular (`/templates`, rotas REST, persistência otimizada).

---

## 🚀 Como Executar o Projeto Localmente

1. **Clonar o repositório**:
   ```bash
   git clone [https://github.com/SEU-UTILIZADOR/optillm-gateway.git](https://github.com/SEU-UTILIZADOR/optillm-gateway.git)
   cd optillm-gateway