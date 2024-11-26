import configparser
import telegram
import requests
import os

from cryptography.fernet import Fernet

config = configparser.ConfigParser()
config_path = os.path.abspath("./resources/config.ini")
config.read(config_path)
serect = config['General']


class Secret:
    def generate_key():
        return Fernet.generate_key()

    def save_key(key , path="resources/secret.key"):
        os.makedirs(os.path.dirname(path), exist_ok=True)  
        with open("secret.key","wb") as key_file:
            key_file.write(key)

    def load_key(filename="resources/secret.key"):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"The secret key file '{filename}' does not exist.")
        return open(filename,"rb").read()

async def sendNotification(message,type):
    if type =="tg":
        await telegram.Bot(token=serect["tgbotid"]).send_message(chat_id=(serect["tggroupid"]), text=message)

    if type =="slack":
        return requests.post(serect["swebhook"], message)
