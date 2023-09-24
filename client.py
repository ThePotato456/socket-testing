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
    def __init__(self, config=None):
        if config is None:
            printe(f"No configuration specified")
            exit(2)
        self.config = config
        self.running = False
        self.thread: threading.Thread = None
        self.client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = None

    def loop(self):
        if not self.client_socket is None:
            self.running = True
            while True:
                try:
                    message = input(f"{self.server_address[0]}:{self.server_address[1]}$>")
                    message_encoded = message.encode('utf-8')
                    data = self.client_socket.recv(1024).decode()
                    if not data:
                        break
                    prints(f"Recevied: {data}")
                except KeyboardInterrupt:
                    self.disconnect()
                except Exception as e:
                    printe(f"An error has occured: {e}")
                    exit(2)

    def connect(self):
        if not self.client_socket is None:
            self.server_address = (self.config['host'], int(self.config['port']))
            
            #Attempt to connect to the server
            printi(f"Attempting to connect to: {self.config['host']}:{int(self.config['port'])}")
            try:
                self.client_socket.connect((self.config['host'], int(self.config['port'])))
                # Create a new thread to handle the client connection
                self.thread: threading.Thread = threading.Thread(target=self.loop, args=())
                # Start the thread if it exists
                if not self.thread is None: self.thread.start()
            except Exception as e:
                printe(f"An error occured: {e}")
                exit(2)
            
    def disconnect(self):
        if not self.client_socket is None:
            printi((f'Disconnecting from {self.server_address[0]}:{self.server_address[1]}'))
            
            # Close the connection from the server but dont close the program itself
            self.client_socket.close()
            self.client_socket: socket.socket = None
            
            printi(f"Disconnected from {self.server_address[0]}:{self.server_address[1]}")
    
    def cleanup(self):
        try:
            if not self.client_socket is None:
                self.client_socket.close()
                self.client_socket: socket.socket = None
            if not self.thread is None:
                self.thread.join()
                self.thread: threading.Thread = None
        except Exception as e:
            printe(f'An exception has occured during cleanup: {e}')

def main():
    try:
        client: Client = None
        config = load_config()
        
        while True:    
            command_input = (input('$> ').lower())
            command = command_input
            args = command_input.split(' ')[1:]
            
            if command == config['commands']['connect']['command']:
                if client is None:
                    client = Client(config=config)
                    client.connect()
                else:
                    printe(f"Client is already connected to {client.server_address[0]}:{client.server_address[1]}")
                    prints(f"{config['commands']['connect']['usage']}")     
            elif config['commands']['help']['command'] in command:
                if len(args) == 0:
                    for cmd in config['commands']:
                        prints(f"\t{config['commands'][cmd]['command']}\t{config['commands'][cmd]['description']}")
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
                    if not client.thread is None:
                        printi("Thread:")
                        prints(f"\nrunning = {client.running})",)
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