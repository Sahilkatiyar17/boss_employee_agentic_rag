import requests

FASTAPI_URL = "http://127.0.0.1:8000"

def call_rag_api(query: str):
    response = requests.post(
        f"{FASTAPI_URL}/chat",
        json={"query": query},
        headers={"Content-Type": "application/json"},
        timeout=120
    )

    print("STATUS:", response.status_code)
    print("RAW RESPONSE:", response.text)   # 👈 VERY IMPORTANT

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()
