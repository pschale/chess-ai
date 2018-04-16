import chess_game as cg
import pandas as pd
import numpy as np
import time

b = np.empty((8,8), dtype='str')
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
for i in range(8):
    b[i, :] = letters[i]
    
c = np.empty((8,8), dtype='str')
for i in range(8):
    c[:, i] = str(i+1)

outfile = open('board_positions/board_positions_1.txt', 'w+')

squares = np.core.defchararray.add(b,c)
cols = np.append(squares.flatten(), ['white_tomove', 'w_castle_kingside', 'w_castle_queenside', 
                                     'b_castle_kingside', 'b_castle_queenside', 'w_material', 
                                     'b_material', 'game_num', 'move_num', 'moves_in_game', 'winner'])

outfile.write(",".join(cols))

i = 0

file_num = 1
game_num = 0
with open('games_parsed.txt', 'r') as h:
    for line in h:
        game_num += 1
        start = time.time()
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
        move_num = 0
        moves_in_game = len(moves)
        for m in moves:
            try:
                g.move(m)
                move_num +=1
                board_position = g.to_csv_format()
                #datarow = np.append(board_position, [white_score]).reshape((1, 70))
                #data = np.append(data, datarow, axis=0)
                outfile.write("\n")
                outfile.write(",".join(list(board_position) + [str(game_num), str(move_num), str(moves_in_game), str(white_score)]))
            except:
                with open('problem_games.txt', 'a+') as h:
                    h.write("error with game {}, at move {}".format(game_num, move_num))
                    h.write("\n")
                    h.write(str(moves))
                    h.write("\n")
                    h.write(str(g))
                    h.write("\n")
                continue
        i += 1
        end = time.time()
        print('Game {} done in {:.2f} seconds, {:.4f} sec/move'.format(i, end - start, (end-start)/len(moves)))
        if i%10000==0:
            outfile.close()
            file_num += 1
            outfile = open('board_positions/board_positions_' + str(file_num) + '.csv', 'w+')
            outfile.write(",".join(cols))

