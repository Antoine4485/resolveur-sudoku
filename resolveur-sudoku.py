# créer un tableau 2D avec, dans chacune des cases, un tableau de 2 éléments(digit, type)
# où le digit est compris entre 1 et 9, et le type a la valeur INITIAL_LBL ou NOT_INITIAL_LBL
# remplir les cases de "départ" avec le couple "digit/'initiale'"
# balayer le tableau de haut en bas et de gauche à droite
# dès qu'une case est vide on s'y arrête et on y met le plus petit digit possible, avec un type NOT_INITIAL_LBL
# 1- si on ne peut mettre aucun digit,
# on revient à la première case précédente NOT_INITIAL_LBL et on y met le plus petit digit possible toujours,
# mais supérieur à celui actuellement dans la case
# si pas possible on revient au 1-

import random
import requests
from bs4 import BeautifulSoup
import csv
from colorama import Back, Fore, Style, deinit, init


class SudokuResolver:
    CSV_FILE = "sudoku.csv"
    DIGIT_CODE = "digit"
    TYPE_CODE = "type"
    INITIAL_LBL = "initial"
    NOT_INITIAL_LBL = "not_initial"
    NB_LINES = 9
    NB_COLUMNS = 9
    NB_TRIES = 0
    NB_TRIES_MAX = 100
    CARRIAGE_RETURN = "\n"
    VERTICAL_SEP = "|"
    HORIZONTAL_SEP = "-"
    HORIZONTAL_SEP_LINE = f"{HORIZONTAL_SEP * 4 * NB_COLUMNS}{HORIZONTAL_SEP}{CARRIAGE_RETURN}"
    HORIZONTAL_SPACE = " "

    def __init__(self):
        self.grid = []
        #ind = random.randrange(2)
        self.__init_grid()
        self.__show_grid()
        self.__resolve_sudoku()
        self.__show_grid()

    def __show_grid(self) -> None:
        # on ne peut pas utiliser la méthode "join()" pour alimenter la variable "draw" à cause des différents styles
        # utilisés
        init()  # sous windows (pour Colorama)
        draw = self.CARRIAGE_RETURN

        for i in range(self.NB_LINES):
            horizontal_sep_style = f"{Fore.BLACK}{Style.NORMAL}" if i % 3 == 0 else ""
            draw += f"{horizontal_sep_style}{self.HORIZONTAL_SEP_LINE}{Style.RESET_ALL}"

            for j in range(self.NB_COLUMNS):
                digit = str(self.grid[i][j][self.DIGIT_CODE]).replace("0", self.HORIZONTAL_SPACE)
                # print(digit)
                digit_style = f"{Fore.GREEN}{Style.NORMAL}"
                if self.grid[i][j][self.TYPE_CODE] == self.INITIAL_LBL:
                    digit_style = f"{Fore.BLUE}{Style.NORMAL}"
                digit = f"{digit_style}{digit}{Style.RESET_ALL}"
                vertical_sep_style = f"{Fore.BLACK}{Style.NORMAL}" if j % 3 == 0 else ""

                draw += (f"{vertical_sep_style}{self.VERTICAL_SEP}{self.HORIZONTAL_SPACE}{digit}"
                         f"{self.HORIZONTAL_SPACE}{Style.RESET_ALL}")

            draw += f"{Fore.BLACK}{Style.NORMAL}{self.VERTICAL_SEP}{self.CARRIAGE_RETURN}{Style.RESET_ALL}"

        draw += f"{Fore.BLACK}{Style.NORMAL}{self.HORIZONTAL_SEP_LINE}{Style.RESET_ALL}"

        print(draw)
        deinit()  # sous windows (pour Colorama)

    def __validate_row(self, row_id: int, digit: int) -> bool:
        for j in range(self.NB_COLUMNS):
            if self.grid[row_id][j][self.DIGIT_CODE] == digit:
                return False

        return True

    def __validate_column(self, column_id: int, digit: int) -> bool:
        for i in range(self.NB_LINES):
            if self.grid[i][column_id][self.DIGIT_CODE] == digit:
                return False

        return True

    def __validate_square(self, row_id: int, column_id: int, digit: int) -> bool:
        first_square_row = row_id // 3 * 3
        first_column_row = column_id // 3 * 3
        for i in range(first_square_row, first_square_row + 3):
            for j in range(first_column_row, first_column_row + 3):
                if self.grid[i][j][self.DIGIT_CODE] == digit:
                    return False

        return True

    def __validate_digit(self, row_id: int, column_id: int, digit: int) -> bool:
        if (not digit.is_integer() or digit not in range(1, 10)
                # on ne peut pas remplacer un digit par un digit inférieur
                or digit <= self.grid[row_id][column_id][self.DIGIT_CODE]):
            return False

        return True

    def __validate_digit_in_grid(self, row_id: int, column_id: int, digit: int) -> bool:
        if (not self.__validate_digit(row_id=row_id, column_id=column_id, digit=digit) or
                not self.__validate_row(row_id=row_id, digit=digit) or
                not self.__validate_column(column_id=column_id, digit=digit) or
                not self.__validate_square(row_id=row_id, column_id=column_id, digit=digit)):
            return False

        return True

    def add_digit(self, row_id: int = 0, column_id: int = 0, digit: int = 1,
                  digit_type: str = NOT_INITIAL_LBL) -> bool:
        # print('ajouterdigit')
        while digit < 10:
            if self.__validate_digit_in_grid(row_id=row_id, column_id=column_id, digit=digit):
                self.grid[row_id][column_id] = {self.DIGIT_CODE: digit, self.TYPE_CODE: digit_type}
                # afficheGrille(grid)
                # input()
                return True
            digit += 1

        return False

    def get_pos_previous_cell(self, start_row_id: int, start_col_id: int):
        # print('getPositionCasePrecedente')
        flag = False
        for i in range(self.NB_LINES - 1, -1, -1):
            for j in range(self.NB_COLUMNS - 1, -1, -1):
                if not flag and i <= start_row_id and j <= start_col_id:
                    flag = True
                    continue
                if flag and self.grid[i][j][self.TYPE_CODE] == self.NOT_INITIAL_LBL:
                    return i, j
        return -1, -1

    def __resolve_sudoku(self):
        posX_case_prec, posY_case_prec = -1, -1
        # NB_TRIES = 0
        # while True and NB_TRIES < 1000:
        while True:
            # print(f'resoudreSudoku A: {posX_case_prec} {posY_case_prec}')
            # NB_TRIES += 1
            flag = False
            for i in range(self.NB_LINES):
                for j in range(self.NB_COLUMNS):
                    if (self.grid[i][j][self.TYPE_CODE] == self.INITIAL_LBL
                            # s'il y a un digit sur la case et qu'il y a par ailleurs une case à modifier,
                            # si cette case à modifier se situe après la case en cours, on passe à la suivante
                            or (self.grid[i][j][self.DIGIT_CODE] > 0
                                and posX_case_prec >= 0 and posY_case_prec >= 0
                                and not (i == posX_case_prec and j == posY_case_prec))):
                        continue
                    # print(f'resoudreSudoku: {i} {j}')
                    if not self.add_digit(i, j):
                        self.grid[i][j][self.DIGIT_CODE] = 0
                        posX_case_prec, posY_case_prec = self.get_pos_previous_cell(i, j)
                        # print(f'resoudreSudoku B: {posX_case_prec} {posY_case_prec}')
                        flag = True
                        break
                if flag:
                    break
            if flag:
                continue
            posX_case_prec, posY_case_prec = -1, -1
            if i == self.NB_LINES - 1 and j == self.NB_COLUMNS - 1:
                break  # programme terminé

    # remplissage en mémoire de la grille de jeu à partir du fichier csv
    def __init_grid(self):
        self.grid = [[{} for _ in range(self.NB_COLUMNS)] for _ in range(self.NB_LINES)]

        with open(self.CSV_FILE, newline="") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=" ", quotechar="|")
            cpt, i, j = 0, 0, 0
            for row in spamreader:
                i = cpt // 9
                j = cpt % 9
                digit = int(row[0])
                digit_type = self.INITIAL_LBL
                if digit == 0:
                    digit_type = self.NOT_INITIAL_LBL
                self.grid[i][j] = {self.DIGIT_CODE: digit, self.TYPE_CODE: digit_type}
                cpt += 1


if __name__ == '__main__':
    SudokuResolver()
