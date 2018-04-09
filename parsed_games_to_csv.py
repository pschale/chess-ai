import chess_game as cg
import pandas as pd
import numpy as np

b = np.empty((8,8), dtype='str')
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
for i in range(8):
    b[i, :] = letters[i]
    
c = np.empty((8,8), dtype='str')
for i in range(8):
    c[:, i] = str(i+1)
    
squares = np.core.defchararray.add(b,c)
cols = np.append(squares.flatten(), ['white_tomove', 'w_castle', 'b_castle', 'winner'])

i = 0

data = np.empty((0, 70), dtype='str')
with open('games_parsed.txt', 'r') as h:
    for line in h:
        print(i)
        game = line.split()
        score = game[0]
        moves = game[1:]
        if score == '0-1':
            white_score = -1
        elif score == '1/2-1/2':
            white_score = 0
        elif score == '1-0':
            white_score = 1
        else:
            raise ValueError('do not recongize score {}'.format(score))
        
        moves = [ele.replace('+', '') for ele in moves]
        moves = [ele.replace('#', '') for ele in moves]
        g = cg.game_board()
        for m in moves:
            g.move(m)
            board_position = g.to_csv_format()
            datarow = np.append(board_position, [white_score]).reshape((1, 70))
            data = np.append(data, datarow, axis=0)
        i += 1

        if i > 1000:
            break
df = pd.DataFrame(data=data, columns=cols)
df.to_csv('board_positions.csv')

