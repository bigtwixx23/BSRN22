import time
from cfonts import render, say
from colorama import Fore, Back, Style
import numpy as np
import threading


class Spieler(threading.Thread):
    """Representation/Object of player.

    This class represents player, including her/his name and her/his own
    field.

    """

    def __init__(self, name, n):
        """Init-Method for Spieler.

        :param name: Name of player
        :param n: width/length of the field
        """

        threading.Thread.__init__(self)
        self.name = name
        self.n = n
        self.field = dict({})
        self.lifes = 0
        self.attacked = []
        self.otherPl = None
        self.game = None

        # These are bool-variables for signalizing and synchronising between
        # the processes
        self.initialize = False
        self.turn = False

        # Asserts, that the field is not bigger than 10
        assert n <= 10
        assert n >= 5

        # Initalizing empty field
        for k in "ABCDEFGHIJ"[:n]:
            self.field[k] = dict({})
            for l in range(1, n+1):
                self.field[k][str(l)] = 0

        # This is a dictionary for the ships, where
        # the key is the length of the ship and
        # the value is the amount of ships available for this length.
        # You can make changes here.
        self.properties = {
            "5": 0,
            "4": 0,
            "3": 0,
            "2": 1
        }

    def run(self):
        """Run Method of Thread Object

        This is the Main Process for one Player. He first waits, to initialize
        his own fields. After that he goes through a while loop, in which he
        makes his pull and waits until it's his turn again.

        :return:
        """
        while not self.initialize:
            time.sleep(1)

        self.initializeField()
        self.game.player_makes_pull = False


        while not self.game.finished:
            while not self.turn and not self.game.finished:
                time.sleep(1)
            if not self.game.finished:
                self.pull()
                self.game.player_makes_pull = False
                self.turn = False

    def putShip(self, arr):
        """This method puts one ship on the field

        First, it checks, whether everything is fine with the fields. After that,
        it puts the ship on the field.

        :param arr: Array of Strings of Fields (arr = ["A1", "A2", "D5"])
        :return: Nothing
        """

        size = len(arr)

        # Check, whether the size is in range.
        assert 1 < size <= 5

        # Check whether ship is available (especially for the given size).
        if not self.properties.get(str(size)) > 0:
            raise IndexError("Kein " + str(size) + "er Schiff verfuegbar!")

        # arr = ["A1", "A2", "D5"]

        for i in range(len(arr)):  # i = 1

            # Check, whether there is a ship already placed.
            if self.field[arr[i][0]][arr[i][1]] == 1:
                raise ValueError("Hier liegt bereits ein Schiff!")

            if i == 0:
                continue

            # Check, whether the current field and the field before (in "arr")
            # are neighbours.
            elif not checkIfNeighbours(arr[i - 1], arr[i]):
                raise ValueError("Die Auswahl muss nebeneinander liegen!")

        # Decreases the availability of ships of the given size
        self.properties[str(size)] -= 1

        # If everything is fine, the ship gets placed.
        for i in arr:
            self.fillField(i)

    def fillField(self, field):
        """Just a helper function, to fill ONE field

        :param field: Field (field = "A1")
        """
        self.field[field[0]][field[1]] = 1
        self.lifes += 1

    def killOwnField(self, target):
        self.field[target[0]][str(int(target[1]))] = 2

    def getAttacked(self, pos):
        """This method gets called, whenever the player gets attacked.

        The method first checks, whether the attacked field is empty or not
        and after that it does change the values.

        :param pos: target position (pos = "A1")
        :return: 0: no hit; 1: hit; 2: already hitten;
        """

        pos = pos[0].capitalize() + pos[1]

        # Check, whether field is empty or not
        if self.field[pos[0]][pos[1]] == 1:

            # If field not empty, call method below and decrease the life
            self.killOwnField(pos)
            self.lifes -= 1
            return 1

        return self.field[pos[0]][pos[1]]

    def initializeField(self):
        """Console-Method for placing the ships.

        :return: Nothing
        """

        print(100*"\n")
        print(self.name + " ist dran.")

        # For each ship-size
        for j in list(self.properties.keys()):  # j := Schiffgröße

            # While there are ships of size "j" available
            while self.properties[j] > 0:
                print("Bitte platzieren Sie Ihr " + str(j) +
                      "er Schiff: (Die Felder müssen nebeneinander liegen! Z.b A1, A2, A3)\n")

                platzierung = []

                # For each part of one Ship (1 Field = 1 Part)
                for l in range(int(j)):

                    # Append field to list

                    while True:
                        inp = input(
                            "Geben Sie bitte das gewünschte Feld ein: (A-" + "ABCDEFGHIJ"[:self.n][-1] + "), (1-" + str(self.n) + ")     Muster: A1 (Beispiel)\n")

                        try:
                            if not inp[0].capitalize() in "ABCDEFGHIJ"[:self.n] or not int(inp[1]) in list(range(1, self.n + 1)):
                                print("Die letzte Eingabe geht ueber das Spielfeld hinaus. Versuchen Sie es erneut (ab letzter Eingabe).")
                                continue

                            inp = inp[0].capitalize() + inp[1]
                            platzierung.append(inp)
                            break

                        except Exception:
                            print("Die letzte Eingabe entspricht nicht dem vorgegebenen Muster! Versuchen Sie es erneut (ab letzter Eingabe).")


                try:
                    # Try to place the ship. Could raise Error, if
                    #   1. Fields are no neighbours
                    #   2. At least one field is used by another ship
                    self.putShip(platzierung)

                except ValueError:

                    print("Entweder mindestens eines der Felder ist bereits von einem anderen Schiff besetzt, oder die Auswahl bildet keine Reihe! Bitte noch einmal versuchen.")
                    continue

    def pull(self):
        """This method assists the player through his pull/turn.

        :return:
        """
        pl = self
        print(100 * "\n")
        print(pl.name + " ist jetzt dran")
        input("Klicke Enter um das momentane Feld anzuzeigen [enter]")

        print(100 * "\n")
        self.displayField()
        print("\n\nDein Leben liegt bei: "  + str(self.lifes))
        time.sleep(1)

        while True:

            target = input(
                "\n\nWelches gegnerische Feld möchten Sie attackieren? ")

            try:
                if not target[0].capitalize() in "ABCDEFGHIJ"[:self.n] or not int(target[1]) in range(1, self.n + 1):
                    print("Eingabe entspricht nicht dem Format!")
                    continue
            except:
                print("Eingabe entspricht nicht dem Format!")
                continue

            target = target[0].capitalize() + target[1]

            if target in pl.attacked:
                print("Hier hattest du bereits hin geschossen...")
                print("Versuche es erneut!\n\n")
                time.sleep(3)
                continue

            # Call Method for Opponent so he gets attacked (no matter if hit or not)
            ret = self.otherPl.getAttacked(target)

            # Add target to List of Attacked Fields (no matter if hit or not)
            pl.attacked.append(target)

            print(100*"\n")

            if ret == 0:

                print(render("Kein Treffer",
                                         font='chrome', colors=['red', 'black'],
                                         align='center'))

                print("\n" + self.name + "s Leben: " + str(self.lifes))
                print(self.otherPl.name + "s Leben: " + str(self.otherPl.lifes))
            elif ret == 1:
                print(render("Getroffen",
                             font='chrome', colors=['green', 'yellow'],
                             align='center'))
                print("\n" + self.name + "s Leben: " + str(self.lifes))
                print(
                    self.otherPl.name + "s Leben: " + str(self.otherPl.lifes))

            time.sleep(3)
            break

    def displayField(self):
        """Method for displaying the fields.

        Displays the own field of the current player, and a modified version
        of the opposite's field. Modified means, that you, as the current pla-
        yer, can only see, where you have shot, with 'X' as a hit and 'O' as a non-hit.

        """

        # Initializing
        field = self.field
        player = self
        otherField = self.otherPl.field
        otherPl = self.otherPl



        # Prepare the current players table
        matrix = []

        for i, j in field.items():
            matrix.append([" "] + [k for k, l in j.items()])
            break

        for i, j in field.items():
            b = []
            b.append(str(i))
            b.extend([l if l == 1 else "X" if l ==
                     2 else "_" for k, l in j.items()])
            matrix.append(b)

        # Creating an empty table for the opponent
        matrix1 = []

        for i, j in otherField.items():
            matrix1.append([" "] + [k for k, l in j.items()])
            break

        for i, j in otherField.items():
            b = []
            b.append(str(i))
            b.extend(["_" for k, l in j.items()])
            matrix1.append(b)

        # Modifying the opponents table
        alph = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]

        for i in player.attacked:

            i = i[0].capitalize() + i[1]

            first = alph.index(i[0]) + 1
            second = int(i[1])

            if otherField[i[0]][i[1]] == 2:
                matrix1[first][second] = "X"
            else:
                matrix1[first][second] = "O"

        # Printing both tables
        print(self.name + "s Spielfeld (deins):\n\n")
        print('\n'.join(
            ['\t'.join([str(cell) for cell in row]) for row in matrix]))
        print("\n\n\n" + self.otherPl.name + "s Spielfeld:\n\n")
        print('\n'.join(
            ['\t'.join([str(cell) for cell in row]) for row in matrix1]))


