#!/usr/bin/python
import sys, os
os.environ['QT_QPA_PLATFORMTHEME'] = 'gtk2'
os.environ['QT_STYLE_OVERRIDE'] = 'gtk2'
#os.environ['QT_QPA_PLATFORM_PLUGIN_PATH']='/usr/lib/x86_64-linux-gnu/qt5/plugins'
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QLabel, QLineEdit, QPushButton, QVBoxLayout, QDateEdit, QDesktopWidget, QFrame
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QIcon

import pdfkit
import subprocess
import sqlite3



class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Compta de la cuisine du LXP')
        self.resize(400, 200)
        # Set the application icon
        current_dir = os.path.dirname(os.path.abspath(__file__)) 
        self.setWindowIcon(QIcon(os.path.abspath(os.path.join(current_dir, "icon.png"))))
        # Get the size of the screen
        screen = QDesktopWidget().screenGeometry()
        # Calculate the center point of the screen
        center_point = screen.center()
        # Get the size of the window
        window_size = self.geometry()
        # Calculate the center point of the window
        center_point.setX(int(center_point.x() - window_size.width() / 2))
        center_point.setY(int(center_point.y() - window_size.height() / 2))
        # Set the window position to the center of the screen
        self.move(center_point)
        # Création du widget QDateEdit
        self.label_date = QLabel('Choisir une date :', self)
        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True) # This enables the calendar widget
        self.date_edit.setDate(QDate.currentDate())
        self.label_value = QLabel('Montant des courses du jour :', self)
        self.input_value = QLineEdit(self)
        self.button_calculate = QPushButton('Compta de la journée', self)
        self.button_calculate.clicked.connect(self.calculate)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.button_calculate_semaine = QPushButton('Compta de la semaine', self)
        self.button_calculate_semaine.clicked.connect(self.calculate_semaine)        
        # Set up the layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.label_date)
        vbox.addWidget(self.date_edit)
        vbox.addWidget(self.label_value)
        vbox.addWidget(self.input_value)
        vbox.addWidget(self.button_calculate)
        vbox.addWidget(separator)
        vbox.addWidget(self.button_calculate_semaine)
        self.setLayout(vbox)


    def generate_pdf(self, date_str, x, y, result, value):
        if getattr(sys, 'frozen', False):
            # Si l'application est un exécutable PyInstaller, utilisez sys._MEIPASS pour accéder aux fichiers extraits
            current_dir = sys._MEIPASS
        else:
            # Si l'application est en cours d'exécution depuis le script Python, utilisez le chemin absolu du fichier
            current_dir = os.path.dirname(os.path.abspath(__file__)) 
        abs_path = os.path.abspath(os.path.join(current_dir, "logo.svg"))
        html = """
        <html>
        <head>
            <title>Repas</title>
            <style>
                body {{
                    background-color: white;
                }}
                table {{
                  margin-left: auto;
                  margin-right: auto;
  border-collapse: collapse;
                }}
                h1, h2 {{
                    text-align: center;
                }}
td {{
  border: 1px solid black;
  padding: 8px;
}}
                td:first-child {{
                  text-align: right;
                  font-weight: bold;
                  width: 200px;
                }}
td:nth-child(2) {{
  text-align: center; /* centrer le contenu de la deuxième colonne */
  padding: 0 30px; /* ajouter de la marge à gauche et à droite des cellules */
}}
.logo {{
  position: absolute;
  top: 50px;
  right: 0;
  z-index: 9999;
  width: 200px;
  height: 200px;

}}
.empty-rectangle::before {{
  content: "Bande de compte";
  text-align: center;
  display: block;
  position: absolute;
  top: 50px;
  left: 0;
  width: 200px;
  height: 200px;
  border: 1px solid black;
}}


            </style>
        </head>
        <body>
        <div class="empty-rectangle"></div>
<img class="logo" src="{}" alt="Logo">
            <h1>Pièces justificatives des dépenses</h1>
            <h2>Repas du {}</h2>

 <table>
  <tr>
    <td>Repas complets (2,50€)</td>
    <td>{}</td>
  </tr>
  <tr>
    <td>Plats simples (1,60€)</td>
    <td>{}</td>
  </tr>
  <tr>
    <td>Recettes</td>
    <td>{:.2f} €</td>
  </tr>
  <tr>
    <td>Dépenses</td>
    <td>{:.2f} €</td>
  </tr>
</table> 

        </body>
        </html>
        """.format(abs_path, datetime.strptime(date_str, '%Y-%m-%d').strftime("%A %d %B %Y"),x, y, result, value)
        options={   'encoding': 'UTF-8', 
                    "enable-local-file-access": "",
                    'margin-top': '1cm',
                    'margin-right': '1cm',
                    'margin-bottom': '1cm',
                    'margin-left': '1cm'
                }
        # Convertit le fichier HTML en PDF
        pdfkit.from_string(html, "/tmp/resultat.pdf", options=options)
        # Ouvre le fichier PDF avec l'éditeur par défaut
        subprocess.run(['xdg-open', '/tmp/resultat.pdf'])

    def calculate(self):
        db_path=os.path.expanduser("~/.cuisine")
        if not os.path.exists(db_path+'/base.db'):
            diff=0
        else:
            conn = sqlite3.connect(db_path+'/base.db')
            cursor = conn.cursor()
            cursor.execute('SELECT float2 FROM my_table ORDER BY date DESC LIMIT 1')
            # Fetch the result
            diff = cursor.fetchone()[0]
        value = float(self.input_value.text().replace(",", "."))
        value_rect=value-diff
        date_str=self.date_edit.date().toString("yyyy-MM-dd")
        a = 2.5
        b = 1.60

        # Initialisation des valeurs de x et y
        x = max(0, round(0.8 * value_rect / a))
        y = max(0, round((value_rect - a * x) / b))

        # Boucle pour minimiser la différence entre result et value
        while True:
            result = a * x + b * y
            diff = result-value_rect
            diff = round(diff, 2)
            if abs(diff) < 1:  # Si la différence est suffisamment petite et y est dans la plage souhaitée, on sort de la boucle
                break
            # Modification de x et y pour réduire la différence
            dx = diff / a
            dy = diff / b
            x += round(dx)
            y += round(dy)
            # Vérification que y est entre 15% et 30% de x
            if y < 0.15 * x:
                y = round(0.15 * x)
            elif y > 0.3 * x:
                y = round(0.3 * x)
        if self.register(date_str, x, y, value, diff):
            self.generate_pdf(date_str, x, y, result, value)

    def register(self,date_str, x, y, value, diff):
        db_path=os.path.expanduser("~/.cuisine")
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        conn = sqlite3.connect(db_path+'/base.db')
        cursor = conn.cursor()
        # Create a table to store the list
        cursor.execute('''CREATE TABLE IF NOT EXISTS my_table (date TEXT PRIMARY KEY, integer1 INTEGER, integer2 INTEGER, float1 REAL, float2 REAL)''')
        # Check if the row with the given date already exists
        cursor.execute('''SELECT date FROM my_table WHERE date = ?''', (date_str,))
        existing_date = cursor.fetchone()

        if existing_date is not None:
            # If the row already exists, ask for confirmation to overwrite it
            confirm = QMessageBox.question(None, 'Confirmation', 'Cette date existe déjà dans la base, voulez-vous la remplacer ?',
                                            QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
            if confirm == QMessageBox.Cancel:
                # If Cancel is clicked, do not overwrite the row and exit the program
                conn.close()
                return False
            else:
                        cursor.execute('''UPDATE my_table SET integer1=?, integer2=?, float1=?, float2=? WHERE date=?''', (x, y, value, diff, date_str))
        else:
            # Insert the list into the table
            cursor.execute('''INSERT INTO my_table (date, integer1, integer2, float1, float2) VALUES (?, ?, ?, ?, ?)''', (date_str, x, y, value, diff))
        # Commit the changes
        conn.commit()
        # Close the connection
        conn.close()
        return True
    
  
    def calculate_semaine(self):
        db_path=os.path.expanduser("~/.cuisine/base.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        date = QDateTime(self.date_edit.date())
        date = date.toPyDateTime().date()
        start_date = date - timedelta(days=date.weekday())
        end_date = start_date + timedelta(days=4)
        dates = []
        for x in range(5):
            date = start_date + timedelta(days=x)
            date = date.strftime('%Y-%m-%d')
            dates.append(date)
        # Execute a SELECT query to check if the dates exist in the table
        query = "SELECT * FROM my_table WHERE date IN ({})".format(','.join('?' * len(dates)))
        cursor.execute(query, dates)
        result = cursor.fetchall()
        # Close the connection
        conn.close()
        current_dir = os.path.dirname(os.path.abspath(__file__)) 
        abs_path = os.path.abspath(os.path.join(current_dir, "logo.svg"))
        html = """
        <html>
        <head>
            <title>Repas</title>
            <style>
                body {{
                    background-color: white;
                }}
                table {{
                  border-collapse: collapse;
  position: absolute;
  top: 50%;
  left: 0%;
  transform: translate(0%, -50%);
  width: 100%;
                }}
                h1 {{
                    text-align: center;
                }}
td {{
  border: 1px solid black;
  padding: 8px;
  text-align: center;
}}
.logo {{
  position: absolute;
  top: 0;
  right: 0;
  width: 150px;
}}
th {{background-color: #f2f2f2;
  border: 1px solid black;
  padding: 8px;}}

table tfoot tr:first-child td:nth-child(-n+4) {{
  border: none;
}}
table tfoot tr:last-child td:nth-last-child(-n+2) {{
  background-color: #f2f2f2;
  border: 1px solid black;
  padding: 8px;
    font-weight: bold;
}}

            </style>
        </head>
        <body>
<img class="logo" src="{}" alt="Logo">
<br><br><br><br><br><br><br><br>

<h1>Repas de la semaine du {} au {}</h1>

<table>
  <thead>
    <th>Date</th>
    <th>Repas complets<br>(2,50€)</th>
    <th>Plats simples<br>(1,60€)</th>
    <th>Recettes</th>
    <th>Dépenses</th>
    <th>Différence </th>
  </thead>
  <tbody>""".format(abs_path, start_date.strftime('%d %B %Y') , end_date.strftime('%d %B %Y'))
        tot=0
        for row in sorted(result, key=lambda x: x[0]):
            date=datetime.strptime(row[0], '%Y-%m-%d').strftime('%A %d %B %Y')
            percu=row[1]*2.5+row[2]*1.6
            diff=percu-row[3]
            tot+=diff
            html+="""
  <tr>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{:.2f} €</td>
    <td>{:.2f} €</td>
    <td>{:.2f} €</td>
  </tr>
""".format(date,row[1],row[2],percu, row[3], diff)
        html+="""</tbody>
          <tfoot>
        <tr>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td>Total</td>
    <td>{:.2f} €</td>
  </tr>
  </tfoot>""".format(tot)
        
        html+="""
              </table>
              </body>
              </html>"""
        options={   'encoding': 'UTF-8', 
                    "enable-local-file-access": "",
                    'margin-top': '1cm',
                    'margin-right': '1cm',
                    'margin-bottom': '1cm',
                    'margin-left': '1cm',
                    'orientation': 'landscape'
                }
        # Convertit le fichier HTML en PDF
        pdfkit.from_string(html, "/tmp/resultat.pdf", options=options)
        # Ouvre le fichier PDF avec l'éditeur par défaut
        subprocess.run(['xdg-open', '/tmp/resultat.pdf'])







if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())

