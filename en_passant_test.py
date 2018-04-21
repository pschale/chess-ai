import chess_game as cg
import numpy as np

a = cg.game_board()
a.move('e4')
a.move('d5')
a.move('e5')
#a.move('f5')
print(a)
print(a.en_passantable_square)
print(a.find_all_legal_moves('B'))
[print(ele) for ele in a.find_all_next_board_positions('B')]
[print(ele.en_passantable_square) for ele in a.find_all_next_board_positions('B')]
