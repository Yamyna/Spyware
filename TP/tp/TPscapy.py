import ipaddress
import signal
import sys
from scapy.all import IP, ICMP, TCP, sr1, wrpcap, rdpcap, UDP
from TPipconfig import TPipconfig

class TPscapy:
    """
    Classe pour TP4 : scapy
    """
    def __init__(self):
        """
        Initialisation des variables addresses_en_lignes, tp_ipconfig et pcap_fichier
        """
        self.addresses_en_lignes = []
        self.tp_ipconfig = TPipconfig()
        self.pcap_fichier = "capture.pcap"  

    def check_open_ports(self, ip):
        """
        Vérifie si les ports sont ouverts parmis une liste de ports prédéfinies et envoie un packet tcp.

        Retourne :
            Le port ouvert.
        """
        ports_ouverts = []
        ports_liste = [80, 443, 22, 21, 69, 67, 25, 53, 110, 143, 587, 3306, 8080, 137, 138, 139]

        for port in ports_liste:
            reponse = self.envoie_paquet_tcp(ip, port)
            if reponse is not None and reponse.haslayer(TCP) and reponse[TCP].flags == 18:
                ports_ouverts.append(port)

        return ports_ouverts

    def envoie_paquet_icmp(self, ip, adresse_info):
        """
        Envoie unn packet icmp en fonction de la carte réseau.

        Retourne :
            Aucune valeur : None.
        """
        try:
            reponse = sr1(IP(dst=ip) / ICMP(), timeout=1, verbose=False, iface=str(adresse_info["carte"]).rstrip(":"))
            return reponse
        except Exception as e:
            return None

    def envoie_paquet_tcp(self, ip, port):
        """
        Envoie paquet tcp.
        """
        try:
            reponse = sr1(IP(dst=ip) / TCP(dport=port, flags="S"), timeout=1, verbose=False)
            return reponse
        except Exception as e:
            return None

    def ping_adresse_ip(self, adresse_info):
        """
        Ping la plage d'adresse ip de la carte réseau et affiche les ports ouverts si le ping est réussi. Affiche l'ip source et destination.

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
            print(f"Ping de la plage d'adresse IP {reseau}...\n")

            for ip in reseau.hosts():
                ip = str(ip)
                response = self.envoie_paquet_icmp(ip, adresse_info)
                if response is not None and response.haslayer(ICMP) and response[ICMP].type == 0:
                    print(f"Adresse IP {ip} : Réponse reçue !")

                    src_ip = response[IP].src
                    dst_ip = response[IP].dst

                    print(f"IP source : {src_ip}, IP destination : {dst_ip}")

                    if TCP in response:
                        dst_port = response[TCP].dport
                        print(f"Port destination : {dst_port}")
                    elif UDP in response:
                        dst_port = response[UDP].dport
                        print(f"Port destination : {dst_port}")

                    self.addresses_en_lignes.append(ip)
                    open_ports = self.check_open_ports(ip)
                    if open_ports:
                        print(f"Ports ouverts pour l'adresse IP {ip}: {', '.join(map(str, open_ports))}")
                    else:
                        print(f"Aucun port ouvert pour l'adresse IP {ip}.")
                else:
                    print(f"Adresse IP {ip} : Pas de réponse.")

        except Exception as e:
            print(f"Erreur lors du ping : {e}")

    def addresses_en_ligne_fichier(self):
        """
        Ecrit les adresses en lignes et leur numéro de port dans un fichier texte. Et crée un fichier pcap.

        Retourne :
            Aucune valeur de retour.
        """
        with open("addresses_en_ligne.txt", "w") as file:  # Assurez-vous que le nom de fichier correspond à celui que vous utilisez
            for ip in self.addresses_en_lignes:
                file.write(ip + "\n")
                open_ports = self.check_open_ports(ip)
                if open_ports:
                    file.write(f"Ports ouverts : {', '.join(map(str, open_ports))}\n")
                else:
                    file.write("Aucun port ouvert.\n")
        print("Adresses en ligne écrites dans 'addresses_en_ligne.txt'.")
        self.cree_pcap_fichier()

    def cree_pcap_fichier(self):
        """
        Creer un fichier pcap avec l'ip source/destination.

        Retourne :
            Aucune valeur de retour.
        """
        if not self.addresses_en_lignes:
            return

        source_ip = self.addresses_en_lignes[0]
        paquets = [IP(src=source_ip, dst=ip) / ICMP() for ip in self.addresses_en_lignes]
        wrpcap(self.pcap_fichier, paquets)
        print(f"Fichier pcap '{self.pcap_fichier}' créé avec succès.")

    def parse_pcap_fichier(self):
        """
        Parse le fichier pcap pour afficher son contenue.

        Retourne :
            Aucune valeur de retour.
        """
        try:
            capture_paquets = rdpcap(self.pcap_fichier)
            for paquet in capture_paquets:
                if IP in paquet:
                    src_ip = paquet[IP].src
                    dst_ip = paquet[IP].dst
                    if TCP in paquet:
                        dst_port = paquet[TCP].dport
                        print("Contenue du fichier pcap :")
                        print(f"IP source : {src_ip}, IP destination : {dst_ip}, Port destination : {dst_port}")
                    elif UDP in paquet:
                        dst_port = paquet[UDP].dport
                        print("Contenue du fichier pcap :")
                        print(f"IP source : {src_ip}, IP destination : {dst_ip}, Port destination : {dst_port}")
                    else:
                        print("Contenue du fichier pcap :")
                        print(f"IP source : {src_ip}, IP destination : {dst_ip}")
        except FileNotFoundError:
            print(f"Fichier '{self.pcap_fichier}' non trouvé.")

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
            return

        print("\nMenu des cartes réseau :")
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
                self.parse_pcap_fichier()
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
        sys.exit()

if __name__ == "__main__":
    tpscapy = TPscapy()
    signal.signal(signal.SIGINT, tpscapy.stop_ctrl_c)
    tpscapy.menu_ping()