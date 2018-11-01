from PIL import Image  # Gestion facile des images (Pillow, un fork de PIL)

import Labyrinthe  # Nécessaire à la génération des labyrinthe


class ImageAdapater:
    """
    Abstract class to extends to be known as valid image type
    """

    @classmethod
    def draw(cls, xy, color) -> None:
        pass

    @classmethod
    def save(cls, name) -> None:
        pass


class ImagePIL(ImageAdapater):
    """
    Class who communicates with the Pillow module
    """
    name = "pil"
    image = None

    def __init__(self, sizex, sizez) -> None:
        self.image = Image.new("RGB", (sizex, sizez))

    def draw(self, xy, color) -> None:
        self.image.putpixel(xy, color)

    def save(self, name) -> None:
        self.image.save(name + ".png", "PNG")

    def show(self) -> None:
        self.image.show()


class ImagePGM(ImageAdapater):
    """
    Class who manage .pgm format
    """
    name = "pgm"
    sizex = 0
    sizey = 0
    head = str()
    text = str()
    image = None

    def __init__(self, sizex, sizey) -> None:
        self.sizex = sizex
        self.sizey = sizey
        self.head = "P2\n{0} {1}\n255".format(sizex, sizey)
        self.text = "0 " * (sizex * sizey)

    def draw(self, xy, color) -> None:
        chain = list()
        for c in self.text.split(" "):
            chain.append(str(c))
            chain.append(" ")

        # Code de la cellule, de 0 à (x * y) - 1 par ligne (ligne 1: 0, 1, ... X - 1) (ligne 2: X, X + 1, ... 2X - 1)
        cellule_code = (xy[1] * self.sizex + xy[0])

        if xy[0] >= self.sizex or xy[1] >= self.sizey:
            raise IndexError("One or more coordinate is outside of the image")

        for (i, c) in enumerate(chain):
            # Les caractères impaires sont des espaces, on les ignores
            if i % 2 == 1:
                continue

            if i / 2 == cellule_code:
                chain[i] = str(color)
                break

        self.text = "".join(chain)

    def save(self, name) -> None:
        f = open(name + ".pgm", "w")
        f.write(self.head)
        f.write("\n")
        f.write(self.text)
        f.close()
        self.image = f


class Choice:
    """
    Each instance of this class represents a moment when we make a choice.
    """
    # Case d'origine ou on a fait un choix (utile pour la marqué comme la précédente)
    origin = 0, 0
    # Typé comme une liste de n-uplets
    possibility = []

    def __init__(self, origin, possibility):
        self.origin = origin
        self.possibility = possibility

    def makechoice(self) -> tuple:
        """
        Make a choice between different possible cells
        :return tuple: Chosen cell (she had already been removed from possibility)
        """
        (posx, posy) = self.possibility[0], self.possibility[1]
        del self.possibility[0]
        del self.possibility[0]

        return posx, posy

    def hadexploreallpossibility(self):
        return len(self.possibility) == 0


def convertcodetocolor(code):
    """
    Convert labyrinth color code to RGB/Unique color
    :param code: Code provided by labyrinth generation (between 0 and 3)
    :return tuple|int: Code couleur à écrire dans l'image, respectivement un tuple RGB pour PIL et une couleur unique pour les images pgm
    """
    # tuple or int
    pixel = (0, 0, 0)
    color = 0

    if code == 0:
        pixel = (0, 0, 0)
        color = 0
    elif code == 1:
        pixel = (255, 255, 255)
        color = 255
    elif code == 2:
        pixel = (128, 0, 128)
        color = 100
    elif code == 3:
        pixel = (0, 128, 0)
        color = 170

    if imageadapter.name == "pil":
        return pixel
    elif imageadapter.name == "pgm":
        return color


def isvalid(labyrinth, cellule_x, cellule_y) -> bool:
    """
    Check if a cell at specified coordinate is valid (not a wall)
    :param labyrinth: 2 dimensions tabs who act as labyrinthe
    :param cellule_x: X coordinate
    :param cellule_y: Y coordinate
    :return bool: True if specified cell is not a wall
    """
    return labyrinth[cellule_x][cellule_y] != 0


