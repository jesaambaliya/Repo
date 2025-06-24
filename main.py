from fastapi import FastAPI, Request
from danhq import Dhan
import os

app = FastAPI()

# Load credentials
API_KEY = os.getenv("1000591159")
ACCESS_TOKEN = os.getenv("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzUxMDUxMzM1LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiaHR0cHM6Ly93ZWJob29rLWhhbmRsZXItNmx1eS5vbnJlbmRlci5jb20iLCJkaGFuQ2xpZW50SWQiOiIxMDAwNTkxMTU5In0.f-1VYtckHZUlDnEUAlKXWIZH_d0MBSBUh6DA7gyRX9NU7J69fSHARu4TdwwWoiUGNVJOJ0R4dLcX7wirvkGLlQ")

# Initialize Dhan client
dhan = Dhan(api_key=API_KEY, access_token=ACCESS_TOKEN)

@app.get("/")
def root():
    return {"message": "Webhook handler is live!"}

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()

    symbol = payload.get("symbol")  # e.g., "NIFTY"
    side = payload.get("side")      # "BUY" or "SELL"
    option_type = payload.get("type")  # "CE" or "PE"
    qty = int(payload.get("qty", 75))  # default to 1 lot

    # Get correct securityId from Dhan (hardcoded here or fetched dynamically)
    if symbol == "NIFTY":
        security_id = "<YOUR_NIFTY_ATM_CE_ID>" if option_type == "CE" else "<YOUR_NIFTY_ATM_PE_ID>"
    else:
        return {"error": "Invalid symbol"}

    order_data = {
        "securityId": security_id,
        "transactionType": "BUY" if side == "BUY" else "SELL",
        "exchangeSegment": "NFO",
        "productType": "INTRADAY",
        "orderType": "MARKET",
        "quantity": qty,
        "price": 0,  # Market order
        "orderValidity": "DAY"
    }

    # Place the order
    response = dhan.place_order(order_data)
    return {"status": "success", "response": response}
