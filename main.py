from fastapi import FastAPI, Request
from dhanhq import Dhan
import os

app = FastAPI()

# Load credentials securely
API_KEY = os.getenv("DHAN_CLIENT_ID", "1000591159")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzUxMDUxMzM1LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiaHR0cHM6Ly93ZWJob29rLWhhbmRsZXItNmx1eS5vbnJlbmRlci5jb20iLCJkaGFuQ2xpZW50SWQiOiIxMDAwNTkxMTU5In0.f-1VYtckHZUlDnEUAlKXWIZH_d0MBSBUh6DA7gyRX9NU7J69fSHARu4TdwwWoiUGNVJOJ0R4dLcX7wirvkGLlQ")

# Initialize Dhan client
dhan = Dhan(api_key=API_KEY, access_token=ACCESS_TOKEN)

@app.get("/")
def root():
    return {"message": "Webhook handler is live!"}

@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    print("Received webhook:", data)

    try:
        # Build order object
        order = DhanOrder(
            symbol=data["symbol"],
            transactionType=data["side"],
            exchangeSegment=data.get("exchangeSegment", "NSE_FNO"),
            productType=data.get("productType", "INTRADAY"),
            orderType=data.get("orderType", "MARKET"),
            quantity=int(data.get("quantity", 75)),
            price=0,
            triggerPrice=0,
            validity="DAY",
        )
        # Place order using helper
        resp = dhan.place_order(order)

        print("Order API Response:", resp)
        return resp

    except Exception as e:
        print("Error placing order:", e)
        return {"error": str(e)}
