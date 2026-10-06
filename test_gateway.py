import requests
import json

url = "http://127.0.0.1:8000/v1/chat/completions"

# Cabeçalho com a chave de API do cliente
headers = {"X-API-Key": "cliente-isabelly-123"}

# Mensagem com dados sensíveis (e-mail e telemóvel) para testar o Guardrail e o Cache
payload = {
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Olá! O meu email é teste@email.com e o meu telemóvel é 912345678."}]
}

print("A enviar o 1.º pedido (Vai processar, mascarar dados e guardar no Cache):")
response = requests.post(url, json=payload, headers=headers)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

print("\n" + "="*50 + "\n")

print("A enviar o 2.º pedido IDÊNTICO (Vai vir diretamente do Cache a Custo Zero!):")
response_cached = requests.post(url, json=payload, headers=headers)
print(json.dumps(response_cached.json(), indent=2, ensure_ascii=False))