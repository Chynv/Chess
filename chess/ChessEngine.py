from CONST import *


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

    def reset(self):
        board = unpack_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
        white_to_move = True
        self.move_log = []

    def makeMove(self, move):
        if move in self.getValidMoves():
            self.board[move.sr][move.sc] = "_"
            self.board[move.er][move.ec] = move.pieceMoved
            self.move_log.append(move)
            self.white_to_move = not self.white_to_move
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

    # Okay. A move is legal if it of course it moves properly and it doesn't end with you in check
    # If there are no moves that don't leave you in check you dead as hell lmao
    # If there are no moves and you're not in check it's a stalemate
    # I think to make it less computationally costly, I can project the moves from the king!
    # If it detects a knight in one knight move from itself it is IN CHECK!

    def getValidMoves(self):
        return self.getAllPossibleMoves()

    def getAllPossibleMoves(self):
        moves = []
        for y in range(8):
            for x in range(8):
                print(self.white_to_move)
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

    def projection(self, r, c, moves, direction):
        yDir, xDir = direction

        # just in case. Don't want no infinite loops baby bones
        if abs(yDir) + abs(xDir) == 0:
            return

        isWhite = self.board[r][c].isupper()
        mR, mC = r, c
        while True:
            mR += yDir
            mC += xDir
            if not (0 <= mR < 8 and 0 <= mC < 8):
                return
            if self.board[mR][mC] == "_":
                moves.append(Move((r, c), (mR, mC), self.board))
            else:
                if self.board[mR][mC].isupper() ^ isWhite:
                    moves.append(Move((r, c), (mR, mC), self.board))
                return


    def getPawnMoves(self, r, c, moves):
        if r == 0 or r == 7: # Bit of a shortcut that would break down in the case of variations but
            # you sacrifice generalisability for brevity
            return
        if self.white_to_move: # white pawn moves, duh
            # I should have kept their colour indicators in their names because underscore is a possiblity
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
        return self.colsToFiles[col] + self.rowsToRanks[row]