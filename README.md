# chess-ai

Current status:
Can take any board position and whose move it is and give all possible positions available from it (equivalent to showing all legal moves, but it's hard to get all moves - like castling - into a uniform format, so I'm just outputing what the board position would be after the move is made). Just added move indicator.

File board_positions_1.csv is a csv file with board positions and castling ability for the first 1000 games in the database, should be ready to stick into a NN

Features left to implement:

Draw conditions

full checking to ensure en passant is legal (when entered as algebraic move)

Feature to add if I'm really bored:
    make the printed board look pretty; could make image with matplotlib or something. Not at all necessary for the machine learning angle
