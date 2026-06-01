import requests

GRAPH_URL = "https://graph.facebook.com/v23.0"


# def exchange_code_for_token(app_id: str, app_secret: str, redirect_uri: str, code: str):
#     """
#     Exchanges OAuth code for access token
#     (returned from Embedded Signup)
#     """
#     print("app_id:", app_id)
#     print("app_secret:", app_secret)
#     print("redirect_uri:", redirect_uri)
#     print("code:", code)

#     url = f"{GRAPH_URL}/oauth/access_token"

#     params = {
#         "client_id": app_id,
#         "client_secret": app_secret,
#         "redirect_uri": redirect_uri,
#         "code": code,
#     }

#     response = requests.get(url, params=params, timeout=30)
#     print("Token exchange response:", response)
#     if response.status_code != 200:
#         print("Meta Error Details:", response.text)
#     response.raise_for_status()

#     return response.json()


# def get_business_id(access_token: str):
#     """
#     Fetches Meta Business Manager account ID
#     """

#     url = f"{GRAPH_URL}/me/businesses"

#     params = {"access_token": access_token}

#     response = requests.get(url, params=params, timeout=30)
#     response.raise_for_status()

#     data = response.json()

#     if not data.get("data"):
#         raise Exception("No business accounts found")

#     return data["data"][0]["id"]


# def get_waba_id(access_token: str, business_id: str):
#     """
#     Fetch WhatsApp Business Accounts under a Business Manager
#     """

#     url = f"{GRAPH_URL}/" f"{business_id}/owned_whatsapp_business_accounts"

#     params = {"access_token": access_token}

#     response = requests.get(url, params=params, timeout=30)
#     response.raise_for_status()

#     data = response.json()

#     if not data.get("data"):
#         raise Exception("No WABA found")

#     return data["data"][0]["id"]


# def get_phone_number_id(access_token: str, waba_id: str):
#     """
#     Fetch WhatsApp phone number ID linked to WABA
#     """

#     url = f"{GRAPH_URL}/{waba_id}/phone_numbers"

#     params = {"access_token": access_token}

#     response = requests.get(url, params=params, timeout=30)
#     response.raise_for_status()

#     data = response.json()

#     if not data.get("data"):
#         raise Exception("No phone number found")

#     phone = data["data"][0]

#     return {
#         "phone_number_id": phone["id"],
#         "display_phone_number": phone.get("display_phone_number"),
#         "verified_name": phone.get("verified_name"),
#     }


# facebook/facebook.py


# def get_whatsapp_business_accounts(access_token: str):
#     """Fetches the WhatsApp Business Accounts by requesting it as a field on the /me node."""
#     response = requests.get(
#         f"{GRAPH_URL}/me/businesses",  # Requesting the base user node
#         params={
#             "access_token": access_token,
#             # "fields": "whatsapp_business_accounts",
#         },
#         timeout=30,
#     )
#     print("WhatsApp Business Accounts response:", response)
#     print("Response content:", response.text)
#     response.raise_for_status()

#     business_id = "188948312504244"
#     response = requests.get(
#         f"{GRAPH_URL}/{business_id}",
#         params={
#             "fields": "owned_whatsapp_business_accounts",
#             "access_token": access_token,
#         },
#     )
#     print("Owned WABA response:", response)
#     print("Response content:", response.text)
#     response.raise_for_status()

#     # Meta returns this nested inside a key matching the field name
#     return response.json().get("whatsapp_business_accounts", {"data": []})


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

            # Extract the inner data array from owned_whatsapp_business_accounts
            owned_wabas = waba_data.get("owned_whatsapp_business_accounts", {}).get(
                "data", []
            )
            all_wabas.extend(owned_wabas)

        except Exception as e:
            print(f"Error fetching WABAs for Business ID {business_id}: {e}")
            continue

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
