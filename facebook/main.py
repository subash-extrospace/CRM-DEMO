from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from facebook.scripts.subscribe import subscribe_page

from facebook.config import (
    META_APP_ID,
    META_APP_SECRET,
    META_REDIRECT_URI,
    META_VERIFY_TOKEN,
)

from facebook.facebook import exchange_code_for_token, get_user_pages, send_message

from facebook.database import facebook_pages

app = FastAPI()


@app.get("/facebook/connect")
def connect_facebook():

    login_url = (
        "https://www.facebook.com/v23.0/dialog/oauth"
        f"?client_id={META_APP_ID}"
        f"&redirect_uri={META_REDIRECT_URI}"
        "&scope="
        "pages_manage_metadata,"
        "pages_read_engagement,"
        "pages_messaging,"
        "business_management"
    )

    return {"login_url": login_url}


@app.get("/facebook/callback")
def facebook_callback(code: str):

    token_response = exchange_code_for_token(
        app_id=META_APP_ID,
        app_secret=META_APP_SECRET,
        redirect_uri=META_REDIRECT_URI,
        code=code,
    )

    user_access_token = token_response["access_token"]

    pages = get_user_pages(user_access_token)

    for page in pages.get("data", []):

        facebook_pages[page["id"]] = {
            "page_name": page["name"],
            "page_access_token": page["access_token"],
        }

        subscribe_page(page["id"], page["access_token"])

    return {"success": True, "pages": pages.get("data", [])}


@app.get("/facebook/webhook")
def verify_webhook(
    hub_mode: str = None, hub_verify_token: str = None, hub_challenge: str = None
):

    if hub_mode == "subscribe" and hub_verify_token == META_VERIFY_TOKEN:
        return int(hub_challenge)

    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/facebook/webhook")
async def receive_webhook(request: Request):

    body = await request.json()

    if body.get("object") != "page":
        return {"status": "ignored"}

    for entry in body.get("entry", []):

        for messaging in entry.get("messaging", []):

            sender = messaging.get("sender", {})
            recipient = messaging.get("recipient", {})
            message = messaging.get("message")

            if not message:
                continue

            sender_id = sender.get("id")
            page_id = recipient.get("id")

            print("Incoming Message")
            print("Sender:", sender_id)
            print("Page:", page_id)
            print("Text:", message.get("text"))

            page_info = facebook_pages.get(page_id)

            if not page_info:
                continue

            send_message(
                page_access_token=page_info["page_access_token"],
                recipient_id=sender_id,
                message="Hello how can i assist you today",
            )

    return {"status": "ok"}
