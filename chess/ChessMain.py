import pygame as p

HEIGHT = WIDTH = 512
from chess import ChessEngine
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 30
IMAGES = {}
PIECE_SIZE = 0.9 * SQ_SIZE

def loadImages():
    for image in ["bb", "bk", "bn", "bp", "bq", "br", "wB", "wK", "wN", "wP", "wQ", "wR"]:
        IMAGES[image[1]] = p.transform.smoothscale(p.image.load("chess/images/{}.svg".format(image)), (PIECE_SIZE, PIECE_SIZE))

def main():
    p.init()
    p.font.init()
    my_font = p.font.SysFont('OpenType', 20)
    p.display.set_caption("Chess")
    p.display.set_icon(p.image.load("chess/images/icon.png"))
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()

    validMoves = gs.getValidmoves()
    moveMade = False # Flag variable

    loadImages()
    running = True
    sqSelected = ()
    playerClicks = [] # Two tuples [0] being piece to move [1] being location
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if (row, col) == sqSelected:
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2:
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    if move in validMoves:
                        print(move.getChessNotation())
                        gs.makeMove(move)
                        moveMade = True
                    # Reset after
                    sqSelected = ()
                    playerClicks = []
            elif e.type == p.KEYDOWN:
                if e.key == p.K_r:
                    gs.undoMove()
                    moveMade = True

        if moveMade:
            validMoves = gs.getValidmoves()
            moveMade = False

        drawGameState(screen, gs, my_font)
        clock.tick(MAX_FPS)
        p.display.flip()




# Responsible for the graphics!
def drawGameState(screen, state, font):
    # Draw board first obviously goofball
    drawBoard(screen, state.board)
    drawCoordinates(screen, font)

def drawBoard(screen, board):
    x_pos, y_pos = p.mouse.get_pos()
    col, row = x_pos // SQ_SIZE, y_pos // SQ_SIZE
    for y in range(DIMENSION):
        for x in range(DIMENSION):
            colour = [(230, 238, 210),(105, 135, 76)][(y + x) % 2]
            if y == row and x == col:
                al = 0.3
                r, g, b = colour
                r, g, b = r * (1 - al), g * (1 - al), b * (1 - al)
                mr, mg, mb = [(105, 135, 76), (230, 238, 210)][(y + x) % 2]
                mr, mg, mb = mr * al, mg * al, mb * al
                colour = (r + mr, g + mg, b + mb)
            p.draw.rect(screen, colour, p.Rect(x * SQ_SIZE, y * SQ_SIZE, SQ_SIZE, SQ_SIZE))

            d = (SQ_SIZE - PIECE_SIZE) / 2
            if board[y][x] != "_":
                screen.blit(IMAGES[board[y][x]],
                            p.Rect(x * SQ_SIZE + d, y * SQ_SIZE + d, PIECE_SIZE, PIECE_SIZE))


ranksToRows = {'8': 0, '7': 1, '6': 2, '5': 3, '4': 4, '3': 5, '2': 6, '1': 7}
rowsToRanks = {j: i for i, j in ranksToRows.items()}
filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
colsToFiles = {j: i for i, j in filesToCols.items()}

def drawCoordinates(screen, font):
    colour = [(105, 135, 76), (230, 238, 210)]
    for i in range(DIMENSION):
        screen.blit(font.render(rowsToRanks[i], False, colour[i % 2]), p.Rect(3, 4 + i * SQ_SIZE, 6, 6))
        screen.blit(font.render(colsToFiles[i], False, colour[(i + 1) % 2]), p.Rect(55 + i * SQ_SIZE, 496, 6, 6))

if __name__ == "__main__":
    main()