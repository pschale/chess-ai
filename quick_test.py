import chess_game as cg
import numpy as np

a = cg.game_board()

#a.move('e4', 'W')

#a.move('e5', 'B')

#a.move('d4', 'W')
#a.move('Bb4', 'B')
#a.move('Nc3', 'W')
#a.move('Nf3', 'W')
#a.move('Bd3', 'W')
#a.print()
next_board_positions = a.find_all_next_board_positions('W')
print(next_board_positions)
[print(j) for j in a.find_all_next_board_positions('W')]