import pygame
import graphics
from collections import OrderedDict

# Shogi constants
# starting pieces and promotions
# pawn, lance, knight, silver general, gold general, king
# Sente and Gote pieces
def add_piece_id(pieces_dict, string_id, id, can_promote=True):
    # Sente and Gote pieces
    sg = ['S', 'G']
    for i in range(len(sg)):
        # unpromoted
        piece = sg[i] + string_id
        pieces_dict[piece] = id
        # promoted
        if can_promote:
            promoted = sg[i] + 'P' + string_id
            pieces_dict[promoted] = id + 1
            id += 1
        id += 1
    return id

def get_piece_ids():
    pieces = {}
    id = 0
    piece_symbs = ['P', 'L', 'N', 'S', 'R', 'B']
    # Add promotable pieces
    for s in piece_symbs:
        id = add_piece_id(pieces, s, id)
    # Add Gold and King
    id = add_piece_id(pieces, 'G', id, False)
    id = add_piece_id(pieces, 'K', id, False)
    return pieces

piece_ids = get_piece_ids()
SPRITES_PATH = './sprites/'
PNG = '.png'

class Shogi:
    """
    Holds all data related to the current state of the game
    in addition to all graphical data
    """
    def __init__(self, bwidth, debug=False):
        self.board = Board(bwidth, debug)
        # Whose turn is it? 0=sente 1=gote
        self._turn = 0
        self._selected_piece = None
        self._selected_piece_target_positions = []

    @property
    def turn(self):
        return self._turn

    @property
    def selected_piece_target_positions(self):
        return self._selected_piece_target_positions

    @property
    def selected_piece(self):
        return self._selected_piece

    @selected_piece.setter
    def selected_piece(self, piece):
        self._selected_piece = piece
        targets = []
        # Selected piece can be set to None if a piece is not selected
        # or if a piece not belonging to the current player is selected
        if piece is not None:
            enemy_positions = [p.position for p in self.board.player_pieces[(self.turn+1)%2]]
            player_positions = [p.position for p in self.board.player_pieces[self.turn]]
            # If selected piece is not on board, it is droppable
            # Target constraints differ from pieces in play
            if piece.on_board is False:
                # Two cases, pawn or not
                if piece.id == 0 or piece.id == 2:
                    # pawn cannot be dropped where there is already a pawn owned by the player
                    print(piece.targets)
                    for player_piece in self.board.player_pieces[self.turn]:
                        # If player piece is a pawn (pawn is in orientation facing away from player)
                        # Remove targets along the column where that pawn is
                        if player_piece.id == self.turn * 2 and player_piece.on_board:
                            print(player_piece.id)
                            print(player_piece.position)
                            del piece.targets[player_piece.position[0]]
                # Not pawn, targets should only be empty squares
                for p in self.board.all_pieces:
                    if p.on_board:
                        col = p.position[0]
                        if col in piece.targets:
                            piece.targets[col].remove(p.position)
                targets = [pos for key in piece.targets for pos in piece.targets[key]]
            else:
                # Add all target positions in a direction to list up until the max range or when
                # the piece targets a piece on the same side
                for movement, position in piece.targets.items():
                    for pos in position:
                        # If target is an enemy, we want to include it as a target
                        # But we do not want to extend any further
                        if pos in enemy_positions:
                            targets.append(pos)
                            break
                        # Include blank squares as targets
                        if pos not in player_positions:
                            targets.append(pos)
                        # We cannot attack our own pieces so don't include them
                        else:
                            break
        self._selected_piece_target_positions = targets

    def _next_turn(self):
        self._turn = (self._turn + 1) % 2

    def move_selected_piece(self, new_pos, dropped, promote):
        """
        Move the selected piece to the new position and handle capture
        """
        self.board.update_piece(self._selected_piece, self.turn, new_pos=new_pos, dropped=dropped, promote=promote)
        # Handle capture
        self._capture_handler()
        # Update squares targeted by the moved piece
        self._selected_piece.update()
        # Increment the turn
        self._next_turn()

    def _capture_handler(self):
        """ Remove enemy piece if selected piece lands on it """
        if self.turn == 0:
            for piece in self.board.gote_pieces:
                if piece.position == self._selected_piece.position:
                    # Piece to be captured is a gote piece so 1
                    self.board.update_piece(piece, 1, captured=True)
                    break
        else:
            for piece in self.board.sente_pieces:
                if piece.position == self._selected_piece.position:
                    # Piece to be captured is a sente piece so 0
                    self.board.update_piece(piece, 0, captured=True)
                    break

