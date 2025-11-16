import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"Using API Key: {api_key}")

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "llama3-8b-8192",
    "messages": [
        {"role": "system", "content": "You are a helpful Barangay Official."},
        {"role": "user", "content": "Paano kumuha ng barangay clearance?"}
    ]
}

response = requests.post(url, json=payload, headers=headers)

print(f"Status code: {response.status_code}")
print(response.text)
