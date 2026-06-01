import requests
from meta.database import whatsapp_numbers

GRAPH_URL = "https://graph.facebook.com/v23.0"


def get_whatsapp_business_accounts(access_token: str):
    """
    Fetches all WhatsApp Business Accounts (WABAs) across all Meta Businesses
    the logged-in user has access to.
    """
    all_wabas = []

    # 1. Fetch all Meta Businesses connected to this user
    try:
        biz_response = requests.get(
            f"{GRAPH_URL}/me/businesses",
            params={"access_token": access_token},
            timeout=30,
        )
        biz_response.raise_for_status()
        businesses = biz_response.json().get("data", [])
    except Exception as e:
        print(f"Error fetching Meta Businesses: {e}")
        return {"data": []}

    # 2. Loop through each Meta Business to fetch its owned WABAs
    for biz in businesses:
        business_id = biz.get("id")
        try:
            waba_response = requests.get(
                f"{GRAPH_URL}/{business_id}",
                params={
                    "fields": "owned_whatsapp_business_accounts",
                    "access_token": access_token,
                },
                timeout=30,
            )
            waba_response.raise_for_status()
            waba_data = waba_response.json()
            print(f"Business ID {business_id} WABA response:", waba_response)
            print("Response content:", waba_response.text)

            # Extract the inner data array from owned_whatsapp_business_accounts
            owned_wabas = waba_data.get("owned_whatsapp_business_accounts", {}).get(
                "data", []
            )
            all_wabas.extend(owned_wabas)

        except Exception as e:
            print(f"Error fetching WABAs for Business ID {business_id}: {e}")
            continue
    print("All WABAs found:", all_wabas)
    # Return a structured format matching Meta's native array structure
    return {"data": all_wabas}


def get_whatsapp_phone_numbers(waba_id: str, access_token: str):
    """Fetches verified phone numbers inside a specific WhatsApp Business Account."""
    response = requests.get(
        f"{GRAPH_URL}/{waba_id}/phone_numbers",
        params={"access_token": access_token},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def send_whatsapp_message(
    phone_number_id: str, access_token: str, recipient_phone: str, message_text: str
):
    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_phone,
        "type": "text",
        "text": {"body": message_text},
    }

    response = requests.post(url, headers=headers, json=payload)

    return response


def handle_whatsapp_messages(body):
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
