import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Preços fictícios por 1k tokens (exemplo para FinOps)
MODEL_PRICING = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
}

@app.route("/v1/chat/completions", methods=["POST"])
def proxy_chat_completions():
    body = request.get_json() or {}
    target_model = body.get("model", "gpt-3.5-turbo")
    messages = body.get("messages", [])
    
    # Roteamento inteligente baseado no tamanho da mensagem
    if target_model == "gpt-4o" and messages and isinstance(messages, list):
        last_msg = messages[-1]
        if isinstance(last_msg, dict) and "content" in last_msg:
            if len(str(last_msg["content"])) < 30:
                target_model = "gpt-3.5-turbo"

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        return jsonify({"detail": "Chave da API OpenAI não configurada no Gateway."}), 500

    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }

    body["model"] = target_model

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        json=body,
        headers=headers,
        timeout=30.0
    )
    
    if response.status_code != 200:
        return jsonify(response.json()), response.status_code

    data = response.json()

    usage = data.get("usage", {"prompt_tokens": 10, "completion_tokens": 15})
    pricing = MODEL_PRICING.get(target_model, {"input": 0.001, "output": 0.002})
    
    estimated_cost = (
        (usage.get("prompt_tokens", 10) / 1000) * pricing["input"] +
        (usage.get("completion_tokens", 15) / 1000) * pricing["output"]
    )
    
    data["optillm_finops_cost_usd"] = round(estimated_cost, 6)
    data["optillm_routed_model"] = target_model

    return jsonify(data)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "OptiLLM-Gateway"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)