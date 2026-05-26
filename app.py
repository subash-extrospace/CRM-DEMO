from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
import uvicorn
import requests
from pydantic import BaseModel

from scripts.receive_messages import process_meta_messages
from scripts.send_message_whatsapp import send_whatsapp_message
from scripts.tasks import process_message_task

app = FastAPI()

# Your verify token whatsapp
VERIFY_TOKEN = "SUBASH123@"
ACCESS_TOKEN = "EAAj4GJK1lnIBRjZAtVuNMhKs5FxQFq1VA77uTgOeT2jOtNY8NPSIpO69DfZA6RgcQoIH4ZBz6QZATgXpVVWZBkDAgJwv7APlnQAdpL0JbR8SmgqXCPhq1d9EzTlDqUxGHsTz934ZASwmNMcIZCTOVxaX36ZAZAIOfgpatMnsgBZCe1lAhIhC6FlHa7zOlgNBXXR8uEdlGQAPjgGhHKIxZBWCPbjiqwZCYpMwM7tu9jwv0xZBp6ZAALsf1O1GhRZCi5TM1DisXczrHZCPWST8fBnEjqcpBjTss3MZCAZA4ZD"
PHONE_NUMBER_ID = "1050012661539701"


class SendMessageRequest(BaseModel):
    to: str
    message: str


@app.get("/webhook/meta")
async def verify_webhook(request: Request):
    """
    Meta webhook verification endpoint
    """

    hub_mode = request.query_params.get("hub.mode")
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")

    # Verify token
    print("Received webhook verification request:")
    print(f"hub.mode: {hub_mode}")
    print(f"hub.verify_token: {hub_verify_token}")
    print(f"hub.challenge: {hub_challenge}")
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        print("Webhook verified successfully!")
        return PlainTextResponse(content=hub_challenge, status_code=200)

    return PlainTextResponse(content="Verification failed", status_code=403)


@app.post("/webhook/meta")
async def receive_message(request: Request):
    """
    Receive incoming meta messages
    """

    body = await request.json()

    messages = process_meta_messages(body)

    # Save to database logic. For now, skip it.

    # ==========================================
    # Trigger Celery Task
    # ==========================================
    for msg in messages:

        process_message_task.delay(msg["platform"], msg["sender"], msg["message"])

    return JSONResponse(content={"status": "received"}, status_code=200)


@app.post("/whatsapp/send-message")
async def send_message(data: SendMessageRequest):
    response = send_whatsapp_message(data)
    return {"status_code": response.status_code, "response": response.json()}


@app.get("/")
async def root():
    return {"message": "WhatsApp CRM backend is running"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
