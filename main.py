from fastapi import FastAPI, Request
from danhq import Dhan
import os

app = FastAPI()

# Load credentials (store these in environment variables in Render)
API_KEY = os.getenv("API_KEY") or "1000591159"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN") or "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzUxMDUxMzM1LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiaHR0cHM6Ly93ZWJob29rLWhhbmRsZXItNmx1eS5vbnJlbmRlci5jb20iLCJkaGFuQ2xpZW50SWQiOiIxMDAwNTkxMTU5In0.f-1VYtckHZUlDnEUAlKXWIZH_d0MBSBUh6DA7gyRX9NU7J69fSHARu4TdwwWoiUGNVJOJ0R4dLcX7wirvkGLlQ"

# Initialize Dhan client
dhan = Dhan(api_key=API_KEY, access_token=ACCESS_TOKEN)

@app.get("/")
def root():
    return {"message": "Webhook handler is live!"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        payload = await request.json()

        # Log full payload for debug
        print("Received Payload:", payload)

        # Extract fields safely
        symbol = payload.get("symbol", "NIFTY")
        side = payload.get("side")
        option_type = payload.get("type")  # CE or PE
        qty = int(payload.get("quantity", 75))  # default to 1 lot
        action = payload.get("action")  # ENTRY or EXIT
        last_price = float(payload.get("lastTradedPrice", 0.0))

        # Validate required fields
        if not all([side, option_type, action]):
            return {"error": "Missing required fields (side/type/action)"}

        # Placeholder logic for ATM strike and security ID
        if option_type == "CE":
            security_id = "104069"  # e.g., dummy NIFTY CE
        elif option_type == "PE":
            security_id = "104070"  # e.g., dummy NIFTY PE
        else:
            return {"error": "Invalid option type"}

        transaction_type = "BUY" if action == "ENTRY" else "SELL"

        order_data = {
        "securityId": security_id,
        "transactionType": transaction_type,
        "exchangeSegment": "NSE_FNO",
        "productType": "INTRADAY",
        "orderType": "MARKET",
        "quantity": qty,
        "price": 0,
        "orderValidity": "DAY"
}


        print("Placing Order:", order_data)
        response = dhan.place_order(order_data)
        return {"status": "Order Placed", "response": response}

    except Exception as e:
        print("Webhook error:", str(e))
        return {"error": str(e)}
