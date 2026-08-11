import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_API = os.getenv("BASE_API")
API_KEY = os.getenv("API_KEY")


def ask_dify(question, user_id, conversation_id=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "inputs": {"info": question},
        "query": question,
        "response_mode": "blocking",
        "user": str(user_id)}

    if conversation_id:
        data["conversation_id"] = conversation_id

    response = requests.post(BASE_API,headers=headers,json=data)

    print("Status:", response.status_code)
    print(response.text)

    result = response.json()

    return {
        "answer": result.get("answer"),
        "conversation_id": result.get("conversation_id")
    }