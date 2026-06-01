from fastapi import APIRouter, FastAPI, HTTPException, Request
from meta.scripts.facebook import (
    subscribe_page,
    get_user_pages,
    handle_facebook_messages,
)
from meta.scripts.whatsapp import (
    get_whatsapp_business_accounts,
    get_whatsapp_phone_numbers,
    handle_whatsapp_messages,
)
from meta.config import (
    META_APP_ID,
    META_APP_SECRET,
    META_REDIRECT_URI,
    META_VERIFY_TOKEN,
)

from meta.scripts import exchange_code_for_token
from meta.database import facebook_pages, whatsapp_numbers, instagram_accounts
from meta.scripts import (
    extend_user_access_token,
)
from meta.scripts.instagram import get_facebook_instagram_pages

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
        "business_management,"
        "whatsapp_business_management,"
        "whatsapp_business_messaging,"
        "instagram_basic,"
        "instagram_manage_messages"
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
    # pages = get_user_pages(long_lived_token)

    # for page in pages.get("data", []):

    #     facebook_pages[page["id"]] = {
    #         "page_name": page["name"],
    #         "page_access_token": page["access_token"],
    #     }

    #     subscribe_page(page["id"], page["access_token"])

    pages_response = get_facebook_instagram_pages(long_lived_token)

    for page in pages_response.get("data", []):
        page_id = page["id"]
        page_token = page["access_token"]
        page_name = page["name"]

        # Store Facebook Page as you normally do
        facebook_pages[page_id] = {
            "page_name": page_name,
            "page_access_token": page_token,
        }
        subscribe_page(page_id, page_token)

        # Check if this Page has a linked Instagram Business Account
        if "instagram_business_account" in page:
            instagram_id = page["instagram_business_account"]["id"]

            instagram_accounts[instagram_id] = {
                "instagram_account_id": instagram_id,
                "associated_page_name": page_name,
                "page_access_token": page_token,  # Used to send replies
            }

    # 2. Handle WhatsApp Business Accounts
    try:
        waba_response = get_whatsapp_business_accounts(long_lived_token)
        for waba in waba_response.get("data", []):
            waba_id = waba["id"]
            waba_name = waba.get("name", "Unnamed WABA")

            # Fetch phone numbers for this WABA
            phone_response = get_whatsapp_phone_numbers(waba_id, long_lived_token)
            for phone in phone_response.get("data", []):
                whatsapp_numbers[phone["id"]] = {
                    "display_phone_number": phone["display_phone_number"],
                    "waba_id": waba_id,
                    "access_token": long_lived_token,  # Note: In production, exchange this for a long-lived/system token
                    "waba_name": waba_name,
                }
    except Exception as e:
        print(f"No WhatsApp accounts found or error occurred: {e}")

    return {
        "success": True,
        "pages": facebook_pages,
        "whatsapp": whatsapp_numbers,
        "instagram": instagram_accounts,
    }


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
        handle_facebook_messages(body)
        return {"status": "ok"}

    # --- HANDLE WHATSAPP MESSAGES ---
    elif body.get("object") == "whatsapp_business_account":
        handle_whatsapp_messages(body)

        return {"status": "ok"}

    return {"status": "ignored"}
