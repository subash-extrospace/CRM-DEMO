import requests

from celery_app import celery
from scripts.send_message_messenger import send_messenger_message
from scripts.send_message_whatsapp import send_whatsapp_message

ACCESS_TOKEN = "EAAj4GJK1lnIBRjZAtVuNMhKs5FxQFq1VA77uTgOeT2jOtNY8NPSIpO69DfZA6RgcQoIH4ZBz6QZATgXpVVWZBkDAgJwv7APlnQAdpL0JbR8SmgqXCPhq1d9EzTlDqUxGHsTz934ZASwmNMcIZCTOVxaX36ZAZAIOfgpatMnsgBZCe1lAhIhC6FlHa7zOlgNBXXR8uEdlGQAPjgGhHKIxZBWCPbjiqwZCYpMwM7tu9jwv0xZBp6ZAALsf1O1GhRZCi5TM1DisXczrHZCPWST8fBnEjqcpBjTss3MZCAZA4ZD"
PHONE_NUMBER_ID = "1050012661539701"


# @celery.task
# def process_message_task(phone_number: str, user_message: str):

#     print("\n======================")
#     print("CELERY TASK STARTED")
#     print("Phone:", phone_number)
#     print("Message:", user_message)
#     print("======================\n")

#     # ==========================================
#     # Fake AI response
#     # ==========================================
#     ai_reply = "Hello how can i help you?"

#     # ==========================================
#     # Send WhatsApp Message
#     # ==========================================
#     url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

#     headers = {
#         "Authorization": f"Bearer {ACCESS_TOKEN}",
#         "Content-Type": "application/json",
#     }

#     payload = {
#         "messaging_product": "whatsapp",
#         "to": phone_number,
#         "type": "text",
#         "text": {"body": ai_reply},
#     }

#     response = requests.post(url, headers=headers, json=payload)

#     print("WhatsApp Response:")
#     print(response.json())


@celery.task
def process_message_task(platform: str, sender: str, user_message: str):

    print("\n======================")
    print("CELERY TASK STARTED")
    print("Platform:", platform)
    print("Sender:", sender)
    print("Message:", user_message)
    print("======================\n")

    # ==========================================
    # Fake AI Response
    # ==========================================
    ai_reply = "Hello how can i help you?"

    # ==========================================
    # WHATSAPP
    # ==========================================
    if platform == "whatsapp":

        send_whatsapp_message(sender, ai_reply)

    # ==========================================
    # MESSENGER
    # ==========================================
    elif platform == "messenger":

        send_messenger_message(sender, ai_reply)
