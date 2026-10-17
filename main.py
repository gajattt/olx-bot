import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1560940211859357696/CmEPHq6Tb5hdI42lUKJV44bH6nqKn2Xo9icu-9Ov3dqRjCTMfm6GR0HqxSScm8laWrYf"

data = {
    "content": "🚨 **TESTOWE POWIADOMIENIE!** Jeśli to widzisz, to Discord działa idealnie."
}

response = requests.post(WEBHOOK_URL, json=data)
print("Status wysłania na Discord:", response.status_code)
