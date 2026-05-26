import requests

PAGE_ACCESS_TOKEN = "EAAj4GJK1lnIBRnCMXZANmc8AyF3FHgn3l6Dlu1ZC3hv9eAYm2q8H12gZB0VqQE2riEZAagDdOB9ugERnetae6wLcQYHg9tPza5NDm8Q6ISNBElC0D7ifr7VraL0q45ZAkaGclrZCpZCegTJmjO9433uM1PoiurxIZAfiq7DtQS5JQkQ2umPbuZB5bKEZC0akh3UYh02Ph4FmaZAtAZDZD"


def send_messenger_message(recipient_id: str, message: str):

    url = "https://graph.facebook.com/v22.0/me/messages"

    headers = {"Content-Type": "application/json"}

    params = {"access_token": PAGE_ACCESS_TOKEN}

    payload = {"recipient": {"id": recipient_id}, "message": {"text": message}}

    response = requests.post(url, headers=headers, params=params, json=payload)

    print("\n======================")
    print("MESSENGER SEND RESPONSE")
    print(response.json())
    print("======================\n")

    return response
