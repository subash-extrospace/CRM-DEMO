import requests

GRAPH_URL = "https://graph.facebook.com/v23.0"


def subscribe_app_to_waba(waba_id, access_token):
    url = f"{GRAPH_URL}/{waba_id}/subscribed_apps"

    requests.post(url, params={"access_token": access_token}, timeout=30)
