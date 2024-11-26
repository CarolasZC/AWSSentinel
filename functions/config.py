import configparser
import os

from cryptography.fernet import Fernet
from functions.function import Secret 

config = configparser.ConfigParser()
config_path = os.path.abspath("./resources/config.ini")
config.read(config_path)
general = config['General']

def configureNotif(bot:str,group:str,webhook:str):
    if os.path.exists("secret.key") == False:
        key = Secret.generate_key()
        Secret.save_key(key)
    
    serect_key = Secret.load_key()
    cipher = Fernet(serect_key)
    if bot!=None or "":
        general["tgbotid"] = cipher.encrypt(bot.encode()).decode()
    if group!=None or "":    
        general["tggroupid"] = cipher.encrypt(group.encode()).decode()
    if webhook!=None or "":
        general["swebhook"] = cipher.encrypt(webhook.encode()).decode()

    with open('./resources/config.ini', 'w') as configfile:
        config.write(configfile)

# def systemconfig(lines):
#     with open("/etc/systemd/system/aws-sentinel.service","w") as sys_file:
#         sys_file.writelines(lines)
#         sys_file.close()