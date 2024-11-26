# import sys
# import os

# from functions.config import systemconfig

# lines = [
#     '[Unit]\n', 'Description=AWS Sentinel service\n','After=multi-user.target\n\n',
#     '[Service]\n', 'Type=simple','Restart=always\n',f'ExecStart={sys.executable} /AWSSentinel/main.py --listen\n\n',
#     '[Install]\n', 'WantedBy=multi-user.target'
#     ]

# def listen():
#     if os.path.exists("aws-sentinel.service") == False:
#         systemconfig(lines)