class Spiel:
    """This class is the representation of the game itself."""

    def __init__(self, n, pl1, pl2):
        """Init method of Spiel.

        :param n: length/width of field.
        :param pl1: Spieler-Object as a representation of Player 1
        :param pl2: Spieler-Object as a representation of Player 2
        """
        self.n = n
        self.pl1 = pl1
        self.pl2 = pl2
        self.pl1.otherPl = pl2
        self.pl1.game = self
        self.pl2.otherPl = pl1
        self.pl2.game = self

        self.pl1.start()
        self.pl2.start()

        # These are bool-variables for signalizing and synchronising between
        # the processes
        self.player_makes_pull = False
        self.finished = False

    def startOfGame(self):
        self.pl1.initialize = True
        self.player_makes_pull = True
        while self.player_makes_pull:
            time.sleep(1)

        self.pl2.initialize = True
        self.player_makes_pull = True
        while self.player_makes_pull:
            time.sleep(1)

    def match(self):
        """This method represents the actual game.

        Through a while loop, the players will play the game until one of them
        has no life left.
        """
        player = True
        while self.pl1.lifes > 0 and self.pl2.lifes > 0:  # Until no life left
            if player:
                self.pl1.turn = True
                self.player_makes_pull = True
                while self.player_makes_pull:
                    time.sleep(1)

            else:
                self.pl2.turn = True
                self.player_makes_pull = True
                while self.player_makes_pull:
                    time.sleep(1)

            player = not player

        print(100*"\n")
        winner = self.pl1 if self.pl1.lifes > 0 else self.pl2
        print(winner.name + " hat das Spiel gewonnen.")
        time.sleep(3)
        self.finished = True
        self.pl1.join()
        self.pl2.join()

        winnerOfTheGame = render(winner.name +' ist der Gewinner ', font='block', colors=['red', 'red'], align='center')
        print(winnerOfTheGame)


def checkIfNeighbours(a, b):
    """Checks, whether a and b are neighbours.

    :param a: Example "A1"
    :param b: Example "A2"
    :return: True, if neighbours, else False
    """

    alph = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    nums = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

    aLetter = a[0]
    aNumber = a[1]

    bLetter = b[0]
    bNumber = b[1]

    if aLetter == bLetter:
        return abs(int(aNumber) - int(bNumber)) == 1
    elif aNumber == bNumber:
        return abs(alph.index(aLetter) - alph.index(bLetter)) == 1
    else:
        return False


def Console():

    output = render('Battleships', font='chrome', colors=['blue', 'white'], align='center')
    second = render('the game of Ships', font='chrome', colors=['red', 'black'], align='center')
    print(output)
    print(second)

    name1 = input("Name des 1. Spielers: ")
    name2 = input("Name des 2. Spielers: ")

    while True:
        try:
            n = int(input("Wie groß soll das Spielfeld sein? (5 <= n <= 10) "))

            game = Spiel(n, Spieler(name1, n), Spieler(name2, n))
            break

        except Exception:
            print("Ungueltige Eingabe")

    game.startOfGame()
    game.match()


Console()
