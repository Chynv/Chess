from CONST import *
import random

def unpack_fen(fen_string):
    board = [["_" for _ in range(8)] for _ in range(8)]
    pos = 0
    for i in fen_string:
        if i in "12345678":
            pos += int(i)
        elif i != "/":
            board[pos // 8][pos % 8] = i
            pos += 1
    return board


class GameState:
    def __init__(self):
        self.board = unpack_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
        self.white_to_move = True
        self.move_log = []
        self.moveFunctions = {
            "p": self.getPawnMoves,
            "r": self.getRookMoves,
            "b": self.getBishopMoves,
            "q": self.getQueenMoves,
            "k": self.getKingMoves,
            "n": self.getKnightMoves
        }
        # Perhaps for the sake of good code I should do len(self.board), but that conflicts with my OCD ADHD
        # I'm running through to check because the fen might be different.

        self.whiteKingLocation = ()
        self.blackKingLocation = ()

        for tRow in range(8):
            for tCol in range(8):
                if self.board[tRow][tCol] == "K":
                    if self.whiteKingLocation == ():
                        self.whiteKingLocation = (tRow, tCol)
                        print(self.whiteKingLocation)
                    else:
                        raise "Only one white king. This ain't 5D chess."
                elif self.board[tRow][tCol] == "k":
                    if self.blackKingLocation == ():
                        self.blackKingLocation = (tRow, tCol)
                        print(self.blackKingLocation)
                    else:
                        raise "Only one black king. This ain't 5D chess."

    def reset(self):
        self.board = unpack_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
        self.white_to_move = True
        self.move_log = []

    def makeMove(self, move, validMoves):
        if move in validMoves:
            self.board[move.sr][move.sc] = "_"
            self.board[move.er][move.ec] = move.pieceMoved
            self.move_log.append(move)

            if self.white_to_move:
                col = "W"
            else:
                col = "B"

            self.white_to_move = not self.white_to_move

            if move.pieceMoved == "K":
                self.whiteKingLocation = (move.er, move.ec)
            elif move.pieceMoved == "k":
                self.blackKingLocation = (move.er, move.ec)
            print(move.pieceMoved, piecePlusColour[col + "p"])
            if move.pieceMoved == piecePlusColour[col + "p"] and (move.er == 7 or move.er == 0):
                self.board[move.er][move.ec] = piecePlusColour[col + "q"]

            return "Successful Move"
        else:
            return "Failed Move"

    def undoMove(self):
        if not self.move_log:
            return
        move = self.move_log.pop(-1)
        self.board[move.sr][move.sc] = move.pieceMoved
        self.board[move.er][move.ec] = move.pieceCaptured
        self.white_to_move = not self.white_to_move
        if move.pieceMoved == "K":
            self.whiteKingLocation = (move.sr, move.sc)
        elif move.pieceMoved == "k":
            self.blackKingLocation = (move.sr, move.sc)

    # Okay. A move is legal if it of course it moves properly and it doesn't end with you in check
    # If there are no moves that don't leave you in check you dead as hell lmao
    # If there are no moves and you're not in check it's a stalemate
    # I think to make it less computationally costly, I can project the moves from the king!
    # If it detects a knight in one knight move from itself it is IN CHECK! Coolio

    def getValidMoves(self):
        moves = []
        for move in self.getAllPossibleMoves():
            # Kind of a back track. Change the board and then check a condition and then change it back.
            # This will need to be modified when en passant and castling are implemented.
            self.board[move.sr][move.sc] = "_"
            self.board[move.er][move.ec] = move.pieceMoved

            if move.pieceMoved == "K":
                self.whiteKingLocation = (move.er, move.ec)
            elif move.pieceMoved == "k":
                self.blackKingLocation = (move.er, move.ec)

            if not self.checkProject():
                moves.append(move)
            self.board[move.sr][move.sc] = move.pieceMoved
            self.board[move.er][move.ec] = move.pieceCaptured

            if move.pieceMoved == "K":
                self.whiteKingLocation = (move.sr, move.sc)
            elif move.pieceMoved == "k":
                self.blackKingLocation = (move.sr, move.sc)
        if len(moves) == 0:
            if self.white_to_move:
                r, c = self.whiteKingLocation
            else:
                r, c = self.blackKingLocation

            if self.checkProject():
                # Goofiest code you've ever done seen in your damn life
                print("checkmate" + " %s wins" % ["white", "black"][int(self.white_to_move)])
            else:
                print("stalemate")

        return moves

    def getAllPossibleMoves(self):
        moves = []
        for y in range(8):
            for x in range(8):
                # If it's black it's lowercase
                # Black and white's turn
                # True ^ True = False
                # False ^ False = False
                # True ^ False = True
                if self.board[y][x].isupper() ^ self.white_to_move:
                    continue
                piece = self.board[y][x].lower()
                if piece == "_":
                    continue
                self.moveFunctions[piece](y, x, moves)
        return moves

    def projection(self, r, c, moves, direction, target=False):
        yDir, xDir = direction

        # just in case. Don't want no infinite loops
        if abs(yDir) + abs(xDir) == 0:
            return

        isWhite = self.board[r][c].isupper()
        mR, mC = r, c
        while True:
            mR += yDir
            mC += xDir
            if not (0 <= mR < 8 and 0 <= mC < 8):
                return "_"
            if self.board[mR][mC] == "_":
                if not target:
                    moves.append(Move((r, c), (mR, mC), self.board))
            else:
                if self.board[mR][mC].isupper() ^ isWhite:
                    if not target:
                        moves.append(Move((r, c), (mR, mC), self.board))
                    else:
                        return mR, mC
                return "_"

    def getPawnMoves(self, r, c, moves):
        if r == 0 or r == 7: # Bit of a shortcut that would break down in the case of variations but
            # you sacrifice generalisability for brevity
            return
        if self.white_to_move: # white pawn moves, duh
            # I should have kept their colour indicators in their names because underscore is a possibility
            # So I gotta do something goofy like this!!! I know this code is forbidden!!! :(
            # Also I wanted to use FEN notation (just for the pieces) because it's cute as
            if self.board[r - 1][c] == "_":
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "_":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c > 0 and self.board[r - 1][c - 1].islower() and self.board[r - 1][c - 1] != "_":
                moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c < 7 and self.board[r - 1][c + 1].islower() and self.board[r - 1][c + 1] != "_":
                moves.append(Move((r, c), (r - 1, c + 1), self.board))
        else: # This code hurts my heart and when I implement en passant it may bite me
            if self.board[r + 1][c] == "_":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "_":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c > 0 and self.board[r + 1][c - 1].isupper() and self.board[r + 1][c - 1] != "_":
                moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c < 7 and self.board[r + 1][c + 1].isupper() and self.board[r + 1][c + 1] != "_":
                moves.append(Move((r, c), (r + 1, c + 1), self.board))

    #  Look at that code. So tasteful in its brevity. Three lines for a rook, three lines for a bishop and three
    #  lines for a queen. Oh my god, it even has my watermark.

    def getRookMoves(self, r, c, moves):
        for dir_ in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            self.projection(r, c, moves, dir_)

    def getBishopMoves(self, r, c, moves):
        for dir_ in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            self.projection(r, c, moves, dir_)

    def getQueenMoves(self, r, c, moves):
        for dir_ in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            self.projection(r, c, moves, dir_)

    def getKnightMoves(self, r, c, moves):
        isWhite = self.board[r][c].isupper()
        for a, b in [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]:
            nR = a + r
            nC = b + c
            if not(0 <= nR < 8 and 0 <= nC < 8):
                continue
            if self.board[nR][nC] == "_":
                moves.append(Move((r, c), (nR, nC), self.board))
            else:
                if self.board[nR][nC].isupper() ^ isWhite:
                    moves.append(Move((r, c), (nR, nC), self.board))

    # holy shit I actually made all of that really quickly. Super proud of myself rn lol (10 Mar 2023)

    def getKingMoves(self, r, c, moves):
        isWhite = self.board[r][c].isupper()
        for a, b in [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]:
            nR = a + r
            nC = b + c
            if not (0 <= nR < 8 and 0 <= nC < 8):
                continue
            if self.board[nR][nC] == "_":
                moves.append(Move((r, c), (nR, nC), self.board))
            else:
                if self.board[nR][nC].isupper() ^ isWhite:
                    moves.append(Move((r, c), (nR, nC), self.board))

    def checkProject(self, retHighlight = False):

        flag = False
        # I'll set it to True if I encounter something checking the current king. I don't want to return
        # immediately because I want to get all checkers in case of a double check. I don't think
        # more than two checks are possible at once so I might implement something to check that I already
        # have two things checking so I don't have to continue searching but it's also a very
        # unlikely scenario in the first place so I wouldn't save much time.

        seen = []
        # I don't think it needs to be a set because if a queen checks like a rook it won't check like a bishop

        if self.white_to_move:
            col = "B"
            r, c = self.whiteKingLocation
        else:
            col = "W"
            r, c = self.blackKingLocation

        # Project knight moves from king. If knight of opposite colour detected, return True
        for a, b in [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]:
            nR = a + r
            nC = b + c
            if not (0 <= nR < 8 and 0 <= nC < 8):
                continue
            if self.board[nR][nC] == piecePlusColour[col + "n"]:
                # return True
                seen.append((nR, nC))
                flag = True

        # bishop & queen
        for dir_ in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            coordsCollided = self.projection(r, c, [], dir_, True)
            if coordsCollided == "_":
                continue
            nR, nC = coordsCollided
            pieceCollidedWith = self.board[nR][nC]
            if pieceCollidedWith in piecePlusColour[col + "q"] + piecePlusColour[col + "b"]:
                # return True
                seen.append((nR, nC))
                flag = True

        # rook & queen
        for dir_ in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            coordsCollided = self.projection(r, c, [], dir_, True)
            if coordsCollided == "_":
                continue
            nR, nC = coordsCollided
            pieceCollidedWith = self.board[nR][nC]
            if pieceCollidedWith in piecePlusColour[col + "q"] + piecePlusColour[col + "r"]:
                # return True
                seen.append((nR, nC))
                flag = True

        # Pawns! They only ever attack adjacently diagonally and their direction remains the same. I can
        # do a neat little trick with that fact by projecting from te king based upon who's turn it is
        # nice and succinctly.

        for a, b in [(1 - 2 * int(self.white_to_move), -1), (1 - 2 * int(self.white_to_move), 1)]:
            nR = a + r
            nC = b + c
            if not (0 <= nR < 8 and 0 <= nC < 8):
                continue
            if self.board[nR][nC] == piecePlusColour[col + "p"]:
                # return True
                seen.append((nR, nC))
                flag = True

        # King!!
        for a, b in [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]:
            nR = a + r
            nC = b + c
            if not (0 <= nR < 8 and 0 <= nC < 8):
                continue
            if self.board[nR][nC] == piecePlusColour[col + "k"]:
                # return True
                seen.append((nR, nC))
                # you will never red highlight the king so no need to flag it. You will only ever need to check
                # for it when you make a move to make sure that your king does not fall within an attacked square
                # by the enemy king. I'm not sure if this is bad programming practise but it feels right
                return True

        if retHighlight:
            return seen
        else:
            return flag


class Move:
    def __init__(self, startSq, endSq, board):
        # start row, start column, end row, end column just shortened a little for brevity's sake
        self.sr, self.sc = startSq
        self.er, self.ec = endSq
        self.pieceMoved = board[self.sr][self.sc]
        self.pieceCaptured = board[self.er][self.ec]

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.sr == other.sr and self.sc == other.sc and self.er == other.er and self.ec == other.ec
        return False

    def getChessNotation(self):
        return self.getRankFile(self.sr, self.sc) + self.getRankFile(self.er, self.ec)

    def getRankFile(self, row, col):
        return colsToFiles[col] + rowsToRanks[row]
