import chess_game as cg
import numpy as np

#Test 1: 2-move checkmate

a = cg.game_board()
checkmate_2move = ['f3', 'e5', 'g4', 'Qh4']
a.play_game(checkmate_2move)
csvstr = a.to_csv_format()
print('this should be a 2-move checkmate, black wins')
b = cg.game_board(gametype = 'saved', csvstr = csvstr)
print(b)
print('this should look exactly the same')


#Test 2: 4-move checkmate
a = cg.game_board()
checkmate_4move = ['e4', 'e5', 'Qf3', 'Nc6', 'Bc4', 'b5', 'Qxf7']
a.play_game(checkmate_4move)
print('this should be 4-move checkmate')

#Test 3: first game from fics database
f = open('games_parsed.txt')
game = f.readline().split()[1:-1]
a = cg.game_board()
a.play_game(game)

#Test 4: game with pawn promotion via capture
a = cg.game_board()
game = 'e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 a6 f4 e5 Nf3 Nbd7 ' + \
       'a4 Qc7 Bd3 Be7 Qe2 O-O O-O b6 fxe5 dxe5 Kh1 Nc5 Bg5 ' + \
       'Be6 Nh4 Nxd3 cxd3 Kh8 Nf5 Ng8 Be3 Rad8 Nxe7 Nxe7 a5 ' + \
       'bxa5 Na4 Qd6 Qf2 Rc8 Bc5 Qc7 Rfc1 Rfe8 Rc3 Nc6 Nb6 Rb8 ' + \
       'Nd5 Qd7 Nf6 gxf6 Qxf6+ Kg8 d4 Rb3 d5 Bxd5 Qg5+ Kh8 Rd1 ' + \
       'Rxc3 bxc3 Qd8 Qh5 Qf6 exd5 Nb8 Qh3 a4 c4 Qf4 Be3 Qe4 c5 ' + \
       'Rg8 Qf3 Qxf3 gxf3 Rc8 Ra1 Rd8 c6 Rc8 Rc1 a3 c7 Kg7 d6 Kf6 ' + \
       'cxb8=R Rxb8 Ra1 Ke6 Rxa3 Ra8 Bc5 a5 Ra4 Kd5 Ba3 Ra7 Kg2 f6 ' + \
       'Kg3 f5 Kh4 Ke6 Rc4 Rb7'

game = game.split()
a.play_game(game)