class Board:

    def __init__(self, bwidth, debug=False):
        # Assume player's pieces are sente
        self.sente_pieces = pygame.sprite.Group()
        self.gote_pieces = pygame.sprite.Group()
        self.all_pieces = pygame.sprite.Group()
        self.sente_dropcount = OrderedDict()
        self.gote_dropcount = OrderedDict()
        self.player_pieces = {0:self.sente_pieces, 1:self.gote_pieces}
        self.width = bwidth
        # self.board = _init_board(self.pieces)
        #self._piece_ids = self._get_piece_ids()
        self._init_pieces()
        if debug == True:
            print(piece_ids)
            for p in self.sente_pieces:
                print('{}, {}'.format(p.id, p.position))

    def _init_pieces(self):
        # Add pawns
        for i in range(1, 10):
            self.sente_pieces.add(Piece(piece_ids['SP'], (i, 3), self.width))
            self.gote_pieces.add(Piece(piece_ids['GP'], (i, 7), self.width))
        # Add lances, knights, silver, golds
        pieces = ['L','N','S','G']
        for i in range(1, len(pieces)+1):
            if pieces[i-1] == 'G':
                # First half of board
                self.sente_pieces.add(Piece(piece_ids['S'+pieces[i-1]], (i, 1), self.width, promotable=False))
                self.gote_pieces.add(Piece(piece_ids['G'+pieces[i-1]], (i, 9), self.width, promotable=False))
                # Second half of board
                self.sente_pieces.add(Piece(piece_ids['S'+pieces[i-1]], (10-i, 1), self.width, promotable=False))
                self.gote_pieces.add(Piece(piece_ids['G'+pieces[i-1]], (10-i, 9), self.width, promotable=False))
            else:
                # First half of board
                self.sente_pieces.add(Piece(piece_ids['S'+pieces[i-1]], (i, 1), self.width))
                self.gote_pieces.add(Piece(piece_ids['G'+pieces[i-1]], (i, 9), self.width))
                # Second half of board
                self.sente_pieces.add(Piece(piece_ids['S'+pieces[i-1]], (10-i, 1), self.width))
                self.gote_pieces.add(Piece(piece_ids['G'+pieces[i-1]], (10-i, 9), self.width))
        # Add kings, bishops, rooks
        self.sente_pieces.add(Piece(piece_ids['SK'], (5, 1), self.width,  promotable=False))
        self.gote_pieces.add(Piece(piece_ids['GK'], (5, 9), self.width, promotable=False))
        self.sente_pieces.add(Piece(piece_ids['SB'], (2, 2), self.width))
        self.gote_pieces.add(Piece(piece_ids['GB'], (8, 8), self.width))
        self.sente_pieces.add(Piece(piece_ids['SR'], (8, 2), self.width))
        self.gote_pieces.add(Piece(piece_ids['GR'], (2, 8), self.width))
        # Add to all_pieces
        self.all_pieces.add([s for s in self.sente_pieces])
        self.all_pieces.add([s for s in self.gote_pieces])

    def update_piece(self, piece, type, new_pos=None, promote=False, captured=False, dropped=False):
        """
        Update groups with information about the selected piece
        type - 0 sente, 1 gote
        """
        groups = [self.sente_pieces, self.gote_pieces]
        dropcount = [self.sente_dropcount, self.gote_dropcount]
        old_pos = piece.position
        optype = (type + 1) % 2
        # Allow piece to be updated by removing it from groups
        self.all_pieces.remove(piece)
        groups[type].remove(piece)
        # Update it's position if given
        if new_pos is not None:
            piece.position = new_pos
        # If the piece is being dropped onto the board
        if dropped:
            # Decrement piece count and remove if there are 0 of them
            dropcount[type][piece.id] -= 1
            if dropcount[type][piece.id] == 0:
                del dropcount[type][piece.id]
            else:
                # Create new piece to replace it
                new_piece = Piece(piece.id, None, self.width, on_board=False)
                groups[type].add(new_piece)
                self.all_pieces.add(new_piece)
            # Piece is now in play
            piece.on_board = True
        if promote:
            # Add promoted piece
            # Promoted piece's id is one greater than unpromoted version
            new_piece = Piece(piece.id+1, new_pos, self.width, promotable=False)
            groups[type].add(new_piece)
            self.all_pieces.add(new_piece)
            # We do not want to add the original piece back into the groups
            return
        # Give ownership to enemy if piece is captured
        # otherwise return ownership.
        # If piece is dropped, it will be added to the correct groups
        if captured:
            # Promoted pieces need to be chagned to unpromoted form
            if piece.promotable == False and piece.id != 24 and piece.id != 25:
                piece.id -= 1
            # Switch orientation of captured piece
            # Gold has a different id switch calculation
            if piece.id == 24:
                id = 25
            elif piece.id == 25:
                id = 24
            else:
                # Get all face up pieces to face down, vice versa
                if ((piece.id + 2) / 2) % 2 != 0:
                    id = piece.id + 2
                else:
                    id = piece.id - 2
            if id in dropcount[optype]:
                dropcount[optype][id] += 1
            else:
                # Add captured piece to group only once
                cap_piece = Piece(id, None, self.width, on_board=False)
                groups[optype].add(cap_piece)
                dropcount[optype][cap_piece.id] = 1
                # Add captured piece to all pieces
                self.all_pieces.add(cap_piece)
        else:
            groups[type].add(piece)
            # Add piece back to all pieces
            self.all_pieces.add(piece)