def findnear(cellule_x, cellule_y) -> list:
    """
    Find the four near cell
    :param cellule_x: X coordinate
    :param cellule_y: Y coordinate
    :return list: List containing the four coordinates
    """
    return [
        (cellule_x + 1, cellule_y),
        (cellule_x - 1, cellule_y),
        (cellule_x, cellule_y + 1),
        (cellule_x, cellule_y - 1)
    ]


def getbegin(labyrinth) -> tuple:
    """
    Return the labyrinth beginning position
    This method is useless because begin is always (1,1)
    :param labyrinth: 2 dimensions tabs who act as labyrinth
    :return tuple: 2-uplet who contains beginning position
    :raise Exception: If the labyrinth doesn't contain any entry point
    """
    for longeur in range(0, len(labyrinth)):
        for hauteur in range(0, len(labyrinth[longeur])):
            if labyrinth[longeur][hauteur] == 2:
                return longeur, hauteur

    Exception("Unhandled exception")


def findnearvalid(labyrinth, exclude, cellule_x, cellule_y) -> list:
    """
    Find near valid cells (not a wall)
    :param labyrinth: 2 dimensions tabs who act as labyrinth
    :param exclude: A cell to exclude (basically the previous location)
    :param cellule_x: Current cell X
    :param cellule_y: Current cell Y
    :return list: List of all available coordinate (grouped by two)
    """
    validcellule = []

    for near in findnear(cellule_x, cellule_y):
        if isvalid(labyrinth, near[0], near[1]) and exclude != near:
            validcellule += (near[0], near[1])

    return validcellule


def isbeginning(labyrinth, cellule_x, cellule_y) -> bool:
    """
    Check if this cell is the beginning
    :param labyrinth: 2 dimensions tabs who act as labyrinth
    :param cellule_x: Current cell X
    :param cellule_y: Current cell Y
    :return bool: True if this cell is the beginning
    """
    return labyrinth[cellule_x][cellule_y] == 2


def isend(labyrinth, cellule_x, cellule_y) -> bool:
    """
    Check if this cell is the end
    :param labyrinth: 2 dimensions tabs who act as labyrinth
    :param cellule_x: Current cell X
    :param cellule_y: Current cell Y
    :return bool: True if this cell is the end
    """
    return labyrinth[cellule_x][cellule_y] == 3


def displaylaby(tab2d, sizemultiplicator=10) -> None:
    """
    Build an image since a two dimensions tab
    :param tab2d: 2 dimensions tabs who act as labyrinth
    :param sizemultiplicator: Multiplicator for the image. For example, if you use ten, one laby cell will be represented by 10x10 pixels on the image
    """
    global labyimg
    labyimg = imageadapter(sizemultiplicator * len(tab2d), sizemultiplicator * len(tab2d[0]))

    for longeur in range(0, len(tab2d)):
        for hauteur in range(0, len(tab2d[longeur])):
            # Pour chaque élement du tableau

            value = tab2d[longeur][hauteur]
            pixel = convertcodetocolor(value)

            # Tous les pixels de la cellule
            for x in range(0, sizemultiplicator):
                for y in range(0, sizemultiplicator):
                    coord = (sizemultiplicator * longeur + x, sizemultiplicator * hauteur + y)

                    labyimg.draw(coord, pixel)


# Constantes
YES_ANSWER = ["y", "yes", "oui", "o"]
NO_ANSWER = ["n", "no", "non"]

# Mode debug / développeur
debug = False
validoutput = False
while not validoutput:
    entry = input("Voulez-vous activer le mode 'debug' ? (oui/non)")
    if entry in YES_ANSWER:
        debug = True
        validoutput = True
    elif entry in NO_ANSWER:
        validoutput = True

# Image provider
imageadapter = ImagePIL
validoutput = False
while not validoutput:
    entry = input("Quel moteur de rendu d'image voulez-vous utiliser ? (pil/pgm). Default = PIL")
    if entry in ["pil", "d", "default"]:
        validoutput = True
    elif entry in ["pgm"]:
        imageadapter = ImagePGM
        validoutput = True

