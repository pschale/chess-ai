### Chess AI project
### basic game (no AI yet)
import numpy as np


class game_board():

    def __init__(self, gametype='newgame'):
        #make empty board
        
        self.board = np.empty((8,8),dtype='str')
        self.board[:, :] = " "

        #add pawns and kings
        if gametype=='newgame':
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
        
    def print(self):
        
        for i in range(7, -1, -1):
            print ('| ' + ' | '.join(list(self.board[:, i])))
            
    def move_piece(self, startsquare, endsquare):
        self.board[endsquare] = self.board[startsquare]
        self.board[startsquare] = ' '
    
    def get_all_color_pieces(self, color):
        assert color in ['W', 'B']
        if color == 'W':
            inds = np.where(np.isin(self.board, ['Q', 'K', 'N', 'R', 'B', 'P']))
        else:
            inds = np.where(np.isin(self.board, ['q', 'k', 'n', 'r', 'b', 'p']))
    
        return [(inds[0][i], inds[1][i]) for i in range(len(inds[0]))]
    
    
    def check_check(self, color):
        #color is the color of the possibly threatened king
        kingloc = np.where(self.board == 'K' if color == 'W' else 'k')
        kingloc = (kingloc[0][0], kingloc[1][0])
        print(kingloc)
        assert color in ['W', 'B']
        pieces = self.get_all_color_pieces('W' if color == 'B' else 'B')
        target_locs = []
        for pieceloc in pieces:
            target_locs+= self.find_legal_moves(pieceloc)
        print(target_locs)
        return kingloc in target_locs
            
    def move(self, move, color):
        assert color in ['W', 'B']
        if move=='O-O':
            homerank = 0 if color=='W' else 7
            # add assertions to make sure this is legal move
            self.move_piece((4, homerank), (6, homerank))
            self.move_piece((7, homerank), (5, homerank))
        elif move == 'O-O-O':
            # add assertions to make sure this is legal move
            self.move_piece((4, homerank), (2, homerank))
            self.move_piece((0, homerank), (3, homerank))
        else:
            # first, we need to figure out which square we're moving to
            endsquare = square_index(move[-2:]) #note this is not true for queen promotions
            if color == 'W':
                pawn_home = 1
                adv = 1
                myp = 'P'
            else:
                pawn_home = 6
                adv = -1
                myp = 'p'
            if len(move) == 2: #this is a simple pawn move

                # check if it's a pawn moving two spaces
                if (endsquare[1] == pawn_home + 2*adv) and self.board[endsquare[0], pawn_home+adv] == ' ':
                    assert self.board[endsquare[0], pawn_home] == myp
                    self.move_piece((endsquare[0], pawn_home), endsquare)
                else:
                    assert self.board[endsquare[0], endsquare[1] - adv] == myp
                    assert self.board[endsquare] == ' '
                    self.move_piece((endsquare[0], endsquare[1] - adv), endsquare)
            elif '=' in move:
                endsquare = square_index(move[-3:-1])
                startsquare = (endsquare[0], endsquare[1] - adv)
                assert self.board[startsquare] == myp
                self.move_piece(endsquare, startsquare)
                self.board[endsquare] = move[-1]
                if color == 'B':
                    self.board[endsquare] = self.board(endsquare).lower()
                #pawn promoting
            elif move[0] in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
                startsquare = (['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].index(move[0]), endsquare[1] - adv)
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
                    print(legal_pieces_locnames)
                    scores = [0 for ele in legal_pieces_locnames]
                    for character in info:
                        for i in range(len(legal_pieces_locnames)):
                            print(character in legal_pieces_locnames[i])
                            scores[i] += 1 if character in legal_pieces_locnames[i] else 0
                    startsquare = legal_pieces[scores.index(max(scores))]


                print(square_name(startsquare), square_name(endsquare))
                self.move_piece(startsquare, endsquare)

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

        # go along each path
        u = [(s[0], s[1] + i) for i in range(1, 7-s[1] + 1)]
        d = [(s[0], s[1] - i) for i in range(1, s[1] + 1)]
        l = [(s[0] - i, s[1]) for i in range(1, s[0] + 1)]
        r = [(s[0] + i, s[1]) for i in range(1, 7-s[0] + 1)]

        moves = [u, d, l, r]
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

        
