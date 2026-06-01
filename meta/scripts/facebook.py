import requests
from meta.database import facebook_pages

GRAPH_URL = "https://graph.facebook.com/v23.0"


def get_user_pages(access_token: str):
    response = requests.get(
        f"{GRAPH_URL}/me/accounts", params={"access_token": access_token}, timeout=30
    )

    response.raise_for_status()

    return response.json()


def send_message(page_access_token: str, recipient_id: str, message: str):
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message}}

    response = requests.post(
        f"{GRAPH_URL}/me/messages",
        params={"access_token": page_access_token},
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def subscribe_page(page_id, page_access_token):
    import requests

    response = requests.post(
        f"https://graph.facebook.com/v23.0/{page_id}/subscribed_apps",
        params={"access_token": page_access_token},
    )

    return response.json()


def handle_facebook_messages(body):
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
