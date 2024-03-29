# I might start doing this from now on. Super fun just putting all of the constants in one file.
HEIGHT = WIDTH = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 30
IMAGES = {}
PIECE_SIZE = 0.9 * SQ_SIZE
FONT_SIZE = 20
ranksToRows = {'8': 0, '7': 1, '6': 2, '5': 3, '4': 4, '3': 5, '2': 6, '1': 7}
rowsToRanks = {j: i for i, j in ranksToRows.items()}
filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
colsToFiles = {j: i for i, j in filesToCols.items()}
piecePlusColour = {
    "Br": "r",
    "Bn": "n",
    "Bb": "b",
    "Bq": "q",
    "Bk": "k",
    "Bp": "p",
    "Wr": "R",
    "Wn": "N",
    "Wb": "B",
    "Wq": "Q",
    "Wk": "K",
    "Wp": "P"
}
cornersToRooks = {
    (0, 0): 0,
    (0, 7): 1,
    (7, 0): 2,
    (7, 7): 3
}