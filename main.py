from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

# Replace these with your actual credentials
DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID", "1000591159")
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzUxMDUxMzM1LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiaHR0cHM6Ly93ZWJob29rLWhhbmRsZXItNmx1eS5vbnJlbmRlci5jb20iLCJkaGFuQ2xpZW50SWQiOiIxMDAwNTkxMTU5In0.f-1VYtckHZUlDnEUAlKXWIZH_d0MBSBUh6DA7gyRX9NU7J69fSHARu4TdwwWoiUGNVJOJ0R4dLcX7wirvkGLlQ")

DHAN_BASE_URL = "https://api.dhan.co"

@app.get("/")
def read_root():
    return {"message": "Webhook handler is live!"}

@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    print("Received webhook:", data)

    try:
        symbol = data["symbol"]
        side = data["action"]  # "BUY" or "SELL"
        product_type = data.get("productType", "INTRADAY")
        order_type = data.get("orderType", "MARKET")
        quantity = data.get("quantity", 75)
        exchange_segment = data.get("exchangeSegment", "NSE_FNO")

        headers = {
            "access-token": DHAN_ACCESS_TOKEN,
            "client-id": DHAN_CLIENT_ID,
            "Content-Type": "application/json"
        }

        payload = {
            "symbol": symbol,
            "transactionType": side,
            "exchangeSegment": exchange_segment,
            "productType": product_type,
            "orderType": order_type,
            "quantity": quantity,
            "price": 0,
            "triggerPrice": 0,
            "afterMarketOrder": False,
            "amoTime": "OPEN",
            "disclosedQuantity": 0,
            "validity": "DAY"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{DHAN_BASE_URL}/orders", headers=headers, json=payload)

        print("Order response:", response.json())
        return response.json()

    except Exception as e:
        print("Error handling webhook:", e)
        return {"error": str(e)}
