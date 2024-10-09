#créer un tableau 2D avec, dans chacune des cases, un tableau de 2 éléments(chiffre, type)
	#où le chiffre est compris entre 1 et 9, et le type a la valeur "initiale" ou "non_initiale"
#remplir les cases de "départ" avec le couple "chiffre/'initiale'"
#balayer le tableau de haut en bas et en commençant par la gauche
	#dès qu'une case est vide on s'y arrête et on y met le plus petit chiffre possible, avec un type "non_initiale"
	# 1- si on ne peut mettre aucun chiffre,
		# on revient à la première case précédente "non_initiale" et on y met le plus petit chiffre possible toujours,
		# mais supérieur à celui actuellement dans la case
		# si pas possible on revient au 1-

import random
import requests
from bs4 import BeautifulSoup
import csv
from colorama import Back, Fore, Style, deinit, init

nb_lignes = 9
nb_colonnes = 9
nbEssais = 0
limitePourTests = 100
lst_grille = [[[] for _ in range(nb_colonnes)] for _ in range(nb_lignes)]
ind = random.randrange(2)

def afficheGrille(lst_grille):
	init() # sous windows (pour Colorama)
	grille = '\n'
	for i in range(nb_lignes):
		style_pointilles = ''
		if i % 3 == 0:
			style_pointilles = Fore.BLACK + Style.NORMAL
		grille += style_pointilles + '----' * nb_colonnes + '-\n' + Style.RESET_ALL
		for j in range(nb_colonnes):
			chiffre = str(lst_grille[i][j]['chiffre'])
			#print(chiffre)
			if chiffre == '0':
				chiffre = ' '
			style_chiffre = Fore.GREEN + Style.NORMAL
			if lst_grille[i][j]['type'] == 'initiale':
				style_chiffre = Fore.BLUE + Style.NORMAL
			chiffre = style_chiffre + chiffre + Style.RESET_ALL
			style_barre = ''
			if j % 3 == 0:
				style_barre = Fore.BLACK + Style.NORMAL
			grille += style_barre + '| ' + chiffre + ' ' + Style.RESET_ALL		
		grille += Fore.BLACK + Style.NORMAL + '|\n' + Style.RESET_ALL
	for j in range(nb_colonnes):	
		grille += Fore.BLACK + Style.NORMAL + '----'
	grille += '-\n' + Style.RESET_ALL
	print(grille)
	deinit() # sous windows (pour Colorama)

def validerChiffre(lst_grille, num_ligne, num_colonne, chiffre):
	if (chiffre < 1 or chiffre > 9
	# on ne peut pas remplacer un chiffre par un chiffre inférieur 
	or chiffre <= lst_grille[num_ligne][num_colonne]['chiffre']):
		return False

	valid = True

	#valider ligne
	for j in range(nb_colonnes):
		if lst_grille[num_ligne][j]['chiffre'] == chiffre:
			valid = False
			break

	#valider colonne
	for i in range(nb_lignes):
		if lst_grille[i][num_colonne]['chiffre'] == chiffre:
			valid = False
			break
		
	#valider carré
	premiere_ligne_carre = num_ligne // 3 * 3
	premiere_colonne_carre = num_colonne // 3 * 3	
	for i in range(premiere_ligne_carre, premiere_ligne_carre + 3):
		for j in range(premiere_colonne_carre, premiere_colonne_carre + 3):
			if lst_grille[i][j]['chiffre'] == chiffre:
				valid = False
				break

	return valid

#print(validerChiffre(lst_grille, 5, 5, 3))

def ajouterChiffre(lst_grille, num_ligne = 0, num_colonne = 0,	
		chiffre = 1, type_chiffre = 'non_initiale'):
	#print('ajouterChiffre')
	while chiffre < 10:
		if validerChiffre(lst_grille, num_ligne, num_colonne, chiffre):		
			lst_grille[num_ligne][num_colonne] = {'chiffre': chiffre, 'type': type_chiffre}
			#afficheGrille(lst_grille)
			#input()		
			return True
		chiffre = chiffre + 1
	return False

def getPositionCasePrecedente(lst_grille, ligne_depart, colonne_depart):
	#print('getPositionCasePrecedente')
	flag = False
	for i in range(nb_lignes-1, -1, -1):
		for j in range(nb_colonnes-1, -1, -1):			
			if flag == False and i <= ligne_depart and j <= colonne_depart:
				flag = True
				continue				
			if flag == True and lst_grille[i][j]['type'] == 'non_initiale':
				return i, j
	return -1, -1

def resoudreSudoku(lst_grille):
	posX_case_prec, posY_case_prec = -1, -1	
	#nbEssais = 0
	#while True and nbEssais < 1000:
	while True:
		#print(f'resoudreSudoku A: {posX_case_prec} {posY_case_prec}')
		#nbEssais += 1		
		flag = False
		for i in range(nb_lignes):		
			for j in range(nb_colonnes):
				if (lst_grille[i][j]['type'] == 'initiale'
					# s'il y a un chiffre sur la case et qu'il y a par ailleurs une case à modifier,
					# si cette case à modifier se situe après la case en cours, on passe à la suivante 
					or (lst_grille[i][j]['chiffre'] > 0 
						and posX_case_prec >= 0 and posY_case_prec >= 0
						and not (i == posX_case_prec and j == posY_case_prec))):
					continue
				#print(f'resoudreSudoku: {i} {j}')			
				if not ajouterChiffre(lst_grille, i, j):
					lst_grille[i][j]['chiffre'] = 0
					posX_case_prec, posY_case_prec = getPositionCasePrecedente(lst_grille, i, j)
					#print(f'resoudreSudoku B: {posX_case_prec} {posY_case_prec}')
					flag = True
					break
			if flag == True:
				break
		if flag == True:
			continue
		posX_case_prec, posY_case_prec = -1, -1
		if i == nb_lignes-1 and j == nb_colonnes-1:
			break	# programme terminé

# remplissage en mémoire de la grille de jeu à partir du fichier csv
def initGrille(lst_grille):
	with open('liste_chiffres.csv', newline='') as csvfile:
	    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
	    cpt, i, j = 0, 0, 0
	    for row in spamreader:
	        i = cpt // 9
	        j = cpt % 9
	        chiffre = int(row[0])
	        type_chiffre = 'initiale'
	        if chiffre == 0:
	            type_chiffre = 'non_initiale'
	        lst_grille[i][j] = {'chiffre': chiffre, 'type': type_chiffre}
	        cpt += 1


initGrille(lst_grille)
afficheGrille(lst_grille)
resoudreSudoku(lst_grille)
afficheGrille(lst_grille)