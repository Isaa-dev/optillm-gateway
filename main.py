import os
import time
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configuração da Base de Dados SQLite para Auditoria FinOps
DB_NAME = "gateway.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS request_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            requested_model TEXT,
            routed_model TEXT,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            input_cost REAL,
            output_cost REAL,
            total_cost REAL,
            latency_seconds REAL,
            is_mock INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Tabela de preços por 1k tokens
MODEL_PRICING = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
}

def log_to_db(req_model, rout_model, p_tokens, c_tokens, in_cost, out_cost, tot_cost, latency, is_mock):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO request_logs (timestamp, requested_model, routed_model, prompt_tokens, completion_tokens, input_cost, output_cost, total_cost, latency_seconds, is_mock)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.utcnow().isoformat(), req_model, rout_model, p_tokens, c_tokens, in_cost, out_cost, tot_cost, latency, is_mock))
    conn.commit()
    conn.close()

@app.route("/v1/chat/completions", methods=["POST"])
def proxy_chat_completions():
    start_time = time.time()
    body = request.get_json() or {}
    target_model = body.get("model", "gpt-3.5-turbo")
    messages = body.get("messages", [])
    
    original_model = target_model
    routed_by_optillm = False
    
    # Lógica de Roteamento Inteligente (Smart Routing)
    if target_model == "gpt-4o" and messages and isinstance(messages, list):
        last_msg = messages[-1]
        if isinstance(last_msg, dict) and "content" in last_msg:
            if len(str(last_msg["content"])) < 30:
                target_model = "gpt-3.5-turbo"
                routed_by_optillm = True

    openai_api_key = os.getenv("OPENAI_API_KEY")
    # Ativa o Modo Mock se não houver chave ou se ocorrer erro de créditos/autenticação
    use_mock = not openai_api_key

    data = None
    is_mock_flag = 0

    if not use_mock:
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }
        body["model"] = target_model
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                json=body,
                headers=headers,
                timeout=30.0
            )
            if response.status_code == 200:
                data = response.json()
            else:
                use_mock = True # Fallback automático para mock se faltarem créditos
        except Exception:
            use_mock = True

    elapsed_time = round(time.time() - start_time, 4)

    if use_mock:
        is_mock_flag = 1
        content_preview = messages[-1].get('content', '') if messages else 'N/A'
        data = {
            "id": "chatcmpl-mock-gateway",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": target_model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"[OptiLLM Mock] Resposta simulada com sucesso para: '{content_preview}'"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 15,
                "completion_tokens": 25,
                "total_tokens": 40
            }
        }

    usage = data.get("usage", {"prompt_tokens": 15, "completion_tokens": 25})
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    
    pricing = MODEL_PRICING.get(target_model, {"input": 0.0005, "output": 0.0015})
    input_cost = (prompt_tokens / 1000) * pricing["input"]
    output_cost = (completion_tokens / 1000) * pricing["output"]
    total_cost = input_cost + output_cost

    # Registar a transação na base de dados SQLite
    log_to_db(
        original_model, target_model, 
        prompt_tokens, completion_tokens, 
        input_cost, output_cost, total_cost, 
        elapsed_time, is_mock_flag
    )

    # Injeção de metadados FinOps
    data["optillm_finops"] = {
        "routed_model": target_model,
        "requested_model": original_model,
        "smart_routing_savings_active": routed_by_optillm,
        "gateway_mode": "simulation_mock" if is_mock_flag else "live_openai",
        "cost_breakdown_usd": {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6)
        },
        "latency_seconds": elapsed_time,
        "token_usage": usage
    }

    return jsonify(data)

@app.route("/logs", methods=["GET"])
def get_logs():
    """Endpoint de Auditoria para consultar o histórico FinOps guardado na BD"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM request_logs ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "OptiLLM-Gateway", 
        "version": "0.3.0-finops-db"
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)