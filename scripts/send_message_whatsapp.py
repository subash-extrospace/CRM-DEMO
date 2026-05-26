import requests

PHONE_NUMBER_ID = "1050012661539701"
ACCESS_TOKEN = "EAAj4GJK1lnIBRjZAtVuNMhKs5FxQFq1VA77uTgOeT2jOtNY8NPSIpO69DfZA6RgcQoIH4ZBz6QZATgXpVVWZBkDAgJwv7APlnQAdpL0JbR8SmgqXCPhq1d9EzTlDqUxGHsTz934ZASwmNMcIZCTOVxaX36ZAZAIOfgpatMnsgBZCe1lAhIhC6FlHa7zOlgNBXXR8uEdlGQAPjgGhHKIxZBWCPbjiqwZCYpMwM7tu9jwv0xZBp6ZAALsf1O1GhRZCi5TM1DisXczrHZCPWST8fBnEjqcpBjTss3MZCAZA4ZD"


def send_whatsapp_message(sender, message):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": sender,
        "type": "text",
        "text": {"body": message},
    }

    response = requests.post(url, headers=headers, json=payload)

    return response