# Génération du labyrinthe
labyrinthe = Labyrinthe.creer(11, 15)

# Afficher le code de génération
if debug:
    print("[*] Code de génération : {0}".format(labyrinthe))

# Size multiplicateur
size_multiplicator = 10
validoutput = False
while not validoutput:
    entry = input(
        "De combien souhaitez-vous zoomer l'image par rapport au labyrinthe d'origine ? (une valeur trop importante peut grandement ralentir le programme) Maximum recommandé : 100 (20 pour pgm). Défaut : 10.")
    if entry in ["d", "defaut"]:
        validoutput = True
    else:
        try:
            entry = int(entry)
            size_multiplicator = entry
            validoutput = True
        except ValueError:
            print("Ce nombre n'est pas valide !")

displaylaby(labyrinthe, sizemultiplicator=size_multiplicator)

"""
== CORPS DU PROGRAMME ==
"""

# La position précédente dans le Labyrinthe (utilisé pour ne pas faire sans arrêt demi-tour)
precedent_pos = (-1, -1)
# Départ au départ du labyrinthe
pos = getbegin(labyrinthe)

# Jump to moment when choose
choose_pos = (-1, -1)
# List of possibility for deplacement
pos_possibility = []

# Les casses par lesquelle le programme est passé
collected_case = []

# Liste de choix faits
choose = []

while not isend(labyrinthe, pos[0], pos[1]):
    # == Partie logique == #

    # Les casses candidates au prochain déplacement
    candidate_next = findnearvalid(labyrinthe, precedent_pos, pos[0], pos[1])

    new_pos = (0, 0)
    # Pas le choix (une seule case de libre)
    if len(candidate_next) == 2:
        new_pos = (candidate_next[0], candidate_next[1])

        # Assignation des variables
        precedent_pos = pos
        pos = new_pos

    # Dans le mur - C'est à dire qu'on a fait un mauvais choix précédément
    elif len(candidate_next) == 0:
        print("[*] Ail, je suis dans le mur ! J'ai dû faire un mauvais choix précédément")

        # Le faire "JUMP" là ou il a fait un choix
        new_pos = choose[-1].makechoice()

        # Assignation des variables
        precedent_pos = choose[-1].origin  # Ici on a mis la précédante mais c'est pas la vrai précédante si on a jump
        pos = new_pos

        if choose[-1].hadexploreallpossibility():
            del choose[-1]

    # Faire un choix
    else:
        print("[*] Trop de case, je dois faire un choix...")

        # Candidate next c'est un tableau avec les chiffres de coord (sensé être groupé par deux)
        c_instance = Choice(origin=(pos[0], pos[1]), possibility=candidate_next)
        new_pos = c_instance.makechoice()
        choose.append(c_instance)

        # Assignation des variables
        precedent_pos = pos
        pos = new_pos

    # == End of Partie logique == #

    # Partie visuelle
    collected_case += pos

"""
== FIN DU CORPS DU PROGRAMME ==
"""

# Affichage sur l'image
for i in range(0, len(collected_case), 2):
    longeur = collected_case[i]
    hauteur = collected_case[i + 1]

    # Tous les pixels de la cellule
    for x in range(0, int(size_multiplicator * 0.6)):
        for y in range(0, int(size_multiplicator * 0.6)):
            coord = (size_multiplicator * longeur + x, size_multiplicator * hauteur + y)

            if imageadapter.name == "pil":
                labyimg.draw(coord, (255, 255, 0))
            elif imageadapter.name == "pgm":
                labyimg.draw(coord, str(200))

# Sauvegarde de l'image
labyimg.save("labyrinth")

print("Exécution complète.")

# Affichage de l'image
if imageadapter.name == "pil":
    validoutput = False
    while not validoutput:
        entry = input("Voulez-vous afficher l'image ? (oui/non)")
        if entry in YES_ANSWER:
            validoutput = True
            labyimg.show()
        elif entry in NO_ANSWER:
            validoutput = False

exit(0)
