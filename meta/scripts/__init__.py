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


def extend_user_access_token(app_id: str, app_secret: str, short_token: str):
    """Exchanges a 2-hour short-lived token for a 60-day long-lived token."""
    response = requests.get(
        f"{GRAPH_URL}/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_token,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("access_token")
