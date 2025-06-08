from fastapi import FastAPI, Request
import json
from pydantic import BaseModel

app = FastAPI()

# Test GET route
@app.get("/")
def read_root():
    return {"message": "Webhook handler is live!"}

# POST webhook route
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("Received alert:", data)

    # Add your custom logic here (e.g., Dhan API call)
    return {"status": "success", "data": data}
POST https://<your-render-url>/webhook
Content-Type: application/json

{
  "symbol": "NIFTY",
  "action": "BUY",
  "price": 23000
}
