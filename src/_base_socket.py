import socket
import threading
import json
import logging
import os 
import yaml
from time import sleep
from _orders import NoOrder


class Node:
    def __init__(self):
        pass

    def _separate_jsons(self,input_string):
        result = []
        current_str = ""
        open_braces = 0

        for char in input_string:
            if char == "{":
                open_braces += 1
                current_str += char
            elif char == "}":
                open_braces -= 1
                current_str += char

                if open_braces == 0:
                    result.append(current_str)
                    current_str = ""
            else:
                current_str += char

        return result

class Server(Node):
    def __init__(self, host='127.0.0.1', port=5001):
        # Set self.logger name to server
        self.logger = logging.getLogger('SimTest')
        self.host = host
        self.available_ports = range(50505, 50521, 3)
        self.port_index = 0

        try:
            # read config.yaml
            with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')) as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                self.port = config['port']
        except yaml.YAMLError as exc:
            self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.server_socket.bind((self.host, self.port))
                break
            except OSError:
                self.port = self.available_ports[self.port_index]
                self.port_index += 1
                if self.port_index == len(self.available_ports):
                    self.port_index = 0
                self.logger.info(f"Port is already in use. Using another port: {self.port}")
        self.client_socket = None
        self.is_running = False


    def start(self):
        self.server_socket.listen(1)
        self.logger.info("Server is listening on {}:{}".format(self.host, self.port))
        self.client_socket, address = self.server_socket.accept()
        self.logger.info(f"Connected to client: {address}")
        self.is_running = True

        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()


    def receive(self):
        while self.is_running:
            try:
                data = self.client_socket.recv(1024*1024).decode()
                if data:
                    try:
                        #print(deserialized_data)
                        deserialized_data = json.loads(data)
                    except json.decoder.JSONDecodeError:
                        json_list = self._separate_jsons(data)
                        for json_str in json_list:
                            try:
                                deserialized_data = json.loads(json_str)
                                self.on_receive(deserialized_data)
                            except json.decoder.JSONDecodeError:
                                self.logger.info(f"Could not deserialize data: {json_str}")
                        continue
                    self.on_receive(deserialized_data)
            except ConnectionResetError:
                self.logger.info("Client has disconnected.")
                self.stop()

    def send(self, message : json):
        serialized_message = json.dumps(message)
        self.client_socket.sendall(serialized_message.encode())

    def stop(self):
        self.is_running = False
        self.server_socket.close()
        self.client_socket.close()

    def disconnect(self):
        self.receive_thread.join()

    def on_receive(self, data : json):
        # Override this method in your subclass
        # Raise not implemented error if you don't
        raise NotImplementedError("You must override the on_receive method in your subclass.")

class Client(Node):
    def __init__(self, host='127.0.0.1', port=5001):
        # Set self.logger name to strategy
        self.logger = logging.getLogger('Strategy')
        self.host = host
        self.available_ports = range(50505, 50521, 3)
        self.port_index = 0
        try:
            # read config.yaml
            with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')) as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                self.port = config['port']
        except yaml.YAMLError as exc:
            self.port = port
        self.flipper = -1
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_running = False
        self.is_sent = False

    def connect(self):
        while True:
            try:
                self.client_socket.connect((self.host, self.port))
                self.logger.info("Connected to server on {}:{}".format(self.host, self.port))
                break
            except ConnectionRefusedError:
                self.port = self.available_ports[self.port_index]
                self.port_index += 1
                if self.port_index == len(self.available_ports):
                    self.port_index = 0
                # cancel previous attempt
                self.client_socket.close()
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.logger.info(f"\nServer is not available. Retrying(port={self.port})...")
                sleep(2)
            except OSError:
                self.logger.info("\nServer is not available. Retrying...")
                sleep(2)
        self.is_running = True

        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()
        self.on_connect()
        self.is_sent = False

    def receive(self):
        while self.is_running:
            try:
                decoded_data = self.client_socket.recv(1024).decode()
                if decoded_data:
                    try:
                        deserialized_data = json.loads(decoded_data)
                    except json.decoder.JSONDecodeError:
                        json_list = self._separate_jsons(decoded_data)
                        for json_str in json_list:
                            try:
                                deserialized_data = json.loads(json_str)
                                self.on_receive(deserialized_data)
                                if self.is_sent:
                                    self.is_sent = False
                                else:
                                    self.send(NoOrder(deserialized_data['time']).to_dict())
                                    self.is_sent = False
                            except json.decoder.JSONDecodeError:
                                self.logger.info("Could not deserialize data: ", json_str)
                        continue
                    try:
                        if deserialized_data['message'] == 'END':
                            self.stop()
                            return
                        print("[{}]/[{}]".format(deserialized_data['tick'],deserialized_data['size']), end="\r")
                    except KeyError:
                        pass
                    self.on_receive(deserialized_data)
                    if self.is_sent:
                        self.is_sent = False
                    else:
                        self.send(NoOrder(deserialized_data['time']).to_dict())
                        self.is_sent = False
            except ConnectionResetError:
                self.logger.info("Server has disconnected.")
                self.stop()

    def send(self, message):
        self.is_sent = True
        try:
            if message['data'] == []:
                self.is_sent = False
                return
        except KeyError:
            pass 
        serialized_message = json.dumps(message)
        self.client_socket.sendall(serialized_message.encode())

    def stop(self):
        self.is_running = False
        self.client_socket.close()

    def disconnect(self):
        self.receive_thread.join()
        self.on_disconnect()

    def on_disconnect(self):
        # Override this method in your subclass
        # Raise not implemented error if you don't
        raise NotImplementedError("You must override the on_disconnect method in your subclass.")

    def on_receive(self, data : json):
        # Override this method in your subclass
        # Raise not implemented error if you don't
        raise NotImplementedError("You must override the on_receive method in your subclass.")

    def on_connect(self):
        # Override this method in your subclass
        # Raise not implemented error if you don't
        raise NotImplementedError("You must override the on_connect method in your subclass.")