import requests
import json

api_key = "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"

headers = {
    "Authorization": f"Bearer {api_key}",  # MUST include 'Bearer '
    "Content-Type": "application/json"
}

data = {
    "model": "openai/gpt-3.5-turbo",  # safer to test with this model first
    "messages": [
        {"role": "user", "content": "what is the name of india?"}
    ]
}

response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

result = response.json()

try:
    reply = result['choices'][0]['message']['content']
    print("Chatbot:", reply)
except KeyError:
    print("Error:", result.get("error", "Unknown error"))
