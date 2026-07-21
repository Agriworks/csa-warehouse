import requests
import os

token = "114273893325363479564" # from the logs
headers = {"Authorization": f"Bearer {token}"}
resp = requests.get("http://localhost:8000/presignedURL?filename=test.csv", headers=headers)
print(resp.json())
