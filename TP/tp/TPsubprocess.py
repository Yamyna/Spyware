import subprocess
import ipaddress
import signal
from TPipconfig import TPipconfig

class TPsubprocess:
    """
    Classe pour le TP2 : subprocess.

    """
    def __init__(self):
        """
        Initialisation des variables addresses_en_lignes et tp_ipconfig
        """
        self.addresses_en_ligne = []
        self.tp_ipconfig = TPipconfig()

    def ping_adresse_ip(self, adresse_info):
        """
        Ping la plage d'adresse ip de la carte réseau.

        Retourne :
            Aucune valeur de retour.
        """
        try:
            if "ipv4" in adresse_info and "masque" in adresse_info:
                adresse_ip = adresse_info["ipv4"]
                masque = adresse_info["masque"]
            elif "inet" in adresse_info:
                pass
            else:
                print("Informations manquantes pour le ping.")
                return

            reseau = ipaddress.IPv4Network(f"{adresse_ip}/{masque}", strict=False)
            print(f"Pinging la plage d'adresse IP {reseau}...\n")

            for ip in reseau.hosts():
                ip = str(ip)
                result_ping = subprocess.run(["ping", "-n", "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if result_ping.returncode == 0:
                    print(f"Adresse IP {ip} : Réponse reçue!")
                    self.addresses_en_ligne.append(ip)
                else:
                    print(f"Adresse IP {ip} : Pas de réponse.")
        except Exception as e:
            print(f"Erreur lors du ping : {e}")

    def addresses_en_ligne_fichier(self):
        """
        Ecrit les adresses en lignes dans un fichier texte.

        Retourne :
            Aucune valeur de retour.
        """
        with open("addresses_en_ligne.txt", "w") as file:
            for ip in self.addresses_en_ligne:
                file.write(ip + "\n")
        print("Adresse en ligne dans le fichier:  'addresses_en_ligne.txt'.")

    def infos_ipconfig(self):
        """
        Appel la fonction de la classe TPipconfig pour l'utiliser par la suite dans cette classe

        Retourne :
            La fonction infos_ipconfig() de la classe TPipconfig
        """
        return self.tp_ipconfig.infos_ipconfig()

    def menu_ping(self):
        """
        Menu pour que l'utilisateur saisisse sa carte réseau qu'il veut pinger.

        Retourne:
            Aucune valeur de retour.
        """
        adresses_info = self.infos_ipconfig()
        print(adresses_info)

        if not adresses_info:
            print("Aucune adresse IP trouvée.")

        print("\nMenu des cartes réseau:")
        for i, info in enumerate(adresses_info, 1):
            print(f"{i}. Carte réseau : {info.get('carte', 'Inconnu')}, IP : {info.get('ipv4', 'Inconnue')}, Masque : {info.get('masque', 'Inconnu')}")

        choix = input("\nChoisissez le numéro de la carte réseau à pinger : ")

        try:
            choix = int(choix)
            if 1 <= choix <= len(adresses_info):
                adresse_info_choisie = adresses_info[choix - 1]

                signal.signal(signal.SIGINT, self.stop_ctrl_c)
                self.ping_adresse_ip(adresse_info_choisie)

                self.addresses_en_ligne_fichier()
            else:
                print("Choix invalide.")
        except ValueError:
            print("Veuillez entrer un numéro valide.")

    def stop_ctrl_c(self, signum, frame):
        """
        Fonction qui arrête le programme avec ctrl c
        """
        print("\nPing interrompu par l'utilisateur.")
        self.addresses_en_ligne_fichier()
        exit()

if __name__ == "__main__":
    tpsubprocess = TPsubprocess()
    tpsubprocess.menu_ping()