class Piece(pygame.sprite.Sprite):
    def __init__(self, id, position, bwidth, on_board=True, promotable=True, size=(40,40)):
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.position = position
        self.on_board = on_board
        self._bwidth = bwidth
        self.promotable = promotable
        self.size = size
        self._targets = self._update_targets()
        try:
            self.image = pygame.image.load(SPRITES_PATH + str(self.id) + PNG)
        except Exception as e:
            print(e)
            self.image = pygame.Surface(self.size)
            self._fill_image()
        self.rect = self.image.get_rect()
        self.rect.size = size

    @property
    def targets(self):
        """
        Converts logical position of target to graphical position relative
        to the board
        """
        return self._targets
        """
        targets = {}
        if self._targets:
            for movement, positions in self._targets.items():
                graphical_pos = []
                for pos in positions:
                    graphical_pos.append(self._position_to_board(pos))
                targets[movement] = graphical_pos
        return targets
        """

    def update(self):
        """ Wrapper around update methods """
        self._targets = self._update_targets()

    def _update_targets(self):
        """ Sets the positions that are targeted by the piece instance """
        promoted_down = [1, 5, 9, 13]
        promoted_up = [3, 7, 11, 15]
        # Pawn
        if self.id == 0:
            movement = {'down':1}
            return self._get_targets(movement)
        elif self.id == 2:
            movement = {'up':1}
            return self._get_targets(movement)
        # Lance
        elif self.id == 4:
            movement = {'down':8}
            return self._get_targets(movement)
        elif self.id == 6:
            movement = {'up':8}
            return self._get_targets(movement)
        # Knight
        elif self.id == 8:
            movement = {'nldown':1, 'nrdown':1}
            return self._get_targets(movement)
        elif self.id == 10:
            movement = {'nlup':1, 'nrup':1}
            return self._get_targets(movement)
        # Silver
        elif self.id == 12:
            movement = {'down':1, 'ludiag':1, 'rudiag':1, 'lddiag':1, 'rddiag':1}
            return self._get_targets(movement)
        elif self.id == 14:
            movement = {'up':1, 'ludiag':1, 'rudiag':1, 'lddiag':1, 'rddiag':1}
            return self._get_targets(movement)
        # Bishop
        elif self.id == 16 or self.id == 18:
            movement = {'ludiag':8, 'rudiag':8, 'lddiag':8, 'rddiag':8}
            return self._get_targets(movement)
        # Promoted Bishop
        elif self.id == 17 or self.id == 19:
            movement = {'ludiag':8, 'rudiag':8, 'lddiag':8, 'rddiag':8, 'up':1, 'down':1, 'left':1, 'right':1}
            return self._get_targets(movement)
        # Rook
        elif self.id == 20 or self.id == 22:
            movement = {'up':8, 'down':8, 'left':8, 'right':8}
            return self._get_targets(movement)
        # Promoted Rook
        elif self.id == 21 or self.id == 23:
            movement = {'up':8, 'down':8, 'left':8, 'right':8, 'lddiag':1, 'rddiag':1, 'ludiag':1, 'rudiag':1}
            return self._get_targets(movement)
        # Gold
        elif self.id == 24 or self.id in promoted_down:
            movement = {'up':1, 'down':1, 'left':1, 'right':1, 'lddiag':1, 'rddiag':1}
            return self._get_targets(movement)
        elif self.id == 25 or self.id in promoted_up:
            movement = {'up':1, 'down':1, 'left':1, 'right':1, 'ludiag':1, 'rudiag':1}
            return self._get_targets(movement)
        # King
        elif self.id == 26 or self.id == 27:
            movement = {'up':1, 'down':1, 'left':1, 'right':1, 'ludiag':1, 'rudiag':1, 'lddiag':1, 'rddiag':1}
            return self._get_targets(movement)

    def _get_targets(self, movement):
        """
        Finds the squares targeted by the piece instance
        Params:
            movement - dict with key that determines direction of attack,
                        and value that determines squares to target in that direction
        """
        targets = {}
        pot_targets = []
        # Position may be None if piece is droppable
        try:
            x = self.position[0]
            y = self.position[1]
        except:
            # In this case, we set the piece's targets to all spaces
            # targets becomes a dict with key: column, vals: list of positions in column
            for c in range(1,10):
                cols = []
                for r in range(1,10):
                    cols.append((c, r))
                targets[c] = cols
            return targets
        # Assign targets
        for move, num in movement.items():
            if move == 'down':
                pot_targets = [(x, y+n) for n in range(num+1)][1:]
                in_bounds_targets = self._positions_in_bounds(pot_targets)
                if in_bounds_targets:
                    targets[move] = in_bounds_targets
            elif move == 'up':
                pot_targets = [(x, y-n) for n in range(num+1)][1:]
                in_bounds_targets = self._positions_in_bounds(pot_targets)
                if in_bounds_targets:
                    targets[move] = in_bounds_targets
            elif move == 'left':
                pot_targets = [(x-n, y) for n in range(num+1)][1:]
                in_bounds_targets = self._positions_in_bounds(pot_targets)
                if in_bounds_targets:
                    targets[move] = in_bounds_targets
            elif move == 'right':
                pot_targets = [(x+n, y) for n in range(num+1)][1:]
                in_bounds_targets = self._positions_in_bounds(pot_targets)
                if in_bounds_targets:
                    targets[move] = in_bounds_targets
            elif move == 'ludiag':
                pot_targets = [(x-n, y-n) for n in range(num+1)[1:]]
                in_bounds_targets = self._positions_in_bounds(pot_targets)
                if in_bounds_targets:
                    targets[move] = in_bounds_targets
            elif move == 'rudiag':
                pot_targets = [(x+n, y-n) for n in range(num+1)[1:]]
                in_bounds_targets = self._positions_in_bounds(pot_targets)
                if in_bounds_targets:
                    targets[move] = in_bounds_targets
            elif move == 'lddiag':
                pot_targets = [(x-n, y+n) for n in range(num+1)[1:]]
                in_bounds_targets = self._positions_in_bounds(pot_targets)
                if in_bounds_targets:
                    targets[move] = in_bounds_targets
            elif move == 'rddiag':
                pot_targets = [(x+n, y+n) for n in range(num+1)[1:]]
                in_bounds_targets = self._positions_in_bounds(pot_targets)
                if in_bounds_targets:
                    targets[move] = in_bounds_targets
            elif move == 'nlup':
                pot_targets = [(x-1, y-2)]
                in_bounds_targets = self._positions_in_bounds(pot_targets)
                if in_bounds_targets:
                    targets[move] = in_bounds_targets
            elif move == 'nrup':
                pot_targets = [(x+1, y-2)]
                in_bounds_targets = self._positions_in_bounds(pot_targets)
                if in_bounds_targets:
                    targets[move] = in_bounds_targets
            elif move == 'nldown':
                pot_targets = [(x-1, y+2)]
                in_bounds_targets = self._positions_in_bounds(pot_targets)
                if in_bounds_targets:
                    targets[move] = in_bounds_targets
            elif move == 'nrdown':
                pot_targets = [(x+1, y+2)]
                in_bounds_targets = self._positions_in_bounds(pot_targets)
                if in_bounds_targets:
                    targets[move] = in_bounds_targets
        return targets

    def _positions_in_bounds(self, positions):
        """ Return positions that are in the board bounds """
        in_bounds = []
        for pos in positions:
            if 0 < pos[0] and pos[0] < 10:
                if 0 < pos[1] and pos[1] < 10:
                    in_bounds.append(pos)
        return in_bounds

    def _fill_image(self):
        """ Placeholder for shogi pieces """
        if self.id == piece_ids['SP']:
            self.image.fill(graphics.RED)
        elif self.id == piece_ids['SL']:
            self.image.fill(graphics.GREEN)
        elif self.id == piece_ids['SN']:
            self.image.fill(graphics.BLUE)
"""
pygame.init()
# 4:3 ascpect ratio
width = 800
height = 600
screen = pygame.display.set_mode((width, height))
# Game vars
done = False
clock = pygame.time.Clock()

# Shogi board is a 9x9 square
bwidth = 450
board = graphics.create_board(bwidth)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    # Center board to screen
    screen.blit(board, ((width-bwidth)/2,(height-bwidth)/2))
    pygame.display.flip()
    clock.tick(60)
"""
