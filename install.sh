#!/usr/bin/bash 
sudo apt remove wkhtmltopdf
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb
sudo dpkg -i wkhtmltox_0.12.6.1-2.jammy_amd64.deb
rm wkhtmltox_0.12.6.1-2.jammy_amd64.deb
sudo apt-get install python3-pyqt5 python3-pdfkit
sudo mkdir -p /opt/cuisine
sudo cp logo.svg script.py icon.png /opt/cuisine/

sudo echo """[Desktop Entry]
Encoding=UTF-8
Version=1.0
Type=Application
Terminal=false
Exec=/opt/cuisine/script.py
Name=cuisineLXP
Icon=/opt/cuisine/icon.png""" | sudo tee /usr/share/applications/cuisineLXP.desktop
