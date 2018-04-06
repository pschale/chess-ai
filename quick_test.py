import chess_game as cg
import numpy as np

a = cg.game_board()

a.move('e4', 'W')

a.move('e5', 'B')

a.move('d4', 'W')
a.move('Bb4', 'B')

a.print()

print(a.check_check('W'))