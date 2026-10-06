import requests
import json

url = "http://127.0.0.1:8000/v1/chat/completions"

# Teste com uma mensagem curta (< 30 caracteres) para ativar o Smart Routing (gpt-4o -> gpt-3.5-turbo)
payload = {
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Olá! Quanto é 2+2?"}]
}

print("A enviar pedido para o OptiLLM-Gateway...")
response = requests.post(url, json=payload)

print(f"\nStatus Code: {response.status_code}")
print("Resposta Completa do Gateway com Métricas FinOps:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))