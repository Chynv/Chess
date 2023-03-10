import pygame as p
from CONST import *
from chess import ChessEngine
from time import time
import math
import random


def loadImages():
    for image in ["bb", "bk", "bn", "bp", "bq", "br", "wB", "wK", "wN", "wP", "wQ", "wR"]:
        IMAGES[image[1]] = p.transform.smoothscale(p.image.load("chess/images/{}.svg".format(image)),
                                                   (PIECE_SIZE, PIECE_SIZE))
        IMAGES[image[1] + "big"] = p.transform.smoothscale(p.image.load("chess/images/{}.svg".format(image)),
                                                           (PIECE_SIZE + 10, PIECE_SIZE + 10))


def main():
    p.init()
    p.font.init()
    my_font = p.font.SysFont('OpenType', FONT_SIZE)
    p.display.set_caption("Chess")
    p.display.set_icon(p.image.load("chess/images/icon.png"))
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()

    validMoves = gs.getValidMoves()
    moveMade = False  # Flag variable

    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []  # Two tuples [0] being piece to move [1] being location

    Holding = False
    offset = None

    dropped = False
    displayedMoves = []

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:

                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                offset = (location[0] % SQ_SIZE, location[1] % SQ_SIZE)

                Square = (row, col)
                isWhite = gs.board[row][col].islower()

                # If I have nothing in hand
                if sqSelected == ():
                    dropped = False
                    if gs.board[row][col] == "_":
                        continue
                    else:
                        sqSelected = Square
                        Holding = True
                else:  # If I have something in hand.
                    if Square == sqSelected:
                        Holding = True
                        continue
                    move = ChessEngine.Move(sqSelected, (row, col), gs.board)
                    result = gs.makeMove(move)
                    r, c = sqSelected

                    if result == "Successful Move":
                        moveMade = True
                        sqSelected = ()
                    elif gs.board[row][col] != "_":
                        Holding = True
                        dropped = False
                        sqSelected = Square
                    else:
                        sqSelected = ()

            elif e.type == p.MOUSEBUTTONUP:

                offset = None

                if not Holding:
                    continue

                Holding = False

                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                Square = (row, col)

                if sqSelected == Square:
                    if not dropped:
                        dropped = True
                    else:
                        sqSelected = ()
                    continue

                move = ChessEngine.Move(sqSelected, Square, gs.board)
                result = gs.makeMove(move)
                if result == "Successful Move":
                    moveMade = True
                    sqSelected = ()
                else:
                    dropped = True

            elif e.type == p.KEYDOWN:
                if e.key == p.K_r:
                    gs.undoMove()
                    sqSelected = ()
                    Holding = False
                    moveMade = True

        if moveMade:
            # validMoves = gs.getValidMoves()
            # gs.makeMove(random.choice(validMoves))
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs, my_font, sqSelected, Holding, offset)
        clock.tick(MAX_FPS)
        p.display.flip()

def attemptMove():
    pass


# Responsible for the graphics!
def drawGameState(screen, state, font, square, hold, offset):
    # Draw board first obviously goofball
    drawBoard(screen, state.board, square, hold)
    drawCoordinates(screen, font)

    if hold:
        drawHold(screen, state.board, offset, square)

def drawBoard(screen, board, square, hold):
    a, b = p.mouse.get_pos()
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

            # just overriding the colour because I'm lazy bones

            if (y, x) == square:
                colour = (246,245,123)
            p.draw.rect(screen, colour, p.Rect(x * SQ_SIZE, y * SQ_SIZE, SQ_SIZE, SQ_SIZE))

            d = (SQ_SIZE - PIECE_SIZE) / 2
            if hold and square == (y, x):
                continue
            if board[y][x] != "_":
                screen.blit(IMAGES[board[y][x]],
                            p.Rect(x * SQ_SIZE + d, y * SQ_SIZE + d, PIECE_SIZE, PIECE_SIZE))


def drawCoordinates(screen, font):
    colour = [(105, 135, 76), (230, 238, 210)]
    for i in range(DIMENSION):
        screen.blit(font.render(rowsToRanks[i], False, colour[i % 2]), p.Rect(3, 4 + i * SQ_SIZE, 6, 6))
        screen.blit(font.render(colsToFiles[i], False, colour[(i + 1) % 2]), p.Rect(55 + i * SQ_SIZE, 496, 6, 6))

def drawHold(screen, board, offset, sqSelected):
    a, b = p.mouse.get_pos()
    y, x = sqSelected
    d = PIECE_SIZE // 2
    # d = (PIECE_SIZE + 10) // 2
    g = time() * 3
    swing = HEIGHT // 64
    screen.blit(IMAGES[board[y][x]], # + "big"
                p.Rect(a - d + swing * math.cos(g), b - d + swing / 2 * math.sin(g), PIECE_SIZE, PIECE_SIZE))


if __name__ == "__main__":
    main()