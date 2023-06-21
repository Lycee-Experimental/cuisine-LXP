#!/usr/bin/bash 
# Installation de la version précédente de wkhtmltopdf
sudo apt remove wkhtmltopdf
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb
sudo dpkg -i wkhtmltox_0.12.6.1-2.jammy_amd64.deb
rm wkhtmltox_0.12.6.1-2.jammy_amd64.deb

# Installation des dépendances
sudo apt-get install python3-pyqt5 python3-pdfkit

# Téléchargement de l'application et des ressources
sudo mkdir -p /opt/cuisine
sudo wget https://raw.githubusercontent.com/Lycee-Experimental/cuisine-LXP/main/logo.svg -O /opt/cuisine/logo.svg
sudo wget https://raw.githubusercontent.com/Lycee-Experimental/cuisine-LXP/main/icon.png -O /opt/cuisine/icon.png
sudo chmod 644 /opt/cuisine/icon.png
sudo wget https://raw.githubusercontent.com/Lycee-Experimental/cuisine-LXP/main/script.py -O /opt/cuisine/script.py
sudo chmod +x /opt/cuisine/script.py

# Génération d'un élément de menu
sudo echo """[Desktop Entry]
Encoding=UTF-8
Version=1.0
Type=Application
Terminal=false
Exec=/opt/cuisine/script.py
Name=cuisineLXP
Icon=/opt/cuisine/icon.png""" | sudo tee /usr/share/applications/cuisineLXP.desktop
