import requests

PAGE_ACCESS_TOKEN = "EAAj4GJK1lnIBRnCMXZANmc8AyF3FHgn3l6Dlu1ZC3hv9eAYm2q8H12gZB0VqQE2riEZAagDdOB9ugERnetae6wLcQYHg9tPza5NDm8Q6ISNBElC0D7ifr7VraL0q45ZAkaGclrZCpZCegTJmjO9433uM1PoiurxIZAfiq7DtQS5JQkQ2umPbuZB5bKEZC0akh3UYh02Ph4FmaZAtAZDZD"


# def process_meta_messages(body):
#     print("Received message:")
#     print(body)

#     print("\n==============================")
#     print("Incoming webhook message:")
#     print(body)
#     print("==============================\n")

#     object_type = body.get("object")

#     # ==========================================
#     # WHATSAPP
#     # ==========================================
#     if object_type == "whatsapp_business_account":

#         for entry in body.get("entry", []):
#             for change in entry.get("changes", []):

#                 value = change.get("value", {})
#                 messages = value.get("messages", [])
#                 contacts = value.get("contacts", [])

#                 if not messages:
#                     continue

#                 for msg in messages:

#                     sender_phone = msg.get("from")
#                     text = msg.get("text", {}).get("body")
#                     message_type = msg.get("type")

#                     profile_name = None

#                     if contacts:
#                         profile_name = contacts[0].get("profile", {}).get("name")

#                     print("WHATSAPP MESSAGE")
#                     print("Sender:", sender_phone)
#                     print("Name:", profile_name)
#                     print("Message:", text)
#                     print("Type:", message_type)

#     # ==========================================
#     # MESSENGER / FACEBOOK PAGE
#     # ==========================================
#     elif object_type == "page":

#         for entry in body.get("entry", []):
#             messaging_events = entry.get("messaging", [])

#             for event in messaging_events:

#                 sender_id = event.get("sender", {}).get("id")
#                 message = event.get("message", {})
#                 text = message.get("text")

#                 # ======================================
#                 # Fetch sender profile from Graph API
#                 # ======================================
#                 profile_url = f"https://graph.facebook.com/{sender_id}"

#                 params = {
#                     "fields": "name,profile_pic",
#                     "access_token": PAGE_ACCESS_TOKEN,
#                 }

#                 profile_response = requests.get(profile_url, params=params)

#                 profile_data = profile_response.json()

#                 sender_name = profile_data.get("name")
#                 profile_pic = profile_data.get("profile_pic")

#                 print("MESSENGER MESSAGE")
#                 print("Sender ID:", sender_id)
#                 print("Sender Name:", sender_name)
#                 print("Profile Picture:", profile_pic)
#                 print("Message:", text)

#     # ==========================================
#     # INSTAGRAM
#     # ==========================================
#     elif object_type == "instagram":

#         print("Instagram webhook received")
#         print(body)


def process_meta_messages(body):

    normalized_messages = []

    print("\n==============================")
    print("Incoming webhook message:")
    print(body)
    print("==============================\n")

    object_type = body.get("object")

    # ==========================================
    # WHATSAPP
    # ==========================================
    if object_type == "whatsapp_business_account":

        for entry in body.get("entry", []):
            for change in entry.get("changes", []):

                value = change.get("value", {})
                messages = value.get("messages", [])
                contacts = value.get("contacts", [])

                if not messages:
                    continue

                for msg in messages:

                    sender_phone = msg.get("from")
                    text = msg.get("text", {}).get("body")
                    message_type = msg.get("type")

                    profile_name = None

                    if contacts:
                        profile_name = contacts[0].get("profile", {}).get("name")

                    print("WHATSAPP MESSAGE")
                    print("Sender:", sender_phone)
                    print("Name:", profile_name)
                    print("Message:", text)
                    print("Type:", message_type)

                    # ==================================
                    # NORMALIZED MESSAGE
                    # ==================================
                    normalized_messages.append(
                        {
                            "platform": "whatsapp",
                            "sender": sender_phone,
                            "name": profile_name,
                            "message": text,
                            "message_type": message_type,
                        }
                    )

    # ==========================================
    # MESSENGER / FACEBOOK PAGE
    # ==========================================
    elif object_type == "page":

        for entry in body.get("entry", []):
            messaging_events = entry.get("messaging", [])

            for event in messaging_events:

                sender_id = event.get("sender", {}).get("id")
                message = event.get("message", {})
                # text = message.get("text")

                if not message:
                    continue

                # ======================================
                # Ignore bot/page echo messages
                # ======================================
                if message.get("is_echo"):
                    print("Ignoring echo message")
                    continue

                text = message.get("text")

                # ======================================
                # Ignore empty/non-text messages
                # ======================================
                if not text:
                    continue

                profile_url = f"https://graph.facebook.com/{sender_id}"

                params = {
                    "fields": "name,profile_pic",
                    "access_token": PAGE_ACCESS_TOKEN,
                }

                profile_response = requests.get(profile_url, params=params)

                profile_data = profile_response.json()

                sender_name = profile_data.get("name")
                profile_pic = profile_data.get("profile_pic")

                print("MESSENGER MESSAGE")
                print("Sender ID:", sender_id)
                print("Sender Name:", sender_name)
                print("Profile Picture:", profile_pic)
                print("Message:", text)

                # ==================================
                # NORMALIZED MESSAGE
                # ==================================
                normalized_messages.append(
                    {
                        "platform": "messenger",
                        "sender": sender_id,
                        "name": sender_name,
                        "profile_pic": profile_pic,
                        "message": text,
                    }
                )

    # ==========================================
    # INSTAGRAM
    # ==========================================
    elif object_type == "instagram":

        print("Instagram webhook received")
        print(body)

    return normalized_messages
