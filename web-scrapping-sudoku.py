import requests
from bs4 import BeautifulSoup
import csv

#response = requests.get('https://www.programme.tv/sudoku/grille_du_jour_facile.php')
#response = requests.get('https://www.programme.tv/sudoku/grille_du_jour_moyen.php')
#response = requests.get('https://www.programme.tv/sudoku/grille_du_jour_difficile.php')
response = requests.get('https://www.programme.tv/sudoku/grille_du_jour_expert.php')

soup = BeautifulSoup(response.content, "html.parser")
soup.prettify()
liste_td = soup.find_all('td', attrs={'class': 'gridGame-cell'})

with open('sudoku.csv', 'w', newline='') as liste_chiffres_csv:
    writer = csv.writer(liste_chiffres_csv)
    for i in range(len(liste_td)):
        span = liste_td[i].find('span', attrs={'gridGame-start'})
        chiffre = 0
        if span:
            chiffre = span.string
        writer.writerow([chiffre])
