import socket
from cryptography.fernet import Fernet

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

        with open("received_file.txt", "wb") as file:
            file.write(decrypted_text)

        print("File received, decrypted, and saved successfully.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    server_port = 12345
    receive_and_decrypt_file(server_port)
