### Chess AI project
### basic game (no AI yet)
import numpy as np


class game_board():

    def __init__(self, gametype='newgame'):
        #make empty board
        self.white_pieces = np.zeros((8,8))
        self.black_pieces = np.zeros((8,8))

        #add pawns and kings
        if gametype=='newgame':
            self.white_pieces[:, 1] = 1
            self.white_pieces[0, 0] = 4
            self.white_pieces[7, 0] = 4
            self.white_pieces[1, 0] = 3
            self.white_pieces[6, 0] = 3
            self.white_pieces[2, 0] = 2
            self.white_pieces[5, 0] = 2
            self.white_pieces[3, 0] = 5
            self.white_pieces[4, 0] = 6
                 
            self.black_pieces[:, 6] = 1
            self.black_pieces[0, 7] = 4
            self.black_pieces[7, 7] = 4
            self.black_pieces[1, 7] = 3
            self.black_pieces[6, 7] = 3
            self.black_pieces[2, 7] = 2
            self.black_pieces[5, 7] = 2
            self.black_pieces[4, 7] = 6
            self.black_pieces[3, 7] = 5
            
        self.combine_board()
        
    def combine_board(self):
        self.board = np.empty((8,8),dtype='str')
        self.board[:, :] = " "
        self.board[self.white_pieces==1] = 'P'
        self.board[self.white_pieces==2] = 'B'
        self.board[self.white_pieces==3] = 'N'
        self.board[self.white_pieces==4] = 'R'
        self.board[self.white_pieces==5] = 'Q'
        self.board[self.white_pieces==6] = 'K'
        
        self.board[self.black_pieces==1] = 'p'
        self.board[self.black_pieces==2] = 'b'
        self.board[self.black_pieces==3] = 'n'
        self.board[self.black_pieces==4] = 'r'
        self.board[self.black_pieces==5] = 'q'
        self.board[self.black_pieces==6] = 'k'
        
    def print(self):
    
        #self.combine_board()
        
        for i in range(7, -1, -1):
            print ('| ' + ' | '.join(list(self.board[:, i])))
            
    def move_piece(self, startsquare, endsquare):
        self.board[endsquare] = self.board[startsquare]
        self.board[startsquare] = ' '
            
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

        
