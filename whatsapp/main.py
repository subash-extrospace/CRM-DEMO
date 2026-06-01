from fastapi import APIRouter, FastAPI, HTTPException, Request
from facebook.scripts.subscribe import subscribe_page
from whatsapp.config import (
    META_APP_ID,
    WHATSAPP_EMBEDDED_SIGNUP_CONFIG_ID,
    META_APP_SECRET,
    WHATSAPP_REDIRECT_URI,
    META_REDIRECT_URI,
    META_VERIFY_TOKEN,
)
from fastapi.responses import FileResponse
from whatsapp.schemas import WhatsAppCallbackRequest

# from whatsapp.scripts.whatsapp_utils import (
#     exchange_code_for_token,
#     get_business_id,
#     get_waba_id,
#     get_phone_number_id,
# )
from facebook.facebook import exchange_code_for_token, get_user_pages
from facebook.database import facebook_pages
from whatsapp.scripts.whatsapp_utils import (
    extend_user_access_token,
    get_whatsapp_business_accounts,
    get_whatsapp_phone_numbers,
    send_whatsapp_message,
)
from whatsapp.scripts.subscribe import subscribe_app_to_waba
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# @app.get("/")
# def frontend():
#     return FileResponse("whatsapp/frontend/index.html")


# @app.get("/whatsapp/connect")
# def connect_whatsapp():
#     print("Initiating WhatsApp connection...")
#     print(f"Using App ID: {META_APP_ID}")
#     print("Whatsapp Embedded Signup Config ID:", WHATSAPP_EMBEDDED_SIGNUP_CONFIG_ID)

#     return {
#         "app_id": META_APP_ID,
#         "config_id": WHATSAPP_EMBEDDED_SIGNUP_CONFIG_ID,
#     }


# @app.post("/whatsapp/callback")
# def whatsapp_callback(body: WhatsAppCallbackRequest):

#     token_data = exchange_code_for_token(
#         app_id=META_APP_ID,
#         app_secret=META_APP_SECRET,
#         redirect_uri=WHATSAPP_REDIRECT_URI,
#         code=body.code,
#     )

#     access_token = token_data["access_token"]

#     business_id = get_business_id(access_token)

#     waba_id = get_waba_id(access_token, business_id)

#     phone_data = get_phone_number_id(access_token, waba_id)

#     subscribe_app_to_waba(waba_id, access_token)

#     return {
#         "tenant_id": body.tenant_id,
#         "business_id": business_id,
#         "waba_id": waba_id,
#         "phone_number_id": phone_data["phone_number_id"],
#         "display_phone_number": phone_data["display_phone_number"],
#         "access_token": access_token,
#     }


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
        "business_management,"
        "whatsapp_business_management,"  # Added
        "whatsapp_business_messaging"  # Added
    )
    return {"login_url": login_url}


from whatsapp.database import (
    whatsapp_numbers,
)  # Assume you create this dictionary/DB table


@app.get("/facebook/callback")
def facebook_callback(code: str):
    token_response = exchange_code_for_token(
        app_id=META_APP_ID,
        app_secret=META_APP_SECRET,
        redirect_uri=META_REDIRECT_URI,
        code=code,
    )
    short_token = token_response["access_token"]
    try:
        long_lived_token = extend_user_access_token(
            app_id=META_APP_ID, app_secret=META_APP_SECRET, short_token=short_token
        )
    except Exception as e:
        print(f"Failed to extend token, falling back to short token: {e}")
        long_lived_token = short_token

    # 1. Handle Facebook Pages (Your existing code stays here...)
    pages = get_user_pages(long_lived_token)

    for page in pages.get("data", []):

        facebook_pages[page["id"]] = {
            "page_name": page["name"],
            "page_access_token": page["access_token"],
        }

        subscribe_page(page["id"], page["access_token"])

    # 2. Handle WhatsApp Business Accounts
    try:
        waba_response = get_whatsapp_business_accounts(long_lived_token)
        for waba in waba_response.get("data", []):
            waba_id = waba["id"]

            # Fetch phone numbers for this WABA
            phone_response = get_whatsapp_phone_numbers(waba_id, long_lived_token)
            for phone in phone_response.get("data", []):
                whatsapp_numbers[phone["id"]] = {
                    "display_phone_number": phone["display_phone_number"],
                    "waba_id": waba_id,
                    "access_token": long_lived_token,  # Note: In production, exchange this for a long-lived/system token
                }
    except Exception as e:
        print(f"No WhatsApp accounts found or error occurred: {e}")

    return {"success": True, "pages": facebook_pages, "whatsapp": whatsapp_numbers}


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
    print("Received webhook event:", body)

    # --- HANDLE FACEBOOK PAGES ---
    if body.get("object") == "page":
        # ... your existing Facebook loop code ...
        return {"status": "ok"}

    # --- HANDLE WHATSAPP MESSAGES ---
    elif body.get("object") == "whatsapp_business_account":
        for entry in body.get("entry", []):
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})

                # Check if it contains messages
                if "messages" in value:
                    for message in value["messages"]:
                        # Extract details
                        sender_phone = message.get("from")  # Customer's phone number
                        message_id = message.get("id")
                        msg_type = message.get("type")

                        # Extract text
                        text_body = ""
                        if msg_type == "text":
                            text_body = message.get("text", {}).get("body")

                        # Get your own business phone ID (to look up token)
                        phone_id = value.get("metadata", {}).get("phone_number_id")

                        print(
                            f"Incoming WhatsApp from {sender_phone} to ID {phone_id}: {text_body}"
                        )

                        # Look up your stored tokens
                        phone_info = whatsapp_numbers.get(phone_id)
                        if not phone_info:
                            continue

                        # Send a reply!
                        send_whatsapp_message(
                            phone_number_id=phone_id,
                            access_token=phone_info["access_token"],
                            recipient_phone=sender_phone,
                            message_text="Hello! How can I assist you with WhatsApp today?",
                        )

        return {"status": "ok"}

    return {"status": "ignored"}
