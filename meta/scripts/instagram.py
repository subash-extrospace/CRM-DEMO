import requests

GRAPH_URL = "https://graph.facebook.com/v23.0"


def get_facebook_instagram_pages(access_token: str):
    """Fetches Facebook pages and checks if they have a linked Instagram account."""
    response = requests.get(
        f"{GRAPH_URL}/me/accounts",
        params={
            "fields": "name,access_token,instagram_business_account",
            "access_token": access_token,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
