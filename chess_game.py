### Chess AI project
### basic game (no AI yet)

### Notes:
### main attribute of class (game_board.board) is an 8x8 numpy str array
### square locations (variable s usually used) are tuples (file_index, rank_index), 
###     because game_board.board[s] works nicely
### set of square locations are lists
### Algebraic notation is allowed, with function to translate (even with stuff like exd4 
###     or Bc4xNd3, but not BxN)
### For checking of legal moves, copies of self.board are made, then move is performed, 
###     then check for bad things (ie your king being in check)


import numpy as np
from copy import deepcopy


class game_board():

    def __init__(self, gametype='newgame', csvstr = None, do_threats=True):
        #make empty board
        
        self.board = np.empty((8,8),dtype='str')
        self.cboard = np.zeros((8,8),dtype='str')
        self.board[:, :] = " "
        self.pawn_home = {'W': 1, 'B': 6}
        self.promotion_row = {'W': 7, 'B': 0}
        self.adv = {'W': 1, 'B': -1}
        self.home = {'W': 0, 'B': 7}
        self.en_passantable_square = None
        self.wthreats = np.empty((8,8), dtype='int8')
        self.bthreats = np.empty((8,8), dtype='int8')
        
        #add pawns and kings
        if gametype=='newgame':
            self.can_castle = {'W': {'kingside': True, 'queenside': True}, 
                               'B': {'kingside': True, 'queenside': True}}
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
        elif gametype=='blank':
            print("Blank board created. White to move, and no castling available")
            self.can_castle = {'W': {'kingside': False, 'queenside': False}, 
                               'B': {'kingside': False, 'queenside': False}} 
            self.white_tomove = True
        else:
            self.board = csvstr[:64].reshape(8,8)
            self.can_castle = {'W': {'kingside': csvstr[65], 'queenside': csvstr[66]}, 
                               'B': {'kingside': csvstr[67], 'queenside': csvstr[68]}}
            self.white_tomove = csvstr[64]
        #if do_threats:
        #    self.full_update_threats()
    
    def update_cboard(self):
        self.cboard[np.isin(self.board, ['Q', 'K', 'R', 'B', 'N', 'P'])] = 'W'
        self.cboard[np.isin(self.board, ['q', 'k', 'r', 'b', 'n', 'p'])] = 'B'
        
    def remove_piece(self, s, color, dothreats=True):
        p = self.board[s]
        if dothreats:
            moves = self.find_threats_from_piece(s, color)
            if color == 'B':
                for m in moves:
                    self.bthreats[m[1]] -= 1
            else:
                for m in moves:
                    self.wthreats[m[1]] -= 1
        self.board[s] = ' '
        return p
        
    def add_piece(self, s, p, color, dothreats=True):
        self.board[s] = p
        if dothreats:
            moves = self.find_threats_from_piece(s, color)
            if color == 'B':
                for m in moves:
                    self.bthreats[m[1]] += 1
            else:
                for m in moves:
                    self.wthreats[m[1]] += 1

    def __str__(self):
        # sorry that this looks awful, this prints out the gameboard
        return "\n".join(['| ' + ' | '.join(list(self.board[:, i])) for i in range(7, -1, -1)])
          
    def move(self, move, verb=False): # this takes algebraic moves
        # cases we have to deal with, in the order we do them:
        # castling (queenside and kingside)
        # pawn promotions - there's an '=' in the string (eg e8=Q or h8=N for white, b1=Q or f1=N for black), can include capture
        # pawn move - eg d5 (sometimes advancing two squares)
        # pawn capture - eg dxe5, including en passant (no checking on if it's totally legal yet, though)
        # piece move, captures (Nf3, Nxf3, Nef3, etc).
        if self.white_tomove:
            color = 'W'
            myp = 'P'
            otherp = 'p'
        else:
            color = 'B'
            myp = 'p'
            otherp = 'P'

        if move in ['0-0', 'O-O', '0-0-0', 'O-O-O']:
            self.castle(color, move)
        #if move=='0-0' or move == 'O-O':
        #    assert self.can_castle[color]['kingside']
        #    self.move_piece((4, self.home[color]), (6, self.home[color]), color)
        #    self.move_piece((7, self.home[color]), (5, self.home[color]), color)
        #    self.can_castle[color]['kingside'] = False
        #elif move == '0-0-0' or move == 'O-O-O':
        #    assert self.can_castle[color]['queenside']
        #    self.move_piece((4, self.home[color]), (2, self.home[color]), color)
        #    self.move_piece((0, self.home[color]), (3, self.home[color]), color)
        #    self.can_castle[color]['queenside'] = False
        elif '=' in move:
            endsquare = square_index(move[-4:-2]) #last two characters will be =Q, =N, etc
            if 'x' in move: #pawn promotion via capture
                startsquare = square_index(move[0] + str(endsquare[1] - self.adv[color]+1))
            else:
                startsquare = (endsquare[0], endsquare[1] - self.adv[color])
            assert self.board[startsquare] == myp
            self.move_piece(startsquare, endsquare, color, dothreats=False)
            self.board[endsquare] = move[-1]
            self.full_update_threats()
            if color == 'B':
                self.board[endsquare] = self.board[endsquare].lower()
        else:
            # first, we need to figure out which square we're moving to
            endsquare = square_index(move[-2:])

            if len(move) == 2: #this is a simple pawn move
                # check if it's a pawn moving two spaces
                if (endsquare[1] == self.pawn_home[color] + 2*self.adv[color] 
                        and self.board[endsquare[0], self.pawn_home[color]+self.adv[color]] == ' '):
                    assert self.board[endsquare[0], self.pawn_home[color]] == myp
                    self.move_piece((endsquare[0], self.pawn_home[color]), endsquare, color)
                    #add en passant eligibility if applicable
                    if (self.board[min(endsquare[0]+1, 7), endsquare[1]] == otherp 
                            or self.board[max(endsquare[0]-1, 0), endsquare[1]] == otherp):
                        self.en_passantable_square = endsquare

                else:
                    assert self.board[endsquare[0], endsquare[1] - self.adv[color]] == myp
                    assert self.board[endsquare] == ' '
                    self.move_piece((endsquare[0], endsquare[1] - self.adv[color]), endsquare, color)

            elif move[0] in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']: #pawn capturing
                startsquare = (['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].index(move[0]), endsquare[1] - self.adv[color])
                assert self.board[startsquare] == myp
                if self.board[endsquare] == ' ': #en passant
                    assert (endsquare[0], endsquare[1]-self.adv[color]) == self.en_passantable_square
                    self.board[(endsquare[0], endsquare[1] - self.adv[color])] = ' '
                self.move_piece(startsquare, endsquare, color)
            
            else:
                # 2 special cases: capturing, and need for specification
                p = move[0] if color=='W' else move[0].lower() #name of piece
                
                if 'x' in move:
                    assert not self.find_color(endsquare) == color
                    #en passant will fail here
                
                #find locations with this piece; this is 2nd array because np.where is weird
                locs = np.where(self.board == p)
                locs = [(locs[0][i], locs[1][i]) for i in range(len(locs[0]))]
                
                #find which of those pieces can move to the square in question
                legal_pieces = []
                for loc in locs:
                    legal_moves = self.find_legal_moves(loc)
                    if endsquare in legal_moves:
                        if self.is_legal_move(loc, endsquare, color):
                            legal_pieces.append(loc)    
                
                # deal with what happens if more than one piece can move there
                if len(legal_pieces) == 1:
                    startsquare = legal_pieces[0]
                elif not move[1:-2]:
                    print(move)
                    raise
                else:
                    info = move[1:-2] # eg if move is "Nef3", this picks out "e", the file that the knight starts on
                    legal_pieces_locnames = [square_name(ele) for ele in legal_pieces]
                    scores = [0 for ele in legal_pieces_locnames]
                    for character in info:
                        for i in range(len(legal_pieces_locnames)):
                            scores[i] += 1 if character in legal_pieces_locnames[i] else 0
                    startsquare = legal_pieces[scores.index(max(scores))]
 
                self.move_piece(startsquare, endsquare, color)
        self.white_tomove = not self.white_tomove
        if verb:
            print(self)
        
        game_status = self.game_over()
        if game_status[0]:
            print('Game over: white scores ' + str(game_status[1]))
 
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
        return self.is_threatened(kingloc, color)
           
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
                return True, 2 if self.white_tomove else 0
            else:
                #stalemate
                return True, 1
        else:
            # conditions for draw should go here
            return False, None
                
    def castle(self, color, side): #side is '0-0' or '0-0-0'
        hr = 0 if color == 'W' else 7
        assert side in ['0-0', 'O-O', '0-0-0', 'O-O-O']
        legal_castling_moves = self.check_castling(color)
        if side in ['0-0', 'O-O']: #kingside
            assert '0-0' in legal_castling_moves
            self.move_piece((4, hr), (6, hr), color)
            self.move_piece((7, hr), (5, hr), color)
        else: #queenside
            assert '0-0-0' in legal_castling_moves
            self.move_piece((4, hr), (2, hr), color)
            self.move_piece((0, hr), (3, hr), color)
        self.can_castle[color]['kingside'] = False
        self.can_castle[color]['queenside'] = False

    def find_color(self, s):
        assert not self.board[s] == ' '
        color = 'W' if self.board[s].isupper() else 'B'
        return color
    
    # this function finds the positions that the piece on the named square can move to next
    # returns a list of board positions
    # does NOT check to make sure that this is truly legal (eg pinned pieces)
    # use find_legal_moves_check_check function for that                
    def find_legal_moves(self, s):
        p = self.board[s]
        color = 'W' if p.isupper() else 'B'
        p = p.lower()
        if p == 'q':
            return self.find_queen_moves(s, color, 'moves')
        elif p == 'b':
            return self.find_diagonal_moves(s, color, 'moves')
        elif p == 'r':
            return self.find_rook_moves(s, color, 'moves')
        elif p == 'k':
            return self.find_king_moves(s, color, 'moves')
        elif p == 'n':
            return self.find_knight_moves(s, color, 'moves')
        elif p == 'p':
            return self.find_pawn_moves(s, color, 'moves')
    
    # this makes a copy of the board, makes the move, then sees if you put your king in check
    # returns boolean
    def is_legal_move(self, startsquare, endsquare, color):
            newboard = self.copy()
            newboard.move_piece(startsquare, endsquare, color, dothreats=False)
            return not newboard.check_check(color)
    
    # finds the MOVES that the piece on the named square can legally make
    # returns a list of MOVES - with are 2-element lists [startsquare, endsquare]
    def find_legal_moves_check_check(self, s, color):
        all_moves = self.find_legal_moves(s)
        legal_moves = [[s, move] for move in all_moves if self.is_legal_move(s, move, color)]
        return legal_moves
    
    # finds all of the moves that the named color can make
    # returns a list of MOVES - with are 2-element lists [startsquare, endsquare]
    def find_all_legal_moves(self, color='auto'):
        if color == 'auto':
            color = 'W' if self.white_tomove else 'B'
        # this does not yet include en passant
        pieces = self.get_all_color_pieces(color) #list of piece locations (tuples)
        
        all_legal_moves = []
        
        for p in pieces:
            all_legal_moves += self.find_legal_moves_check_check(p, color)
            
        #look for castling
        #if self.can_castle[color]:
        castle_moves = self.check_castling(color)
        all_legal_moves+=castle_moves
            
        if self.en_passantable_square:
            all_legal_moves += self.find_en_passantmoves(color)
            
        return all_legal_moves
    
    # finds all of the board positions that are possible after color makes its next move
    # returns a LIST of game_boards
    def find_all_next_board_positions(self):
        color = 'W' if self.white_tomove else 'B'
        #first we get the legal moves. For most moves, next board position will be obvious
        legal_moves = self.find_all_legal_moves(color)
        possible_boards = []
        for move in legal_moves: # a move is a list of 2 board positions (tuples), 
                                 # a castling move (1 string, eg O-O), 
                                 # or an en passant move (2 board positions and the string ep)
            # castling

            next_position = self.copy()
            if move in ['0-0', '0-0-0', 'O-O-O', 'O-O']:
                next_position.castle(color, move)
            elif len(move) == 3:
                #en passant
                #next_position.remove_piece(self.en_passantable_square, 'W' if color=='B' else 'B')
                next_position.board[self.en_passantable_square] = ' '
                next_position.move_piece(move[0], move[1], color)
            elif self.board[move[0]].lower() == 'p' and move[1][1] == self.promotion_row[color]:
                print('promoting pawn')
                # pawn promotion - just to knight or queen because we don't want the AI trolling
                #next_position.move_piece(move[0], move[1], color, dothreats=False)
                #next_position.remove_piece(move[1], color, dothreats=False)
                next_position.board[move[0]] = ' ' 
                #next_position.add_piece(move[1], 'Q' if color == 'W' else 'q', color, dothreats=False)
                next_position.board[move[1]] = 'Q' if color == 'W' else 'q' 
                next_position.white_tomove = not next_position.white_tomove
                #next_position.full_update_threats()
                possible_boards.append(next_position)
                
                next_position = self.copy()
                #next_position.move_piece(move[0], move[1], color, dothreats=False)
                #next_position.remove_piece(move[1], color, dothreats=False)
                #next_position.add_piece(move[1], 'N' if color == 'W' else 'n', color, dothreats=False)
                next_position.board[move[0]] = ' ' 
                next_position.board[move[1]] = 'N' if color == 'W' else 'n' 
                next_position.white_tomove = not next_position.white_tomove
                #next_position.full_update_threats()
                possible_boards.append(next_position)
                continue
            else:
                next_position.move_piece(move[0], move[1], color)
            next_position.white_tomove = not next_position.white_tomove
            possible_boards.append(next_position)
        return possible_boards
    
    # Checks to see which castling moves, if any, a player can make right now
    def check_castling(self, color):
        hr = 0 if color == 'W' else 7
        
        castling_moves = []
        
        k_castle_squares = [(4+i, hr) for i in range(4)]
        q_castle_squares = [(i, hr) for i in range(5)]
        #this conditional check if pieces between K and h-rook are open
        # then checks if any of those squares are threatened by other color
        if self.can_castle[color]['kingside'] and (np.all(self.board[[5, 6], [hr, hr]] == ' ') and
            np.all([not self.is_threatened(x, color) for x in 
                k_castle_squares])):
            # that means we can kingside castle
            castling_moves.append('0-0')
        
        if self.can_castle[color]['queenside'] and (np.all(self.board[[1, 2, 3], [hr, hr, hr]] == ' ') and
            np.all([not self.is_threatened(x, color) for x in 
                q_castle_squares])):            
            castling_moves.append('0-0-0')
        return castling_moves
    
    # looks at a particular square, and sees if the OTHER color threatens it
    def is_threatened(self, s, color):
        #find if a square is threatened by other color (used to see if castling is possible)
        assert color in ['W', 'B']
        pieces = self.get_all_color_pieces('W' if color == 'B' else 'B')
        target_locs = []
        for pieceloc in pieces:
            target_locs+= self.find_legal_moves(pieceloc)
        return s in target_locs
       
    def find_color(self, s):
        if self.board[s] in ['P', 'Q', 'K', 'R', 'B', 'N']:
            return 'W'
        elif self.board[s] in ['p', 'q', 'k', 'r', 'b', 'n']:
            return 'B'
        else:  
            return None
    
    # moves a piece owned by color from startsquare to endsquare,
    # updates castling ability (eg moving queenside rook makes that player unable
    #    to queenside castle later in the game)
    def move_piece(self, startsquare, endsquare, color, dothreats=True):
        #print(startsquare, endsquare, self.board[startsquare])
        if self.can_castle[color]['queenside'] or self.can_castle[color]['kingside']:
            if self.board[startsquare] in ['K', 'k']:
                self.can_castle[color]['queenside'] = False
                self.can_castle[color]['kingside'] = False
            elif self.board[startsquare] in ['R', 'r']:
                if startsquare[0] == 0:
                    self.can_castle[color]['queenside'] = False
                elif startsquare[0] == 7:
                    self.can_castle[color]['kingside'] = False

        self.en_passantable_square = None
                         
        if (self.board[startsquare].lower() == 'p'                        #if we're moving a pawn
                and startsquare[1] == self.pawn_home[color]                # and it started on the home row
                and startsquare[1] + 2*self.adv[color] == endsquare[1]):  # and it moved 2 spaces
                otherp = 'P' if color=='B' else 'p'
                if (self.board[min(endsquare[0]+1, 7), endsquare[1]] == otherp
                     or self.board[max(endsquare[0]-1, 0), endsquare[1]] == otherp):
                     self.en_passantable_square = endsquare
                     
        #if not self.board[endsquare] == ' ':
            #self.remove_piece(endsquare, 'B' if color=='W' else 'W', dothreats=dothreats)

        #p = self.remove_piece(startsquare, color, dothreats=dothreats)
        #self.add_piece(endsquare, p, color, dothreats=dothreats)

        self.board[endsquare] = self.board[startsquare]
        self.board[startsquare] = ' '
        

    def new_find_rookmoves(self, s, color):
        rank = self.board[:, s[1]]

        
    def new_find_kingmoves(self, s, color):
        #this looks ugly but it's fast
    
        if s[0] == 0:
            if s[1] == 0:
                #mx = np.array([s[0]+1, s[0]+1, s[0]])
                #my = np.array([s[1]+1, s[1], s[1]+1])
                moves = [(s[0]+1, s[1]+1),
                         (s[0]+1, s[1]),
                         (s[0], s[1]+1)] 
            elif s[1] == 7:
                #mx = np.array([s[0]+1, s[0]+1, s[0]])
                #my = np.array([s[1], s[1]-1, s[1]-1])
                moves = [(s[0]+1, s[1]),
                         (s[0]+1, s[1]-1)
                         (s[0], s[1]-1)] 
            else:
                moves = [(s[0]+1, s[1]+1),
                         (s[0]+1, s[1]),
                         (s[0]+1, s[1]-1),
                         (s[0], s[1]+1),
                         (s[0], s[1]-1)] 
        elif s[0] == 7:
            if s[1] == 0:
                moves = [(s[0], s[1]+1),
                         (s[0]-1, s[1]+1),
                         (s[0]-1, s[1])] 
            if s[1] == 7:
                moves = [(s[0], s[1]-1),
                         (s[0]-1, s[1]),
                         (s[0]-1, s[1]-1)]
            else:
                moves = [(s[0], s[1]+1),
                         (s[0], s[1]-1),
                         (s[0]-1, s[1]+1),
                         (s[0]-1, s[1]),
                         (s[0]-1, s[1]-1)] 
        else:
            if s[1] == 0:
                moves = [(s[0]+1, s[1]+1),
                         (s[0]+1, s[1]),
                         (s[0], s[1]+1),
                         (s[0]-1, s[1]+1),
                         (s[0]-1, s[1])]
            if s[1] == 7:
                moves = [(s[0]+1, s[1]),
                         (s[0]+1, s[1]-1),
                         (s[0], s[1]-1),
                         (s[0]-1, s[1]),
                         (s[0]-1, s[1]-1)]
            else:
                #mx = np.array([s[0]+1, s[0]+1, s[0]+1, s[0], s[0], s[0]-1, s[0]-1, s[0]-1])
                #my = np.array([s[1]+1, s[1], s[1]-1, s[1]+1, s[1]-1, s[1]+1, s[1], s[1]-1])
                moves = [(s[0]+1, s[1]+1),
                         (s[0]+1, s[1]),
                         (s[0]+1, s[1]-1),
                         (s[0], s[1]+1),
                         (s[0], s[1]-1),
                         (s[0]-1, s[1]+1),
                         (s[0]-1, s[1]),
                         (s[0]-1, s[1]-1)]
        
        #mcolors = self.cboard[np.array([mx, my])]
        #legal_moves = [m for m in moves if not self.board[s] in ['Q', 'K', 'R', 'P', 'K', 'B']]
        legal_moves = [m for m in moves if not self.cboard[s]==color]
    
        return legal_moves


    def find_en_passantmoves(self, color):
        # pawn to be captured is on s = self.en_passantable_square
        # pawns doing the capturing are on (s[0]+1, s[1]), (s[0]-1, s[1])
        s = self.en_passantable_square
        endsquare = (s[0], s[1] + self.adv[color])
        assert self.board[endsquare] == ' '
        cs1 = (min(s[0]+1, 7), s[1])
        cs2 = (max(s[0]-1, 0), s[1])
        open_moves = []

        if self.board[cs1].lower()=='p' and self.find_color(cs1)==color:
            open_moves.append([cs1, endsquare, 'ep'])
        if self.board[cs2].lower()=='p' and self.find_color(cs2)==color:
            open_moves.append([cs2, endsquare, 'ep'])
            
        assert(len(open_moves) > 0)
        return open_moves
        
    def copy(self):
        gamecopy = game_board(do_threats=False)
        gamecopy.board = np.copy(self.board)
        gamecopy.can_castle = deepcopy(self.can_castle)
        gamecopy.white_tomove = self.white_tomove
        gamecopy.wthreats = np.copy(self.wthreats)
        gamecopy.bthreats = np.copy(self.bthreats)
        return gamecopy
               
    def get_material(self, color):
        if color == 'W':
            return (9*np.sum(self.board=='Q') + 
                    5*np.sum(self.board=='R') + 
                    3*np.sum(self.board=='N') + 
                    3*np.sum(self.board=='B') + 
                    np.sum(self.board=='P'))
        elif color == 'B':
            return (9*np.sum(self.board=='q') + 
                    5*np.sum(self.board=='r') + 
                    3*np.sum(self.board=='n') + 
                    3*np.sum(self.board=='b') + 
                    np.sum(self.board=='p'))
        else:
            raise 
            
    def to_csv_format(self):
        # need 64 data points for the board, 1 for whose turn it is, 2 (will be 4) for castling abilities
        return np.append(self.board.flatten(), [int(self.white_tomove), 
                                                int(self.can_castle['W']['kingside']),
                                                int(self.can_castle['W']['queenside']),
                                                int(self.can_castle['B']['kingside']),
                                                int(self.can_castle['B']['queenside']),
                                                self.get_material('W'),
                                                self.get_material('B')])
    
    def get_NN_inputs(self, color, dothreats=True):
        # board will be given from point of view of color
        # if black, board is flipped (note: this is not what black would really see, it's mirrored)
        if dothreats:
            board_onehot = np.zeros((8, 8, 10))
            wthreats, bthreats = self.count_threats()
        else:
            board_onehot = np.zeros((8, 8, 8))

        #fboard = self.board.flatten()
        
        board_onehot[:, :, 2] = np.isin(self.board, ['K', 'k'])
        board_onehot[:, :, 3] = np.isin(self.board, ['Q', 'q'])
        board_onehot[:, :, 4] = np.isin(self.board, ['R', 'r'])
        board_onehot[:, :, 5] = np.isin(self.board, ['B', 'b'])
        board_onehot[:, :, 6] = np.isin(self.board, ['N', 'n'])
        board_onehot[:, :, 7] = np.isin(self.board, ['P', 'p'])
        
        if color == 'B':
            board_onehot[:, :, 0] = np.isin(self.board, ['p', 'r', 'n', 'b', 'k', 'q'])
            board_onehot[:, :, 1] = np.isin(self.board, ['P', 'R', 'N', 'B', 'K', 'Q'])
            if dothreats:
                board_onehot[:, :, 8] = bthreats
                board_onehot[:, :, 9] = wthreats
            board_onehot = np.flip(board_onehot, 1)

            aux = [int(self.can_castle['B']['kingside']),
                    int(self.can_castle['B']['queenside']),
                    int(self.can_castle['W']['kingside']),
                    int(self.can_castle['W']['queenside']),
                    self.get_material('B'),
                    self.get_material('W')]
        else:
            board_onehot[:, :, 0] = np.isin(self.board, ['P', 'R', 'N', 'B', 'K', 'Q'])
            board_onehot[:, :, 1] = np.isin(self.board, ['p', 'r', 'n', 'b', 'k', 'q'])
            if dothreats:
                board_onehot[:, :, 8] = wthreats
                board_onehot[:, :, 9] = bthreats
            aux = [int(self.can_castle['W']['kingside']),
                    int(self.can_castle['W']['queenside']),
                    int(self.can_castle['B']['kingside']),
                    int(self.can_castle['B']['queenside']),
                    self.get_material('W'),
                    self.get_material('B')]
                
        return board_onehot, aux
    
    def get_next_NN_inputs(self, color):
        wthreats, bthreats = self.count_threats()
        next_board_positions = self.find_all_next_board_positions()
        
    def full_update_threats(self):
        self.wthreats, self.bthreats = self.count_threats()
    
    def count_threats(self):
        white_threats = np.zeros((8,8))
        black_threats = np.zeros((8,8))
        
        #deal with pawns first
        #whitepawns = np.where(self.board == 'P')
        #whitepawns = [(whitepawns[0][i], whitepawns[1][i]) for i in range(len(whitepawns[0]))]
        #for p in whitepawns:
        #    if p[0] > 0:
        #        white_threats[p[0]-1,p[1]+1] += 1
        #    if p[0] < 7:
        #        white_threats[p[0]+1,p[1]+1] += 1
        #now all the other pieces
        white_pieces = np.where(np.isin(self.board, ['Q', 'K', 'N', 'R', 'B', 'P']))
        white_pieces = [(white_pieces[0][i], white_pieces[1][i]) for i in range(len(white_pieces[0]))]
        
        for p in white_pieces:
            moves = self.find_threats_from_piece(p, 'W')
            for m in moves:
                white_threats[m[1]] += 1
            
        #same for black
        #deal with pawns first
        #blackpawns = np.where(self.board == 'p')
        #blackpawns = [(blackpawns[0][i], blackpawns[1][i]) for i in range(len(blackpawns[0]))]
        #for p in blackpawns:
        #    if p[0] > 0:
        #        black_threats[p[0]-1,p[1]-1] += 1
        #    if p[0] < 7:
        #        black_threats[p[0]+1,p[1]-1] += 1
        #now all the other pieces
        black_pieces = np.where(np.isin(self.board, ['q', 'k', 'n', 'r', 'b', 'p']))
        black_pieces = [(black_pieces[0][i], black_pieces[1][i]) for i in range(len(black_pieces[0]))]
        
        for p in black_pieces:
            moves = self.find_threats_from_piece(p, 'B')
            for m in moves:
                black_threats[m[1]] += 1
                
        return white_threats, black_threats
        
    def find_threats_from_piece(self, s, color):
        if self.board[s].lower() == 'p':
            all_moves = self.find_pawn_moves(s, color, 'threats')
        elif self.board[s].lower() == 'b':
            all_moves = self.find_diagonal_moves(s, color, 'threats')
        elif self.board[s].lower() == 'n':
            all_moves = self.find_knight_moves(s, color, 'threats')
        elif self.board[s].lower() == 'r':
            all_moves = self.find_rook_moves(s, color, 'threats')
        elif self.board[s].lower() == 'k':
            all_moves = self.find_king_moves(s, color, 'threats')
        elif self.board[s].lower() == 'q':
            all_moves = self.find_queen_moves(s, color, 'threats')
        else:
            raise
        #print(s)
        #print(all_moves)
        all_moves = [ele for ele in all_moves if not ele == self.get_kingloc(color)]
        
        if self.is_pinned(s, color):
            legal_moves = [[s, move] for move in all_moves if self.is_legal_move(s, move, color)]
        else:
            legal_moves = all_moves
        return legal_moves
        
    def is_pinned(self, s, color):
        bc = self.copy()
        bc.board[s] == ' '
        return bc.check_check(color)
        
        

    def find_pawn_moves(self, s, color, t):
        if t == 'moves':
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
        elif t == 'threats':
            threatened_squares = []
            if s[0] > 0:
                threatened_squares += [(s[0]-1,s[1]+self.adv[color])]
            if s[0] < 7:
                threatened_squares += [(s[0]+1,s[1]+self.adv[color])]
            return threatened_squares

    def find_diagonal_moves(self, s, color, t):

        # go along each diagonal
        urs = [(s[0] + i, s[1] + i) for i in range(1, min(7-s[0], 7-s[1]) + 1)]
        uls = [(s[0] - i, s[1] + i) for i in range(1, min(s[0], 7-s[1]) + 1)]
        drs = [(s[0] + i, s[1] - i) for i in range(1, min(7-s[0], s[1]) + 1)]
        dls = [(s[0] - i, s[1] - i) for i in range(1, min(s[0], s[1]) + 1)]
        
        moves = [urs, uls, drs, dls]
        stop_index = [-1,-1,-1,-1]
        if t == 'moves':
            for i in range(len(moves)):
                for j in range(len(moves[i])):
                    if self.board[moves[i][j]] == ' ':
                        stop_index[i] = j
                    elif not self.find_color(moves[i][j]) == color:
                        stop_index[i] = j
                        break
                    else:
                        break
        elif t == 'threats':
            for i in range(len(moves)):
                for j in range(len(moves[i])):
                    if self.board[moves[i][j]] == ' ':
                        stop_index[i] = j
                    else:
                        stop_index[i] = j
                        break

        open_moves = [moves[i][:stop_index[i]+1] for i in range(4)]
        open_moves = [item for sublist in open_moves for item in sublist]
        open_moves = [ele for ele in open_moves if ele]
                
        return open_moves

    def new_find_diagonal_moves(self, s, color, t):
    
        
        for ii in [[1,1], [-1,1], [1,-1], [-1,-1]]:
            n = min(7-s[0], 7-s[1])
            sqs = [(s[0]+i*ii[0], s[1]+ii[1]) for i in range(1,1+n)]

        # go along each diagonal
        #nurs = min(7-s[0], 7-s[1])
        #nuls = min(s[0], 7-s[1])
        #ndrs = min(7-s[0], s[1])
        #ndls = min(s[0], s[1])
        
        #burs = self.board[[s[0] + i for i in range(1, nurs+1)], [s[1] + i for i in range(1, nurs+1)]]
        urs = [(s[0] + i, s[1] + i) for i in range(1, min(7-s[0], 7-s[1]) + 1)]
        uls = [(s[0] - i, s[1] + i) for i in range(1, min(s[0], 7-s[1]) + 1)]
        drs = [(s[0] + i, s[1] - i) for i in range(1, min(7-s[0], s[1]) + 1)]
        dls = [(s[0] - i, s[1] - i) for i in range(1, min(s[0], s[1]) + 1)]
        
        urs = np.transpose(np.c_[urs])
        uls = np.transpose(np.c_[uls])
        drs = np.transpose(np.c_[drs])
        dls = np.transpose(np.c_[dls])
       
        burs = self.board[urs[0], urs[1]]
        buls = self.board[uls[0], uls[1]]
        bdrs = self.board[drs[0], drs[1]]
        bdls = self.board[dls[0], dls[1]]
        
        moves = [urs, uls, drs, dls]
        stop_index = [-1,-1,-1,-1]
        if t == 'moves':
            for i in range(len(moves)):
                for j in range(len(moves[i])):
                    if self.board[moves[i][j]] == ' ':
                        stop_index[i] = j
                    elif not self.find_color(moves[i][j]) == color:
                        stop_index[i] = j
                        break
                    else:
                        break
        elif t == 'threats':
            for i in range(len(moves)):
                for j in range(len(moves[i])):
                    if self.board[moves[i][j]] == ' ':
                        stop_index[i] = j
                    else:
                        stop_index[i] = j
                        break

        open_moves = [moves[i][:stop_index[i]+1] for i in range(4)]
        open_moves = [item for sublist in open_moves for item in sublist]
        open_moves = [ele for ele in open_moves if ele]
                
        return open_moves
    def find_rook_moves(self, s, color, t):

        # go along each path all the way to the edge of the board
        u = [(s[0], s[1] + i) for i in range(1, 7-s[1] + 1)]
        d = [(s[0], s[1] - i) for i in range(1, s[1] + 1)]
        l = [(s[0] - i, s[1]) for i in range(1, s[0] + 1)]
        r = [(s[0] + i, s[1]) for i in range(1, 7-s[0] + 1)]

        moves = [u, d, l, r]
        stop_index = [-1,-1,-1,-1]
        # loop over each diagonal, go until a piece is blocking
        # if the piece is the other color, it can be captured
        if t == 'moves':
            for i in range(len(moves)):
                for j in range(len(moves[i])):
                    if self.board[moves[i][j]] == ' ':
                        stop_index[i] = j
                    elif not self.find_color(moves[i][j]) == color:
                        stop_index[i] = j
                        break
                    else:
                        break
        elif t ==  'threats':
            for i in range(len(moves)):
                for j in range(len(moves[i])):
                    if self.board[moves[i][j]] == ' ':
                        stop_index[i] = j
                    else:
                        stop_index[i] = j
                        break
        else:
            raise

        open_moves = [moves[i][:stop_index[i]+1] for i in range(4)]
        open_moves = [item for sublist in open_moves for item in sublist]
        open_moves = [ele for ele in open_moves if ele]
                        
        return open_moves


    def find_knight_moves(self, s, color, t):

        moves = [(s[0] + 2, s[1] + 1),
                 (s[0] - 2, s[1] + 1),
                 (s[0] + 2, s[1] - 1),
                 (s[0] - 2, s[1] - 1),
                 (s[0] + 1, s[1] + 2),
                 (s[0] - 1, s[1] + 2),
                 (s[0] + 1, s[1] - 2),
                 (s[0] - 1, s[1] - 2)]
        if t=='threats':
            legal_moves = [m for m in moves if (m[0]>=0 and m[0]<8 and m[1]>=0 and m[1]<8)]
        elif t=='moves':
            legal_moves = [m for m in moves if (m[0]>=0 and m[0]<8 and m[1]>=0 and m[1]<8) and (not self.find_color(m)==color)]
        return legal_moves
        
    def find_queen_moves(self, s, color, t):
    
        return self.find_rook_moves(s, color, t) + self.find_diagonal_moves(s, color, t)
        
    def find_king_moves(self, s, color, t):
        
        moves = [(s[0]+1, s[1]+1),
                 (s[0]+1, s[1]),
                 (s[0]+1, s[1]-1),
                 (s[0], s[1]+1),
                 (s[0], s[1]-1),
                 (s[0]-1, s[1]+1),
                 (s[0]-1, s[1]),
                 (s[0]-1, s[1]-1)]
        if t == 'moves':
            legal_moves = [m for m in moves if (m[0]>=0 and m[0]<8 and m[1]>=0 and m[1]<8) and (not self.find_color(m)==color)]
        elif t == 'threats':
            legal_moves = [m for m in moves if (m[0]>=0 and m[0]<8 and m[1]>=0 and m[1]<8)]
        else:
            raise
        return legal_moves
        
class saved_game():

    def __init__(self):
        self.num_moves = 0
        self.all_positions = [game_board()]
        self.log = np.empty((0,3))
        self.game_completed = False
        
    def _find_next_positions(self):
        self.next_positions = self.all_positions[-1].find_all_next_board_positions()
        
    def current_position(self):
        return self.all_positions[-1]
        
    def make_move(self, i, dothreats=True):
        self.all_positions.append(self.next_positions[i])
        self.num_moves += 1
        self.log = np.append(self.log, np.array(self.current_position().get_NN_inputs('W', dothreats=dothreats) + (None,))[np.newaxis, :], axis=0)
    
    def finish_game(self):
        score = self.find_winner()
        score_ar = np.array([0,0,0])
        score_ar[score] = 1
        #self.log = np.append(self.log, [score_ar], axis=1)
        self.log[:,2] = [score_ar for i in range(self.num_moves)]
        
    def get_next_NN_inputs(self, dothreats=True):
        self._find_next_positions()
        color = 'W' if self.current_position().white_tomove else 'B'
        self.next_NN_inputs = [ele.get_NN_inputs(color, dothreats=dothreats) for ele in self.next_positions]
        return self.next_NN_inputs
        
    def find_winner(self):
        # 0 for white win, 1 for draw, 2 for black win
        a, b = self.all_positions[-1].game_over()
        if a:
            return b
        w_material = self.all_positions[-1].get_material('W')
        b_material = self.all_positions[-1].get_material('B')
        if w_material > b_material:
            return 0
        elif b_material > w_material:
            return 2
        else:
            return 0
            
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

        
