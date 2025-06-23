from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID", "1000591159")
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzUxMDUxMzM1LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiaHR0cHM6Ly93ZWJob29rLWhhbmRsZXItNmx1eS5vbnJlbmRlci5jb20iLCJkaGFuQ2xpZW50SWQiOiIxMDAwNTkxMTU5In0.f-1VYtckHZUlDnEUAlKXWIZH_d0MBSBUh6DA7gyRX9NU7J69fSHARu4TdwwWoiUGNVJOJ0R4dLcX7wirvkGLlQ")
DHAN_BASE_URL = "https://api.dhan.co"

@app.get("/")
def root():
    return {"message": "Webhook handler is live!"}

@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        data = await request.json()
        print("Received Data:", data)

        payload = {
            "symbol": data["symbol"],
            "transactionType": data["side"],  # "BUY" or "SELL"
            "exchangeSegment": data.get("exchangeSegment", "NSE_FNO"),
            "productType": data.get("productType", "INTRADAY"),
            "orderType": data.get("orderType", "MARKET"),
            "quantity": data.get("quantity", 75),
            "price": 0,
            "triggerPrice": 0,
            "afterMarketOrder": False,
            "amoTime": "OPEN",
            "disclosedQuantity": 0,
            "validity": "DAY"
        }

        headers = {
            "access-token": DHAN_ACCESS_TOKEN,
            "client-id": DHAN_CLIENT_ID,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{DHAN_BASE_URL}/orders", headers=headers, json=payload)

        print("Order Response:", response.text)
        return response.json()

    except Exception as e:
        print("Webhook Error:", e)
        return {"error": str(e)}
