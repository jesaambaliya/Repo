from fastapi import FastAPI, Request
import httpx
from datetime import datetime, timedelta
import os
import json

app = FastAPI()

# ⚙️ Your Dhan credentials
DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID", "1000591159")
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzUxMDUxMzM1LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiaHR0cHM6Ly93ZWJob29rLWhhbmRsZXItNmx1eS5vbnJlbmRlci5jb20iLCJkaGFuQ2xpZW50SWQiOiIxMDAwNTkxMTU5In0.f-1VYtckHZUlDnEUAlKXWIZH_d0MBSBUh6DA7gyRX9NU7J69fSHARu4TdwwWoiUGNVJOJ0R4dLcX7wirvkGLlQ")
DHAN_BASE_URL = "https://api.dhan.co"

# 📅 Get next Thursday expiry date
def get_next_thursday():
    today = datetime.now()
    days_ahead = 3 - today.weekday()  # Thursday is weekday 3
    if days_ahead <= 0:
        days_ahead += 7
    next_thursday = today + timedelta(days=days_ahead)
    return next_thursday.strftime('%Y-%m-%d')

# 🎯 Round NIFTY index to nearest 50 for ATM strike
def round_to_nearest_50(x):
    return int(round(x / 50.0) * 50)

@app.get("/")
def root():
    return {"message": "Webhook handler is live!"}

@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        data = await request.json()
        print("Received:", data)

        action = data["action"]  # "BUY" or "SELL"
        option_type = data["type"]  # "CE" or "PE"
        product_type = data.get("productType", "INTRADAY")
        order_type = data.get("orderType", "MARKET")
        quantity = data.get("quantity", 75)

        expiry = get_next_thursday()

        # 🔍 Get NIFTY index price
        async with httpx.AsyncClient() as client:
            index_response = await client.get(
                f"{DHAN_BASE_URL}/market/feed/indices?index=Nifty%2050&exchange=NSE"
            )
            index_data = index_response.json()
            nifty_price = float(index_data["lastTradedPrice"]) / 100

        strike_price = round_to_nearest_50(nifty_price)

        # 🔍 Load instrument list from file
        with open("instruments.json", "r") as f:
            instruments = json.load(f)

        # 🔍 Filter instrument
        matching = next(
            (
                i for i in instruments
                if i["expiryDate"] == expiry and
                   i["optionType"] == option_type and
                   i["strikePrice"] == strike_price and
                   i["tradingSymbol"].startswith("NIFTY")
            ),
            None
        )

        if not matching:
            return {"error": f"No matching instrument for {strike_price}{option_type} {expiry}"}

        security_id = matching["securityId"]

        payload = {
            "securityId": security_id,
            "transactionType": action,
            "exchangeSegment": "NSE_FNO",
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

        headers = {
            "access-token": DHAN_ACCESS_TOKEN,
            "client-id": DHAN_CLIENT_ID,
            "Content-Type": "application/json"
        }

        # 🚀 Place order
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{DHAN_BASE_URL}/orders", headers=headers, json=payload)
            print("Order response:", res.text)
            return res.json()

    except Exception as e:
        print("Webhook error:", str(e))
        return {"error": str(e)}
