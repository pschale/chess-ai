# chess-ai

Current status:
Can take any board position and whose move it is and give all possible positions available from it (equivalent to showing all legal moves, but it's hard to get all moves - like castling - into a uniform format, so I'm just outputing what the board position would be after the move is made)
mostly functional, though not very easy to input moves yet. Features left to implement:

Castling:
    Disable castling ability after relevant rook has moved (king move disables castling ability)

En passant:
    not added at all

pawn promotion:
    promoting to queeen only option

Move indicator:
    game does not keep track of who moves next

Feature to add if I'm really bored:
    make the printed board look pretty; could make image with matplotlib or something. Not at all necessary for the machine learning angle
