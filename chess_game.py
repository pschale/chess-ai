### Chess AI project
### basic game (no AI yet)

### Notes:
### main attribute of class (game_board.board) is an 8x8 numpy str array
### squares (variable s usually used) are tuples (file_index, rank_index), 
###     because game_board.board[s] works nicely
### set of squares are lists
### Algebraic notation is allowed, with function to translate (even with stuff like exd4 
###     or Bc4xNd3, but not BxN)
### For checking of legal moves, copies of self.board are made, then move is performed, 
###     then check for bad things (ie your king being in check)


import numpy as np


class game_board():

    def __init__(self, gametype='newgame'):
        #make empty board
        
        self.board = np.empty((8,8),dtype='str')
        self.board[:, :] = " "
        self.pawn_home = {'W': 1, 'B': 6}
        self.promotion_row = {'W': 7, 'B': 0}
        self.adv = {'W': 1, 'B': -1}
        self.home = {'W': 0, 'B': 7}

        #add pawns and kings
        if gametype=='newgame':
            self.can_castle = {'W': True, 'B': True}
            self.white_tomove = True
                                    
            self.board[:, 1] = 'P'
            self.board[[2, 5], [0, 0]] = 'B'
            self.board[[1, 6], [0, 0]] = 'N'
            self.board[[0, 7], [0, 0]] = 'R'
            self.board[3, 0] = 'Q'
            self.board[4, 0] = 'K'
        
            self.board[:, 6] = 'p'
            self.board[[2, 5], [7, 7]] = 'b'
            self.board[[1, 6], [7, 7]] = 'n'
            self.board[[0, 7], [7, 7]] = 'r'
            self.board[3, 7] = 'q'
            self.board[4, 7] = 'k'
        
    def copy(self):
        gamecopy = game_board()
        gamecopy.board = np.copy(self.board)
        return gamecopy
        
    def __str__(self):
        # sorry that this looks awful
        return "\n".join(['| ' + ' | '.join(list(self.board[:, i])) for i in range(7, -1, -1)])
    
    def get_all_color_pieces(self, color):
        assert color in ['W', 'B']
        if color == 'W':
            inds = np.where(np.isin(self.board, ['Q', 'K', 'N', 'R', 'B', 'P']))
        else:
            inds = np.where(np.isin(self.board, ['q', 'k', 'n', 'r', 'b', 'p']))
    
        return [(inds[0][i], inds[1][i]) for i in range(len(inds[0]))]
        
    def get_kingloc(self, color):
        p = 'K' if color == 'W' else 'k'
        kingloc = np.where(self.board == p)
        return (kingloc[0][0], kingloc[1][0])
    
    def check_check(self, color):
        #color is the color of the possibly threatened king
        kingloc = self.get_kingloc(color)
        assert color in ['W', 'B']
        pieces = self.get_all_color_pieces('W' if color == 'B' else 'B')
        target_locs = []
        for pieceloc in pieces:
            target_locs+= self.find_legal_moves(pieceloc)
        return kingloc in target_locs
            
    def move(self, move, verb=False): # this takes algebraic moves
        color = 'W' if self.white_tomove else 'B'
        
        if move=='0-0' or move == 'O-O':
            # add assertions to make sure this is legal move
            self.move_piece((4, self.home[color]), (6, self.home[color]))
            self.move_piece((7, self.home[color]), (5, self.home[color]))
        elif move == '0-0-0':
            # add assertions to make sure this is legal move
            self.move_piece((4, self.home[color]), (2, self.home[color]))
            self.move_piece((0, self.home[color]), (3, self.home[color]))
        else:
            # first, we need to figure out which square we're moving to
            endsquare = square_index(move[-2:]) #note this is not true for queen promotions
            if color == 'W':
                myp = 'P'
            else:
                myp = 'p'
            if len(move) == 2: #this is a simple pawn move
                # check if it's a pawn moving two spaces
                if (endsquare[1] == self.pawn_home[color] + 2*self.adv[color]) and self.board[endsquare[0], self.pawn_home[color]+self.adv[color]] == ' ':
                    assert self.board[endsquare[0], self.pawn_home[color]] == myp
                    self.move_piece((endsquare[0], self.pawn_home[color]), endsquare)
                else:
                    assert self.board[endsquare[0], endsquare[1] - self.adv[color]] == myp
                    assert self.board[endsquare] == ' '
                    self.move_piece((endsquare[0], endsquare[1] - self.adv[color]), endsquare)
            elif '=' in move: #pawn promotion
                endsquare = square_index(move[-3:-1])
                startsquare = (endsquare[0], endsquare[1] - adv)
                assert self.board[startsquare] == myp
                self.move_piece(endsquare, startsquare)
                self.board[endsquare] = move[-1]
                if color == 'B':
                    self.board[endsquare] = self.board(endsquare).lower()
                #pawn promoting
            elif move[0] in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']: #pawn capturing
                startsquare = (['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].index(move[0]), endsquare[1] - self.adv[color])
                assert self.board[startsquare] == myp
                self.move_piece(startsquare, endsquare)
            
            else:
                # 2 special cases: capturing, and need for specification
                p = move[0] if color=='W' else move[0].lower() #name of piece
                
                if 'x' in move:
                    assert not self.find_color(endsquare) == color
                    #en passant will fail here
                
                #find locations with this piece; this is 2nd array because np.where is weird
                locs = np.where(self.board == p)
                locs = [(locs[0][i], locs[1][i]) for i in range(len(locs[0]))]
                
                legal_pieces = []
                for loc in locs:
                    legal_moves = self.find_legal_moves(loc)
                    if endsquare in legal_moves:
                        legal_pieces.append(loc)    
                
                if len(legal_pieces) == 1:
                    startsquare = legal_pieces[0]
                elif not move[1:-2]:
                    raise
                else:
                    info = move[1:-2]
                    legal_pieces_locnames = [square_name(ele) for ele in legal_pieces]
                    scores = [0 for ele in legal_pieces_locnames]
                    for character in info:
                        for i in range(len(legal_pieces_locnames)):
                            scores[i] += 1 if character in legal_pieces_locnames[i] else 0
                    startsquare = legal_pieces[scores.index(max(scores))]
 
                self.move_piece(startsquare, endsquare)
        self.white_tomove = not self.white_tomove
        if verb:
            print(self)
        
        game_status = self.game_over()
        if game_status[0]:
            print('Game over: white scores ' + str(game_status[1]))
            
    def play_game(self, list_of_moves):
        for m in list_of_moves:
            m = m.replace('+', '')
            m = m.replace('#', '')
            self.move(m)
        print(self)
    
    
    def game_over(self):
        color_tomove = 'W' if self.white_tomove else 'B'
        if len(self.find_all_legal_moves(color_tomove)) == 0:
            if self.check_check(color_tomove):
                #checkmate
                return True, 0 if self.white_tomove else 1
            else:
                return True, 0.5
        else:
            # conditions for draw should go here
            return False, None
                
    def castle(self, color, side): #side is '0-0' or '0-0-0'
        hr = 0 if color == 'W' else 'B'
        assert side in ['0-0', '0-0-0']
        if side == '0-0':
            self.move_piece((4, hr), (6, hr))
            self.move_piece((7, hr), (5, hr))
        else:
            self.move_piece((4, hr), (2, hr))
            self.move_piece((0, hr), (3, hr))
        self.can_castle[color] = False

    def find_color(self, s):
        assert not self.board[s] == ' '
        color = 'W' if self.board[s].isupper() else 'B'
        return color
                    
    def find_legal_moves(self, s):
        p = self.board[s]
        color = 'W' if p.isupper() else 'B'
        p = p.lower()
        if p == 'q':
            return self.find_queenmoves(s, color)
        elif p == 'b':
            return self.find_diagonals(s, color)
        elif p == 'r':
            return self.find_rookmoves(s, color)
        elif p == 'k':
            return self.find_kingmoves(s, color)
        elif p == 'n':
            return self.find_knightmoves(s, color)
        elif p == 'p':
            return self.find_pawnmoves(s, color)
            
    def legal_move(self, startsquare, endsquare, color):
            newboard = self.copy()
            newboard.move_piece(startsquare, endsquare)
            return not newboard.check_check(color)
            
    def find_legal_moves_check_check(self, s, color):
        all_moves = self.find_legal_moves(s)
        legal_moves = [[s, move] for move in all_moves if self.legal_move(s, move, color)]
        return legal_moves
        
    def find_all_legal_moves(self, color):
        # this does not yet include en passant
        pieces = self.get_all_color_pieces(color) #list of piece locations (tuples)
        
        all_legal_moves = []
        
        for p in pieces:
            all_legal_moves += self.find_legal_moves_check_check(p, color)
            
        #look for castling
        if self.can_castle[color]:
            castle_moves = self.check_castling(color)

            all_legal_moves+=castle_moves
        return all_legal_moves
            
    def find_all_next_board_positions(self, color):
        #first we get the legal moves. For most moves, next board position will be obvious
        legal_moves = self.find_all_legal_moves(color)
        possible_boards = []
        for move in legal_moves: #a move is a list of 2 board positions (tuples)
            # castling
            next_position = self.copy()
            if move in ['0-0', '0-0-0']:
                next_position.castle(color, move)
            elif self.board[move[0]].lower() == 'p' and move[1][1] == self.promotion_row[color]:
                next_position.move_piece(move[0], move[1])#pawn promotion
                next_position.board[move[1]] = 'Q' if color == 'W' else 'q' # can only go to queen for now
            else:
                next_position.move_piece(move[0], move[1])
                
            possible_boards.append(next_position)
        return possible_boards
            
    def check_castling(self, color):
        hr = 0 if color == 'W' else 7
        
        castling_moves = []
        
        k_castle_squares = [(4+i, hr) for i in range(4)]
        q_castle_squares = [(i, hr) for i in range(5)]
        #this conditional check if pieces between K and h-rook are open
        # then checks if any of those squares are threatened by other color
        if (np.all(self.board[[5, 6], [hr, hr]] == ' ') and
            np.all([not self.is_threatened(x, color) for x in 
                k_castle_squares])):
            # that means we can kingside castle
            castling_moves.append('0-0')
        
        if (np.all(self.board[[1, 2, 3], [hr, hr, hr]] == ' ') and
            np.all([not self.is_threatened(x, color) for x in 
                q_castle_squares])):            
            castling_moves.append('0-0-0')
        return castling_moves
        
    def is_threatened(self, s, color):
        #find if a square is threatened by other color (used to see if castling is possible)
        assert color in ['W', 'B']
        pieces = self.get_all_color_pieces('W' if color == 'B' else 'B')
        target_locs = []
        for pieceloc in pieces:
            target_locs+= self.find_legal_moves(pieceloc)
        return s in target_locs
            
    def find_diagonals(self, s, color):

        # go along each diagonal
        urs = [(s[0] + i, s[1] + i) for i in range(1, min(7-s[0], 7-s[1]) + 1)]
        uls = [(s[0] - i, s[1] + i) for i in range(1, min(s[0], 7-s[1]) + 1)]
        drs = [(s[0] + i, s[1] - i) for i in range(1, min(7-s[0], s[1]) + 1)]
        dls = [(s[0] - i, s[1] - i) for i in range(1, min(s[0], s[1]) + 1)]
        
        moves = [urs, uls, drs, dls]
        stop_index = [-1,-1,-1,-1]
        for i in range(len(moves)):
            for j in range(len(moves[i])):
                if self.board[moves[i][j]] == ' ':
                    stop_index[i] = j
                elif not self.find_color(moves[i][j]) == color:
                    stop_index[i] = j
                    break
                else:
                    break

        open_moves = [moves[i][:stop_index[i]+1] for i in range(4)]
        open_moves = [item for sublist in open_moves for item in sublist]
        open_moves = [ele for ele in open_moves if ele]
                
        return open_moves


    def find_rookmoves(self, s, color):

        # go along each path all the way to the edge of the board
        u = [(s[0], s[1] + i) for i in range(1, 7-s[1] + 1)]
        d = [(s[0], s[1] - i) for i in range(1, s[1] + 1)]
        l = [(s[0] - i, s[1]) for i in range(1, s[0] + 1)]
        r = [(s[0] + i, s[1]) for i in range(1, 7-s[0] + 1)]

        moves = [u, d, l, r]
        stop_index = [-1,-1,-1,-1]
        # loop over each diagonal, go until a piece is blocking
        # if the piece is the other color, it can be captured
        for i in range(len(moves)):
            for j in range(len(moves[i])):
                if self.board[moves[i][j]] == ' ':
                    stop_index[i] = j
                elif not self.find_color(moves[i][j]) == color:
                    stop_index[i] = j
                    break
                else:
                    break

        open_moves = [moves[i][:stop_index[i]+1] for i in range(4)]
        open_moves = [item for sublist in open_moves for item in sublist]
        open_moves = [ele for ele in open_moves if ele]
                        
        return open_moves

    def find_knightmoves(self, s, color):

        moves = [(s[0] + 2, s[1] + 1),
                 (s[0] - 2, s[1] + 1),
                 (s[0] + 2, s[1] - 1),
                 (s[0] - 2, s[1] - 1),
                 (s[0] + 1, s[1] + 2),
                 (s[0] - 1, s[1] + 2),
                 (s[0] + 1, s[1] - 2),
                 (s[0] - 1, s[1] - 2)]

        legal_moves = [m for m in moves if (m[0]>=0 and m[0]<8 and m[1]>=0 and m[1]<8) and (not self.find_color(m)==color)]
    
        return legal_moves
        
    def find_queenmoves(self, square, color):
    
        return self.find_rookmoves(square, color) + self.find_diagonals(square, color)
        
    def find_kingmoves(self, s, color):
        
        moves = [(s[0]+1, s[1]+1),
                 (s[0]+1, s[1]),
                 (s[0]+1, s[1]-1),
                 (s[0], s[1]+1),
                 (s[0], s[1]-1),
                 (s[0]-1, s[1]+1),
                 (s[0]-1, s[1]),
                 (s[0]-1, s[1]-1)]
        legal_moves = [m for m in moves if (m[0]>=0 and m[0]<8 and m[1]>=0 and m[1]<8) and (not self.find_color(m)==color)]
    
        return legal_moves
        
    def find_pawnmoves(self, s, color):

        adv = 1 if color == 'W' else -1
        ocolor = 'W' if color == 'B' else 'B'
        legal_moves = []
        startrank = 1 if color == 'W' else 6
        
        if self.board[s[0], s[1] + adv] == ' ':
            legal_moves.append((s[0], s[1] + adv))
            if s[1] == startrank and self.board[s[0], s[1] + 2*adv] == ' ':
                legal_moves.append((s[0], s[1]+2*adv))
        for i in [-1, 1]: #capturing diagonally - en passant not considered yet
            if (s[0] + i < 0) or (s[0] + i > 7):
                continue
            if self.find_color((s[0] + i, s[1] + adv)) == ocolor:
                legal_moves.append((s[0]+i, s[1]+adv))
        return legal_moves
        
    def find_color(self, s):
        if self.board[s] in ['P', 'Q', 'K', 'R', 'B', 'N']:
            return 'W'
        elif self.board[s] in ['p', 'q', 'k', 'r', 'b', 'n']:
            return 'B'
        else:  
            return None
            
    def move_piece(self, startsquare, endsquare):
        if self.board[startsquare].lower() == 'k':
            self.can_castle[self.find_color(startsquare)] = False
        self.board[endsquare] = self.board[startsquare]
        self.board[startsquare] = ' '
        
        
def square_index(squarename):
    assert len(squarename) is 2
    ranknum = int(squarename[1])
    filename = squarename[0]
    
    rankindex = ranknum - 1
    fileindex = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].index(filename)
    
    return (fileindex, rankindex)
    
def square_name(squareindex):

    filename = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'][squareindex[0]]
    ranknum = str(squareindex[1] + 1)
    return filename + ranknum

        
