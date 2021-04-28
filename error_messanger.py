import requests
import os


def send_message(channel_id, text):
    token = os.getenv('TELEGRAMM_TOKEN')
    method = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(method, data={
        "chat_id": channel_id,
        "text": text})
    if response.status_code != 200:
        raise Exception("Send Message Error")
