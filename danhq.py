import httpx

class Dhan:
    def __init__(self, api_key, access_token):
        self.api_key = api_key
        self.access_token = access_token
        self.base_url = "https://api.dhan.co"

    def place_order(self, payload):
        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/json"
        }
        url = f"{self.base_url}/orders"
        response = httpx.post(url, headers=headers, json=payload)
        return response.json()
