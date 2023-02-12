
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

    def reset(self):
        board = unpack_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
        white_to_move = 1
        self.move_log = []

    def makeMove(self, move):
        self.board[move.sr][move.sc] = "_"
        self.board[move.er][move.ec] = move.pieceMoved
        self.move_log.append(move)
        self.white_to_move *= -1

    def undoMove(self):
        if not self.move_log:
            return
        move = self.move_log.pop(-1)
        self.board[move.sr][move.sc] = move.pieceMoved
        self.board[move.er][move.ec] = move.pieceCaptured
        self.white_to_move *= -1

    # Okay. A move is legal if it of course it moves properly and it doesn't end with you in check
    # If there are no moves that don't leave you in check you dead as hell lmao
    # If there are no moves and you're not in check it's a stalemate
    # I think to make it less computationally costly, I can project the moves from the king!
    # If it detects a knight in one knight move from itself it is IN CHECK!

    def getValidmoves(self, ):
        return self.getAllPossibleMoves()

    def getAllPossibleMoves(self):
        moves = [Move((6, 4), (4, 4), self.board)]

        for y in range(8):
            for x in range(8):
                if self.board[y][x].islower() ^ self.white_to_move:
                    continue
                piece = self.board[y][x].lower()
                pass
        return moves



class Move:

    ranksToRows = {'8': 0, '7': 1, '6': 2, '5': 3, '4': 4, '3': 5, '2': 6, '1': 7}
    rowsToRanks = {j: i for i, j in ranksToRows.items()}
    filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    colsToFiles = {j: i for i, j in filesToCols.items()}
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
