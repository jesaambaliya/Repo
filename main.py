from fastapi import FastAPI, Request
from dhan import Dhan
import os

app = FastAPI()

# Replace with your live values
client_id = os.environ.get("1000591159")
access_token = os.environ.get("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzUxMDUxMzM1LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiaHR0cHM6Ly93ZWJob29rLWhhbmRsZXItNmx1eS5vbnJlbmRlci5jb20iLCJkaGFuQ2xpZW50SWQiOiIxMDAwNTkxMTU5In0.f-1VYtckHZUlDnEUAlKXWIZH_d0MBSBUh6DA7gyRX9NU7J69fSHARu4TdwwWoiUGNVJOJ0R4dLcX7wirvkGLlQ")

dhan = Dhan(client_id=client_id, access_token=access_token)

# Predefined mapping of strikes (for testing)
live_strike_map = {
    "CE": {
        "24500": "101000010245542"  # Replace with live CE securityId
    },
    "PE": {
        "24500": "101000010245543"  # Replace with live PE securityId
    }
}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        payload = await request.json()
        symbol = payload.get("symbol")
        side = payload.get("side")
        option_type = payload.get("type")
        qty = int(payload.get("qty", 75))
        ltp = float(payload.get("lastTradedPrice"))

        # ATM strike
        strike = str(round(ltp / 50) * 50)

        if symbol != "NIFTY":
            return {"status": "Error", "message": "Only NIFTY supported."}

        # Get securityId from map
        security_id = live_strike_map[option_type][strike]

        order_data = {
            "securityId": security_id,
            "transactionType": "BUY" if side == "BUY" else "SELL",
            "exchangeSegment": "NSE_FNO",
            "productType": "INTRADAY",
            "orderType": "MARKET",
            "quantity": qty,
            "price": 0,
            "orderValidity": "DAY"
        }

        response = dhan.place_order(order_data)
        return {"status": "Order Placed", "response": response}
    
    except Exception as e:
        print("Webhook error:", str(e))
        return {"status": "Error", "message": str(e)}
