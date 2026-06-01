def subscribe_page(page_id, page_access_token):
    import requests

    response = requests.post(
        f"https://graph.facebook.com/v23.0/{page_id}/subscribed_apps",
        params={"access_token": page_access_token},
    )

    return response.json()
