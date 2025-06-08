from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/")
async def webhook_handler(request: Request):
    payload = await request.json()
    print("Received payload:", payload)
    return {"message": "Webhook received"}
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Webhook handler is live!"}
