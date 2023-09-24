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
    if os.path.exists('./client.json'):
        try:
            config = json.load(open('./client.json', 'r'))
            prints(f"Configuration successfully loaded")
            return config
        except Exception as e:
            printe(f"Error: {e}")
    else:
        with open('./client.default.json', 'r') as default:
            with open('./client.json', 'w+') as config:
                config.writelines(default.readlines())
                config.close()
            default.close()
        return json.load(open('./client.json', 'r'))

class Client:
    def __init__(self):
        self.config = load_config()
        self.client_socket: socket.socket = None
        self.threads = []

    def connect(self):
        pass
    
    def disconnect(self):
        pass
    
    def cleanup(self):
        pass

def main():
    try:
        client: Client = None
        config = load_config()
        
        while True:    
            command_input = (input('$> ').lower())
            command = command_input
            args = command_input.split(' ')[1:]
            
            if config['commands']['help']['command'] in command:
                if len(args) == 0:
                    for cmd in config['commands']:
                        prints(f"\t{config['commands'][cmd]['command']}\t{config['commands'][cmd]['description']}")
                        #printi(f"\tDescription: {config['commands'][cmd]['command']}")
                        #printi(f"\tUsage:        {config['commands'][cmd]['usage']}")
                    printi(f"Type '.help <command name> to find out more information on the usage'")
                else:
                    try:
                        printi(f"Command: {config['commands'][args[0]]['command']}")
                        printi(f"\tDescription: {config['commands'][args[0]]['command']}")
                        printi(f"\tUsage:        {config['commands'][args[0]]['usage']}")
                    except Exception as e:
                        printe(f"Unknown command {args[0]}, use .help to find out commands and their usages")
            elif command == config['commands']['exit']['command']:
                printe('Exiting...')
                if not client is None:
                    client.cleanup()
                exit(1)
            elif command == config['commands']['threads']['command']:
                if not client is None:
                    if client.threads > 0:
                        printi("Threads:")
                        thread_index = 0
                        for thread_obj in client.threads:
                            thread_index += 1
                            prints(f"\tthread[{thread_index}]({thread_obj['type']})",)
                    else:
                        printe(f"No threads currently running, have you connected to the server?")
                else:
                    printe(f"Client isn't currently connected, connect  it with {config['commands']['connect']['command']}")
            elif command == config['commands']['config']['command']:
                if not config is None:
                    printi(f"Currently loaded configuration")
                    for key, value in dict(config).items():
                        if not key == 'commands':
                            prints(f"\t{key} = {value}")
            else:
                printe(f"Unknown command {command}, use .help to find out commands and their usages")
            
            """elif command == config['commands']['status']['command']:
                if not server is None:
                    printi(f"Server Status:")
                    prints(f"\t running = {server.running}")
                    if server.running:
                        prints(f"\t clients = {len(server.clients)}")
                        prints(f"\t threads = {len(server.threads)}")
                else:
                    printe(f"Server isn't running yet, have you tried starting it yet?")"""
    except KeyboardInterrupt as ke:
        if not client is None:
            client.cleanup()
        printe('Exiting...')
        exit(1)

if __name__ == "__main__":
    main()