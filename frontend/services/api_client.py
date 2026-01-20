import requests

FASTAPI_URL = "http://127.0.0.1:8000"

def call_rag_api(query: str):
    response = requests.post(
        f"{FASTAPI_URL}/rag/answer",
        json={"query": query},
        headers={"Content-Type": "application/json"},
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()["answer"]
