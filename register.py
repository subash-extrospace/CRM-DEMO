import requests

ACCESS_TOKEN = "EAAj4GJK1lnIBRjZAtVuNMhKs5FxQFq1VA77uTgOeT2jOtNY8NPSIpO69DfZA6RgcQoIH4ZBz6QZATgXpVVWZBkDAgJwv7APlnQAdpL0JbR8SmgqXCPhq1d9EzTlDqUxGHsTz934ZASwmNMcIZCTOVxaX36ZAZAIOfgpatMnsgBZCe1lAhIhC6FlHa7zOlgNBXXR8uEdlGQAPjgGhHKIxZBWCPbjiqwZCYpMwM7tu9jwv0xZBp6ZAALsf1O1GhRZCi5TM1DisXczrHZCPWST8fBnEjqcpBjTss3MZCAZA4ZD"
PHONE_NUMBER_ID = "1050012661539701"

url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/register"

headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
payload = {"messaging_product": "whatsapp", "pin": "123456"}

response = requests.post(url, headers=headers, json=payload)

print("Status Code:", response.status_code)
print("Response:")
print(response.json())
