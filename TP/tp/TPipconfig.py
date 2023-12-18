import glob
import os
import pathlib
import platform
import subprocess

class TPipconfig:
    """
    Classe du TP1.

    """

    def infos_interface_reseau(self):
        """
        Affiche le système d'exploitation et mets les infos d'ip dans un fichier texte.

        Retourne:
            Aucune valeur de retour.
        
        """
        if "Windows" in platform.uname():
            print("\nNous sommes dans le système d'exploitation Windows.\n")
            ipconfig = subprocess.run("ipconfig", capture_output=True, text=True)
            with open("ipconfig.txt", "w") as fichier:
                fichier.write(ipconfig.stdout)
            with open("ipconfig.txt", "r") as fichier:
                print(fichier.read())

        if "Linux" in platform.uname():
            print("\nNous sommes dans le système d'exploitation Linux.\n")
            ip_a = subprocess.run("ip a", capture_output=True, text=True)
            with open("ipa.txt", "w") as fichier:
                fichier.write(ip_a.stdout)
            with open("ipa.txt", "r") as fichier:
                print(fichier.read())

    def repertoire(self):
        """
        Affiche le contenu du Repertoire crée.

        Retourne :
            Aucune valeur de retour.
        """
        cheminRepertoire = str(pathlib.Path().absolute())
        repertoire = os.path.join(cheminRepertoire, "Repertoire")
        os.makedirs(repertoire, exist_ok=True)

        chemin = os.path.join(repertoire, "**", "*.*")
        print("\nLes fichiers du répertoire créé sont : \n")
        for fichierRepertoire in glob.glob(chemin, recursive=True):
            print(fichierRepertoire)

    def infos_ipconfig(self):
        """
        Fonction qui récupère les informations nécessaires du fichier ipconfig :
        Carte réseau + IP + Masque de sous-réseau.

        Retourne : 
            adresses_info : masque + ip + carte réseau
        """
        adresses_info = []

        print("\nRécupération des IP \n")
        if "Windows" in platform.system():
            with open("ipconfig.txt", "r") as fichier:
                carte = None
                ipv4_ligne = None
                masque_ligne = None
                for ligne in fichier:
                    if "Carte Ethernet" in ligne:
                        carte = ligne.strip()
                    if "IPv4" in ligne:
                        ipv4_num = ligne.strip().split()
                        ipv4_ligne = ipv4_num[-1]
                    if "Masque" in ligne:
                        masque_num = ligne.strip().split()
                        masque_ligne = masque_num[-1]
                        adresses_info.append({
                            "carte": carte,
                            "ipv4": ipv4_ligne,
                            "masque": masque_ligne
                        })

        if "Linux" in platform.system():
            with open("ipa.txt", "r") as fichier:
                for ligne in fichier:
                    if "inet" in ligne:
                        inet_ligne = ligne.strip()
                        adresses_info.append({
                            "inet": inet_ligne
                        })

        return adresses_info

    def menu(self):
        """
        Affiche le menu pour que l'utilisateur choisisse son option

        Retourne : 
            Aucune valeur de retour.
        """
        while True:
            print("\nMenu :")
            print("1. Infos Interface Réseau")
            print("2. Répertoire")
            print("3. Infos IP Config")
            print("4. Quitter")

            choix = input("Choisissez une option : ")

            if choix == "1":
                self.infos_interface_reseau()
            elif choix == "2":
                self.repertoire()
            elif choix == "3":
                self.infos_ipconfig()
            elif choix == "4":
                break
            else:
                print("Option invalide. Veuillez choisir une option valide.")

if __name__ == "__main__":
    tpipconfig = TPipconfig()
    tpipconfig.menu()
