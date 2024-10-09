# On crée un tableau 2D avec, dans chacune des cases, un dictionnaire ayant les clés "chiffre" et "type", le chiffre
# étant compris entre 1 et 9 et le type ayant la valeur INITIAL_LBL ou NOT_INITIAL_LBL.
# On balaie ensuite le tableau de haut en bas et de gauche à droite. Dès qu'une case est vide on y met le plus petit
# chiffre possible, avec un type NOT_INITIAL_LBL.
# 1- si on ne peut mettre aucun chiffre entre 1 et 9, on met un 0 et on revient à la première case précédente ayant le
# type NOT_INITIAL_LBL, dans laquelle on met le plus petit chiffre possible supérieur à celui actuellement dans la case.
# Si ce n'est pas possible on revient au 1-.

import requests
from bs4 import BeautifulSoup
import csv
from colorama import Fore, Style, deinit, init


class SudokuResolver:
    CSV_FILE = "sudoku.csv"
    DIGIT_CODE = "digit"
    TYPE_CODE = "type"
    INITIAL_LBL = "initial"
    NOT_INITIAL_LBL = "not_initial"
    DIGIT_MAX_VALUE = 9
    NB_ROWS = DIGIT_MAX_VALUE
    NB_COLUMNS = DIGIT_MAX_VALUE
    NB_TRIES = 0
    NB_TRIES_MAX = 100
    CSV_SEP = ","
    CARRIAGE_RETURN = "\n"
    VERTICAL_SEP = "|"
    HORIZONTAL_SEP = "-"
    HORIZONTAL_SEP_LINE = f"{HORIZONTAL_SEP * 4 * NB_COLUMNS}{HORIZONTAL_SEP}{CARRIAGE_RETURN}"
    HORIZONTAL_SPACE = " "

    def __init__(self, create_csv: bool = False):
        if create_csv:
            self.__create_csv()
        self.grid = []
        self.__init_grid()
        self.__show_grid()
        self.__resolve()
        self.__show_grid()

    def __show_grid(self) -> None:
        # on ne peut pas utiliser la méthode "join()" pour alimenter la variable "draw" à cause des différents styles
        # utilisés
        init()  # sous windows (pour Colorama)
        draw = self.CARRIAGE_RETURN

        for i in range(self.NB_ROWS):
            horizontal_sep_style = f"{Fore.BLACK}{Style.NORMAL}" if i % 3 == 0 else ""
            draw += f"{horizontal_sep_style}{self.HORIZONTAL_SEP_LINE}{Style.RESET_ALL}"

            for j in range(self.NB_COLUMNS):
                digit = str(self.grid[i][j][self.DIGIT_CODE]).replace("0", self.HORIZONTAL_SPACE)

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
        for i in range(self.NB_ROWS):
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
        if (not digit.is_integer()
                or digit not in range(1, self.DIGIT_MAX_VALUE + 1)
                # on ne peut pas remplacer un digit par un digit inférieur
                or digit <= self.grid[row_id][column_id][self.DIGIT_CODE]):
            return False

        return True

    def __validate_digit_in_grid(self, row_id: int, column_id: int, digit: int) -> bool:
        if (not self.__validate_digit(row_id=row_id, column_id=column_id, digit=digit)
                or not self.__validate_row(row_id=row_id, digit=digit)
                or not self.__validate_column(column_id=column_id, digit=digit)
                or not self.__validate_square(row_id=row_id, column_id=column_id, digit=digit)):
            return False

        return True

    def __get_prev_cell_pos(self, start_row_id: int, start_col_id: int) -> tuple:
        cell_finded = False

        for i in range(self.NB_ROWS - 1, -1, -1):
            for j in range(self.NB_COLUMNS - 1, -1, -1):
                if not cell_finded and i == start_row_id and j == start_col_id:
                    cell_finded = True
                    continue

                if cell_finded and self.grid[i][j][self.TYPE_CODE] == self.NOT_INITIAL_LBL:
                    return i, j

        return -1, -1

    def __add_digit(self, row_id: int = 0, column_id: int = 0) -> bool:
        digit = self.grid[row_id][column_id][self.DIGIT_CODE]

        while digit <= self.DIGIT_MAX_VALUE:
            if self.__validate_digit_in_grid(row_id=row_id, column_id=column_id, digit=digit):
                self.grid[row_id][column_id] = {self.DIGIT_CODE: digit, self.TYPE_CODE: self.NOT_INITIAL_LBL}
                return True
            digit += 1

        self.grid[row_id][column_id][self.DIGIT_CODE] = 0
        return False

    def __add_digits(self, prev_cell_pos_x: int, prev_cell_pos_y: int) -> tuple:
        for i in range(self.NB_ROWS):
            for j in range(self.NB_COLUMNS):
                if (self.grid[i][j][self.TYPE_CODE] == self.INITIAL_LBL
                        or (self.grid[i][j][self.DIGIT_CODE] > 0
                            and prev_cell_pos_x >= 0 and prev_cell_pos_y >= 0
                            and not (i == prev_cell_pos_x and j == prev_cell_pos_y))):
                    continue

                if not self.__add_digit(i, j):
                    prev_cell_pos = self.__get_prev_cell_pos(i, j)
                    return prev_cell_pos

        return -1, -1

    def __resolve(self):
        prev_cell_pos_x, prev_cell_pos_y = -1, -1

        while True:
            prev_cell_pos_x, prev_cell_pos_y = self.__add_digits(prev_cell_pos_x=prev_cell_pos_x,
                                                                 prev_cell_pos_y=prev_cell_pos_y)
            if prev_cell_pos_x == - 1 and prev_cell_pos_y - 1:
                break

    def __init_grid(self):
        self.grid = [[{} for _ in range(self.NB_COLUMNS)] for _ in range(self.NB_ROWS)]

        with open(self.CSV_FILE, newline="") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=" ", quotechar="|")

            for i, row in enumerate(spamreader):
                row = row[0].split(self.CSV_SEP)
                for j, value in enumerate(row):
                    digit = int(value)
                    digit_type = self.NOT_INITIAL_LBL if not digit else self.INITIAL_LBL
                    self.grid[i][j] = {self.DIGIT_CODE: digit, self.TYPE_CODE: digit_type}

    def __create_csv(self):
        # response = requests.get('https://www.programme.tv/sudoku/grille_du_jour_facile.php')
        # response = requests.get('https://www.programme.tv/sudoku/grille_du_jour_moyen.php')
        # response = requests.get('https://www.programme.tv/sudoku/grille_du_jour_difficile.php')
        response = requests.get('https://www.programme.tv/sudoku/grille_du_jour_expert.php')

        soup = BeautifulSoup(response.content, "html.parser")
        soup.prettify()
        tds = soup.find_all('td', attrs={'class': 'gridGame-cell'})

        with open(self.CSV_FILE, 'w', newline='') as liste_chiffres_csv:
            writer = csv.writer(liste_chiffres_csv)
            cpt = 0
            row = []

            for td in tds:
                span = td.find('span', attrs={'gridGame-start'})
                digit = span.string if span else 0
                row.append(digit)
                if (cpt + 1) % self.NB_COLUMNS == 0:
                    writer.writerow(row)
                    row = []
                cpt += 1


if __name__ == '__main__':
    SudokuResolver(create_csv=False)
