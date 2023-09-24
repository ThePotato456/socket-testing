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
    if os.path.exists('./config.json'):
        try:
            config = json.load(open('./config.json', 'r'))
            prints(f"Configuration successfully loaded")
            return config
        except Exception as e:
            printe(f"Error: {e}")
    else:
        with open('./config.default.json', 'r') as default:
            with open('./config.json', 'w+') as config:
                config.writelines(default.readlines())
                config.close()
            default.close()
        return json.load(open('./config.json', 'r'))

class Server():
    def __init__(self):
        self.running = False
        self.config = load_config()
        self.threads = []
        self.clients = []
        
        try:
            # Create TCP socket
            self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Set a reusable socket option to allow binding to the same address
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Define server address and port
            self.server_address = (self.config['host'], int(self.config['port']))
        except Exception as e:
            printe(f'An error occured {e}')
            exit(1)

    def start(self):
        # Attempt to bind the socket to the server address and port
        self.server_socket.bind(self.server_address)
        printi('Server bound to address: ', self.server_socket.getsockname())
        
        # Start the loop function as a thread
        self.server_thread = threading.Thread(target=self.loop)
        # Add server thread to the list of thread for cleanup
        self.threads.append({'type': 'server_thread', 'thread': self.server_thread})
        self.running = True
    
    def cleanup(self):
        if self.running:
            if len(self.clients) > 0:
                for client in self.clients:
                    client_socket: socket.socket = client['client_socket']
                    try:
                        printi(f"Closing socket({client['client_address']})")
                        client_socket.close()
                        prints(f"\tclient_socket({client['client_address']} successfully closed!)")
                    except Exception as e:
                        printe(f'An error occured {e}')
                        return
                    self.clients.remove(client)
            if len(self.clients) > 0:
                for thread_obj in self.threads:
                    thread: threading.Thread = thread_obj['thread']
                    try:
                        printi(f"Closing thread({thread_obj['type']}{len(self.threads)})")
                        thread.join()
                        prints(f"\tThread successfully closed!")
                        self.threads.remove(thread)
                        thread_count -= 1
                        return True
                    except Exception as e:
                        printe(f"Thread Error({len(int(thread_obj['type']))}{len(self.threads)})): {e}")
        else:
            if not self.running:
                printe(f"Server not not running yet, nothing to cleanup")  

            return False
                  
    def loop(self):
        # Main server loop
        while True:
            # Accept a new client connection
            client_socket, client_address = self.server_socket.accept()
            
            # Create a Client data structure
            client = {
                'client_socket': client_socket,
                'client_address': client_address,
                'client_data': {
                    'messages': []
                }   
            }
            self.clients.append(client)
            
            # Create a new thread to handle the client connection
            client_thread: threading.Thread = threading.Thread(target=self.handle_client, args=(client))
            client['client_thread'] = client_thread
            self.threads.append({'type': 'client_thread', 'thread': client_thread})
            client_thread.start()


    # Function to handle each client connection
    def handle_client(self, client):
        printi(f'Connected client: {json.dumps(client)}')

        # Client variables        
        client_socket: socket.socket = client['client_socket']
        client_thread: threading.Thread = client['client_thread']
        client_address = client['client_address']
        client_data = client['client_data']
        client_messages = list(client_data['messages'])

        while True:
            # Receive client message
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            client_messages.append(message)
            prints(f'Received from {client_address}: {message}')

            # Broadcast message to all connected clients                
            for client in self.clients:
                broadcast_client: socket.socket = client['client_socket']
                broadcast_client.send(message.encode('utf-8'))

        # Remove the client from the list when they disconnect
        self.clients.remove(client)
        client_socket.close()
        printe(f'Client disconnected: {client_address}')
        
        # Cleanup client handler thread
        self.threads.remove(client_thread)
        printi(f"Closing thread for {client_address}")
        client_thread.join()

def main():
    try:
        server: Server = None
        config = load_config()
        
        while True:    
            command_input = (input('$> ').lower())
            command = command_input
            args = command_input.split(' ')[1:]
            
            if command == config['commands']['start']['command']:
                if server is None:
                    server = Server()
                    server.start()
                else:
                    printe(f"Server already running...")
                    prints(f"{config['commands']['start']['usage']}")
            elif command == config['commands']['stop']['command']:
                if not server is None:
                    if server.running:
                        printi(f"Closing server socket")
                        try:
                            server.server_socket.close()
                        except Exception as e:
                            printe(f"Unable to close server_socket: {e}")
                    else:
                        printe(f"Server isn't currently running, start it with {config['commands']['start']['command']}")
                else:
                        printe(f"Server isn't currently running, start it with {config['commands']['start']['command']}")
            elif command == config['commands']['threads']['command']:
                if not server is None:
                    if server.threads > 0:
                        printi("Threads:")
                        thread_index = 0
                        for thread_obj in server.threads:
                            thread_index += 1
                            prints(f"\tthread[{thread_index}]({thread_obj['type']})",)
                    else:
                        printe(f"No threads currently running, have you started the server?")
                else:
                    printe(f"Server isn't currently running, start it with {config['commands']['start']['command']}")
            elif command == config['commands']['clients']['command']:
                if not server is None:
                    printi("Clients:")
                    prints(f"\t{json.dumps(server.clients, indent=2)}")
                else:
                    printe(f"Server isn't started, so no clients to show")
                    prints(f"{config['commands']['clients']['usage']}")
            elif command == config['commands']['status']['command']:
                if not server is None:
                    printi(f"Server Status:")
                    prints(f"\t running = {server.running}")
                    if server.running:
                        prints(f"\t clients = {len(server.clients)}")
                        prints(f"\t threads = {len(server.threads)}")
                else:
                    printe(f"Server isn't running yet, have you tried starting it yet?")
            elif config['commands']['help']['command'] in command:
                if len(args) == 0:
                    for cmd in config['commands']:
                        prints(f"\t{config['commands'][cmd]['command']}")
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
                if not server is None:
                    server.cleanup()
                exit(1)
            else:
                printe(f"Unknown command {command}, use .help to find out commands and their usages")
    except KeyboardInterrupt as ke:
        if not server is None:
            server.cleanup()
        printe('Exiting...')
        exit(1)

if __name__ == "__main__":
    main()