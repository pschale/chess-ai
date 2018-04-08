fname = 'ficsgamesdb_2017_standard2000_nomovetimes_1543034.pgn'

ofile = 'games_parsed.txt'

with open(fname) as f:
    for line in f:
        if line[:7] == "[Result":
            score = line.split('"')[1]
        elif line[:2] == '1.':
            moves = line.split('{')[0]
            moves = moves.split(' ')
            moves = [ele for ele in moves if '.' not in ele]
            moves = ' '.join(moves)
            with open(ofile, 'a+') as h:
                h.write(score + ' ' + moves + '\n')
        
        
