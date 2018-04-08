import chess_game as cg
import numpy as np

#Test 1: 2-move checkmate

a = cg.game_board()
checkmate_2move = ['f3', 'e5', 'g4', 'Qh4']
a.play_game(checkmate_2move)
csvstr = a.to_csv_format()

a = cg.game_board(gametype = 'saved', csvstr = csvstr)
print(a)



#Test 2: 4-move checkmate
a = cg.game_board()
checkmate_4move = ['e4', 'e5', 'Qf3', 'Nc6', 'Bc4', 'b5', 'Qxf7']
a.play_game(checkmate_4move)

#Test 3: first game from fics database
f = open('games_parsed.txt')
game = f.readline().split()[1:-1]
print(game)
a = cg.game_board()
a.play_game(game)
