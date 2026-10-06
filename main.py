import os
import time
import sqlite3
import hashlib
import re
from datetime import datetime
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

DB_NAME = "gateway.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS request_logs')
    cursor.execute('DROP TABLE IF EXISTS semantic_cache')
    
    cursor.execute('''
        CREATE TABLE request_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            api_key TEXT,
            requested_model TEXT,
            routed_model TEXT,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            input_cost REAL,
            output_cost REAL,
            total_cost REAL,
            latency_seconds REAL,
            is_mock INTEGER,
            is_cached INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE semantic_cache (
            prompt_hash TEXT PRIMARY KEY,
            response_json TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

MODEL_PRICING = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
}

def mask_pii(text):
    """Guardrail: Mascara e-mails e números de telefone por segurança (PII Redaction)"""
    if not isinstance(text, str):
        return text
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL_REDACTED]', text)
    text = re.sub(r'\b\d{9,11}\b', '[PHONE_REDACTED]', text)
    return text

def get_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

@app.route("/v1/chat/completions", methods=["POST"])
def proxy_chat_completions():
    start_time = time.time()
    
    api_key_header = request.headers.get("X-API-Key", "default-dev-key")
    
    body = request.get_json() or {}
    target_model = body.get("model", "gpt-3.5-turbo")
    messages = body.get("messages", [])
    
    original_model = target_model
    routed_by_optillm = False
    
    for msg in messages:
        if "content" in msg:
            msg["content"] = mask_pii(msg["content"])

    last_content = messages[-1].get("content", "") if messages else ""
    prompt_hash = get_hash(last_content)

    # 1. Verificação de Cache Semântico/Exato
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT response_json FROM semantic_cache WHERE prompt_hash = ?", (prompt_hash,))
    cached_row = cursor.fetchone()
    conn.close()

    if cached_row:
        elapsed_time = round(time.time() - start_time, 4)
        import json
        cached_data = json.loads(cached_row[0])
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO request_logs (timestamp, api_key, requested_model, routed_model, prompt_tokens, completion_tokens, input_cost, output_cost, total_cost, latency_seconds, is_mock, is_cached)
            VALUES (?, ?, ?, ?, 0, 0, 0.0, 0.0, 0.0, ?, 0, 1)
        ''', (datetime.utcnow().isoformat(), api_key_header, original_model, target_model, elapsed_time))
        conn.commit()
        conn.close()
        
        cached_data["optillm_finops"]["cache_hit"] = True
        cached_data["optillm_finops"]["latency_seconds"] = elapsed_time
        return jsonify(cached_data)

    # Lógica de Smart Routing
    if target_model == "gpt-4o" and len(last_content) < 30:
        target_model = "gpt-3.5-turbo"
        routed_by_optillm = True

    openai_api_key = os.getenv("OPENAI_API_KEY")
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
            response = requests.post("https://api.openai.com/v1/chat/completions", json=body, headers=headers, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
            else:
                use_mock = True
        except Exception:
            use_mock = True

    elapsed_time = round(time.time() - start_time, 4)

    if use_mock:
        is_mock_flag = 1
        data = {
            "id": "chatcmpl-enterprise-mock",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": target_model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"[OptiLLM Enterprise Mock] Resposta segura para: '{last_content}'"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 18,
                "completion_tokens": 22,
                "total_tokens": 40
            }
        }

    usage = data.get("usage", {"prompt_tokens": 18, "completion_tokens": 22})
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    
    pricing = MODEL_PRICING.get(target_model, {"input": 0.0005, "output": 0.0015})
    input_cost = (prompt_tokens / 1000) * pricing["input"]
    output_cost = (completion_tokens / 1000) * pricing["output"]
    total_cost = input_cost + output_cost

    # Anexar metadados FinOps ANTES de guardar no cache e responder
    data["optillm_finops"] = {
        "routed_model": target_model,
        "requested_model": original_model,
        "smart_routing_savings_active": routed_by_optillm,
        "gateway_mode": "enterprise_mock" if is_mock_flag else "live_openai",
        "cache_hit": False,
        "pii_guardrail_active": True,
        "cost_breakdown_usd": {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6)
        },
        "latency_seconds": elapsed_time,
        "token_usage": usage
    }

    import json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Guardar no Cache com o bloco optillm_finops já incluído
    cursor.execute('''
        INSERT OR REPLACE INTO semantic_cache (prompt_hash, response_json, created_at)
        VALUES (?, ?, ?)
    ''', (prompt_hash, json.dumps(data), datetime.utcnow().isoformat()))
    
    cursor.execute('''
        INSERT INTO request_logs (timestamp, api_key, requested_model, routed_model, prompt_tokens, completion_tokens, input_cost, output_cost, total_cost, latency_seconds, is_mock, is_cached)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    ''', (datetime.utcnow().isoformat(), api_key_header, original_model, target_model, prompt_tokens, completion_tokens, input_cost, output_cost, total_cost, elapsed_time, is_mock_flag))
    conn.commit()
    conn.close()

    return jsonify(data)

@app.route("/logs", methods=["GET"])
def get_logs():
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
        "version": "0.4.2-enterprise"
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)