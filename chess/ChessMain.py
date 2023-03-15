import pygame as p
from pygame import gfxdraw as gfd
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
    # Pygame stuff that I don't quite understand
    p.init()
    p.font.init()
    my_font = p.font.SysFont('OpenType', FONT_SIZE)
    p.display.set_caption("Chess")
    p.display.set_icon(p.image.load("chess/images/icon.png"))
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()

    validMoves, moveDict = gs.getValidMoves()
    moveMade = False  # Flag variable
    promotion = False

    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []  # Two tuples [0] being piece to move [1] being location

    Holding = False
    offset = None

    dropped = False
    displayedMoves = []
    highlight = []
    redHighlight = []
    colour = "W"
    start, end = (), ()
    kingLoc = ()

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:

                location = p.mouse.get_pos()

                if not promotion:
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
                        result = gs.makeMove(move, validMoves)

                        # If the move worked, that's great!
                        if result == "Successful Move":
                            moveMade = True
                            sqSelected = ()
                        # If it didn't work, if it's not to an empty square, select the new piece!
                        elif result == "Promotion":
                            promotion = True
                            start, end = sqSelected, (row, col)
                            colour = "W" if gs.board[sqSelected[0]][sqSelected[1]].isupper() else "B"
                        elif gs.board[row][col] != "_":
                            Holding = True
                            dropped = False
                            sqSelected = Square
                        # Okay it's an empty square? Unselect.
                        else:
                            sqSelected = ()
                else: # promotion menu!!

                    # I think the move will be made in the promotion menu. When you make a selection,

                    startX = WIDTH // 4
                    x, y = location
                    if not (WIDTH // 4 < x < 3 * WIDTH // 4 and HEIGHT // 2 - HEIGHT // 16 < y < 9 * HEIGHT // 16):
                        promotion = False # 8 - 1 + 2
                        continue
                    moveMade = True
                    piece = (x - startX) // SQ_SIZE
                    g = ChessEngine.Move(start, end, gs.board)
                    g.id += str(piece)
                    gs.makeMove(g, validMoves)
                    promotion = False

            elif e.type == p.MOUSEBUTTONUP:

                if promotion:
                    continue

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
                result = gs.makeMove(move, validMoves)
                if result == "Successful Move":
                    moveMade = True
                    sqSelected = ()
                elif result == "Promotion":
                    promotion = True
                    colour = "W" if gs.board[sqSelected[0]][sqSelected[1]].isupper() else "B"
                    start, end = sqSelected, (row, col)
                else:
                    dropped = True

            elif e.type == p.KEYDOWN:
                if e.key == p.K_r:
                    gs.undoMove()
                    sqSelected = ()
                    Holding = False
                    moveMade = True

        if moveMade:
            # random robot. Very goofy when you try to undo moves
            # validMoves = gs.getValidMoves()
            # if validMoves:
            #     gs.makeMove(random.choice(validMoves), validMoves)

            if gs.move_log:
                lastMove = gs.move_log[-1]
                highlight = [(lastMove.sr, lastMove.sc), (lastMove.er, lastMove.ec)]
            else:
                highlight = []

            redHighlight = gs.checkProject(True)
            if redHighlight:
                print("Check!")
                if gs.white_to_move:
                    kingLoc = gs.whiteKingLocation
                else:
                    kingLoc = gs.blackKingLocation

            validMoves, moveDict = gs.getValidMoves()
            moveMade = False

        # Probably a bad sign if I'm stacking this many damn parameters but saul good because I'm a master navigator
        drawGameState(screen, gs, my_font, sqSelected, Holding, offset, highlight, redHighlight, promotion, colour, moveDict, kingLoc)
        clock.tick(MAX_FPS)
        p.display.flip()


# Responsible for the graphics!
def drawGameState(screen, state, font, square, hold, offset, highlight, redHighlight, promotion, colour, moveDict, kingLoc):
    # Promotion is an interrupting game state. I don't know how to think about it.
    if not promotion:
        # Draw board first obviously goofball. Don't draw what's being held. That ain't your job funct.
        drawBoard(screen, state.board, square, hold, highlight, redHighlight, moveDict, kingLoc)
        drawCoordinates(screen, font)

        # If something is being held, draw it mate! Haha mate good pun.
        if hold:
            drawHold(screen, state.board, offset, square)

    else:
        drawPromotionMenu(screen, colour)


def drawBoard(screen, board, square, hold, highlight, redHighlight, moveDict, kingLoc):
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
            moveCol = [(207, 217, 182), (95, 125, 67)][(y + x) % 2]
            if (y, x) in [square] + highlight:
                colour = [(246,245,123), (212, 219, 127)][(y + x) % 2]
                moveCol = [(230, 230, 108), (194, 201, 113)][(y + x) % 2]
            # elif (y, x) in highlight: # In case I want to make a different colour for moves
            #     colour = [(246,245,123), (212, 219, 127)][(y + x) % 2]

            # if (y, x) in redHighlight:
            #     colour = [(194, 35, 35), (194, 35, 35)][(y + x) % 2]
            #     moveCol = [(173, 31, 31), (176, 26, 26)][(y + x) % 2]
            # I don't really like the red highlight. I might enable it later but it doesn't look that good.
            # Instead the king will be highlighted red.
            if redHighlight and (y, x) == kingLoc:
                colour = [(194, 35, 35), (194, 35, 35)][(y + x) % 2]
                moveCol = [(173, 31, 31), (176, 26, 26)][(y + x) % 2]

            p.draw.rect(screen, colour, p.Rect(x * SQ_SIZE, y * SQ_SIZE, SQ_SIZE, SQ_SIZE))

            if (y, x) in moveDict[square]:
                if board[y][x] == "_":
                    # p.draw.circle(screen, moveCol, ((x + 1/2) * SQ_SIZE, (y + 1/2) * SQ_SIZE), SQ_SIZE//6)
                    gfd.filled_circle(screen, int((x + 1 / 2) * SQ_SIZE), int((y + 1 / 2) * SQ_SIZE), SQ_SIZE // 6, moveCol)
                    gfd.aacircle(screen, int((x + 1 / 2) * SQ_SIZE), int((y + 1 / 2) * SQ_SIZE), SQ_SIZE // 6, moveCol)

                else:
                    p.draw.circle(screen, moveCol, ((x + 1 / 2) * SQ_SIZE, (y + 1 / 2) * SQ_SIZE), SQ_SIZE // 2, width=6)
                    gfd.aacircle(screen, int((x + 1 / 2) * SQ_SIZE), int((y + 1 / 2) * SQ_SIZE), SQ_SIZE // 2, moveCol)
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


def drawPromotionMenu(screen, pieceColour):
    colour = (105, 135, 76)
    p.draw.rect(screen, colour, p.Rect(WIDTH // 4 - 5, HEIGHT // 2 - HEIGHT // 16 - 5, WIDTH // 2 + 10, HEIGHT // 8 + 10),
                border_top_left_radius=4, border_top_right_radius=4,
                border_bottom_left_radius=4, border_bottom_right_radius=4)
    colour = (230, 238, 210)
    p.draw.rect(screen, colour, p.Rect(WIDTH // 4, HEIGHT // 2 - HEIGHT // 16, WIDTH // 2, HEIGHT // 8),
                border_top_left_radius=4, border_top_right_radius=4,
                border_bottom_left_radius=4, border_bottom_right_radius=4)
    options = ["q", "r", "b", "n"]
    for i in range(4):
        screen.blit(IMAGES[piecePlusColour[pieceColour + options[i]]],
                    p.Rect(WIDTH // 4 + i * SQ_SIZE + 2.5, HEIGHT // 2 - HEIGHT // 16 + 2.5, PIECE_SIZE, PIECE_SIZE))


if __name__ == "__main__":
    main()
