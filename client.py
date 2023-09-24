#!./.venv/bin/python3

import socket
import threading
import os
import json

from colorama import Fore, Style
printi = lambda *a, **kw: print(f' {Style.BRIGHT}[{Fore.CYAN}i{Fore.RESET}]{Style.RESET_ALL}', *a, **kw)
printe = lambda *a, **kw: print(f' {Style.BRIGHT}[{Fore.LIGHTRED_EX}-{Fore.RESET}]', *a, **kw)
prints = lambda *a, **kw: print(f' {Style.BRIGHT}[{Fore.LIGHTGREEN_EX}+{Fore.RESET}]', *a, **kw)

def load_config():
    if not os.path.exists('./config'): os.mkdir('./config')

    if os.path.exists('./config/client.json'):
        try:
            config = json.load(open('./config/client.json', 'r'))
            prints(f"Configuration successfully loaded")
            return config
        except Exception as e:
            printe(f"Error: {e}")
    else:
        with open('./config/client.default.json', 'r') as default:
            with open('./config/client.json', 'w+') as config:
                json.dump(config, json.load(default), indent=2)
                config.close()
            default.close()
        return json.load(open('./config/client.json', 'r'))