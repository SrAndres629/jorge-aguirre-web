
import requests
import json

headers = {
    "apikey": "B89599B2-37E4-4DCA-92D3-87F8674C7D69"
}

try:
    response = requests.get("http://localhost:8081/instance/fetchInstances", headers=headers)
    data = response.json()
    for item in data:
        print(f"ID: {item.get('id')}")
        print(f"INSTANCEID: {item.get('instanceId')}")



except Exception as e:
    print(f"Error: {e}")
