import requests

GRAPH_URL = "https://graph.facebook.com/v23.0"


def exchange_code_for_token(app_id: str, app_secret: str, redirect_uri: str, code: str):
    response = requests.get(
        f"{GRAPH_URL}/oauth/access_token",
        params={
            "client_id": app_id,
            "client_secret": app_secret,
            "redirect_uri": redirect_uri,
            "code": code,
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


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
