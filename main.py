from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/")
async def webhook_handler(request: Request):
    payload = await request.json()
    print("Received payload:", payload)
    return {"message": "Webhook received"}
