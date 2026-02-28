import requests
import os

API_KEY = os.getenv("HUGGINGFACE_API_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

API_URL = "https://router.huggingface.co/hf-inference/models/google/flan-t5-base"

payload = {
    "inputs": "Is it safe to go outside if PM2.5 is 320?"
}

response = requests.post(API_URL, headers=headers, json=payload)

print(response.json())