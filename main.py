from fastapi import FastAPI, Request
from danhq import Dhan
import os

app = FastAPI()

# ====== API Credentials ======
API_KEY = "1000591159"  # Your Client ID
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzUxMDUxMzM1LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiaHR0cHM6Ly93ZWJob29rLWhhbmRsZXItNmx1eS5vbnJlbmRlci5jb20iLCJkaGFuQ2xpZW50SWQiOiIxMDAwNTkxMTU5In0.f-1VYtckHZUlDnEUAlKXWIZH_d0MBSBUh6DA7gyRX9NU7J69fSHARu4TdwwWoiUGNVJOJ0R4dLcX7wirvkGLlQ"  # Full access token

# ====== Initialize Dhan Client ======
dhan = Dhan(api_key=API_KEY, access_token=ACCESS_TOKEN)

@app.get("/")
def root():
    return {"message": "Webhook handler is live and working!"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    
    symbol = data.get("symbol", "NIFTY")
    option_type = data.get("type", "CE")  # CE or PE
    transaction_type = data.get("side", "BUY")  # BUY or SELL
    qty = int(data.get("qty", 75))

    # STEP 1: Get list of NIFTY option instruments
    instruments = dhan.get_instruments(exchange_segment="NSE_FNO", security_type="OPTIDX")

    # STEP 2: Filter only for required type (CE or PE) and symbol
    filtered = [
        i for i in instruments 
        if i['symbol'].upper() == symbol 
        and i['optionType'] == option_type
        and i['tradingSymbol'].startswith(symbol)
        and i['expiryDate'] >= i['expiryDate']  # Ensures valid expiry
    ]

    # STEP 3: Sort by nearest expiry
    sorted_filtered = sorted(filtered, key=lambda x: x['expiryDate'])

    if not sorted_filtered:
        return {"error": "No matching options found"}

    # STEP 4: Pick the nearest ATM strike
    ltp = float(data.get("lastTradedPrice", 23500))
    atm_strike = min(sorted_filtered, key=lambda x: abs(float(x["strikePrice"]) - ltp))

    # STEP 5: Extract securityId
    security_id = atm_strike["securityId"]

    # STEP 6: Create order payload
    order = {
        "securityId": security_id,
        "transactionType": transaction_type,
        "exchangeSegment": "NSE_FNO",
        "productType": "INTRADAY",
        "orderType": "MARKET",
        "quantity": qty,
        "price": 0,
        "orderValidity": "DAY"
    }

    # STEP 7: Place the order
    try:
        response = dhan.place_order(order)
        return {"status": "Order Placed", "response": response}
    except Exception as e:
        return {"status": "Order Failed", "error": str(e)}
