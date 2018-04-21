import chess_game as cg
import numpy as np

a = cg.game_board()
a.move('e4')
a.move('d5')
a.move('e5')
next_positions = a.find_all_next_board_positions()
assert False in [None==ele.en_passantable_square for ele in next_positions]
print('Successfully finds move that will make en passant possible')

a.move('f5')
next_moves = a.find_all_legal_moves()
assert [(4, 4), (5, 5), 'ep'] in next_moves
print('Successfuly finds en passant move')
a.move('exf6')
print(a)
print('check to make sure en passant move was done successfully')

b = cg.game_board()
b.move('e4')
b.move('a5')
b.move('g4')
b.move('a4')
b.move('e5')
b.move('b5')
b.move('g5')
b.move('f5')
print(b)
next_moves = b.find_all_legal_moves()
ep_moves = [m for m in next_moves if 'ep' in m]
print(ep_moves)
print('there should be 2 en passant moves available')

c = cg.game_board()
c.move('g4')
c.move('e6')
c.move('g5')
c.move('h5')
print([m for m in c.find_all_legal_moves() if 'ep' in m])

#print(a)
#print(a.en_passantable_square)
#print(a.find_all_legal_moves('B'))
#[print(ele) for ele in a.find_all_next_board_positions('B')]
#[print(ele.en_passantable_square) for ele in a.find_all_next_board_positions('B')]
