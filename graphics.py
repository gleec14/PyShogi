import pygame

from ui import Window, Button
import shogi

# Color constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (212, 212, 212)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Game constants
PIECE_WIDTH = 40

def position_to_board(pos, bwidth):
    """ Converts position in board to graphical board space """
    tile_width = bwidth // 9
    # Center the pieces in their place on the board
    offset = tile_width // ((2 * tile_width) / (tile_width - PIECE_WIDTH))
    x = (pos[0] - 1) * tile_width + offset
    y = (pos[1] - 1) * tile_width + offset
    return (x, y)

def board_to_position(pos, bwidth):
    """ Converts a position in board space to the logical position in the game """
    tile_width = bwidth // 9
    # Center the pieces in their place on the board
    offset = tile_width // ((2 * tile_width) / (tile_width - PIECE_WIDTH))
    x = (pos[0] - offset) / tile_width + 1
    y = (pos[1] - offset) / tile_width + 1
    return (x, y)

def board_to_screen(pos, screen_width, screen_height, bwidth):
    """
    Converts a position in board space to a position in screen space
    """
    x = pos[0] + (screen_width-bwidth)/2
    y = pos[1] + (screen_height-bwidth)/2
    return (x, y)

def screen_to_board(pos, screen_width, screen_height, bwidth):
    """
    Converts a position in screen space to a position in board space
    """
    x = pos[0] - (screen_width-bwidth)/2
    y = pos[1] - (screen_height-bwidth)/2
    return (x, y)

def draw_promotion_prompt(screen, screen_width, screen_height, bwidth):
    board_center = position_to_board((3,4), bwidth)
    screen_center = board_to_screen(board_center, screen_width, screen_height, bwidth)
    # Prompt window
    window = Window(250, 100)
    window.set_position(screen_center)
    # Yes and No buttons
    yes_button = Button('yes', 100, 50, GREEN)
    yes_button.set_position((screen_center[0] + 10, screen_center[1] + 2 * window.height / 4))
    no_button = Button('no', 100, 50, RED)
    no_button.set_position((2 * screen_center[0] - 140, screen_center[1] + 2* window.height / 4))
    window.add_buttons([yes_button, no_button])
    # Draw window and buttons
    window.draw(screen)

    # Draw prompt at the center
    font = pygame.font.SysFont(None, 25)
    text_surf = font.render("Do you wish to promote?", True, BLACK)
    text_rect = text_surf.get_rect()
    board_center = position_to_board((5,4), bwidth)
    screen_center = board_to_screen(board_center, screen_width, screen_height, bwidth)
    text_rect.center = (screen_center[0] + 25, screen_center[1] + 25)
    screen.blit(text_surf, text_rect)

    yes_surf = font.render("Yes", True, BLACK)
    yes_rect = yes_surf.get_rect()
    board_center = position_to_board((4,5), bwidth)
    screen_center = board_to_screen(board_center, screen_width, screen_height, bwidth)
    yes_rect.center = (screen_center[0] + 10, screen_center[1] + 25)
    screen.blit(yes_surf, yes_rect)

    no_surf = font.render("No", True, BLACK)
    no_rect = no_surf.get_rect()
    board_center = position_to_board((6,5), bwidth)
    screen_center = board_to_screen(board_center, screen_width, screen_height, bwidth)
    no_rect.center = (screen_center[0] + 40, screen_center[1] + 25)
    screen.blit(no_surf, no_rect)

    return window
    """
    window_width = 250
    window_height = 100
    window = pygame.Surface((window_width, window_height))
    window.fill(WHITE)
    # Yes button
    yes_button = pygame.Surface((100, 50))
    yes_button.fill(GREEN)
    yes_button_rect = yes_button.get_rect()
    yes_button_rect.topleft = (screen_center[0] + 10, screen_center[1] + 2 * window_height / 4)
    # No button
    no_button = pygame.Surface((100, 50))
    no_button.fill(RED)
    no_button_rect = no_button.get_rect()
    no_button_rect.topleft = (2 * screen_center[0] - 140, screen_center[1] + 2* window_height / 4)
    screen.blit(window, screen_center)
    screen.blit(yes_button, yes_button_rect)
    screen.blit(no_button, no_button_rect)

    # Draw prompt at the center
    font = pygame.font.SysFont(None, 25)
    text_surf = font.render("Do you wish to promote?", True, BLACK)
    text_rect = text_surf.get_rect()
    board_center = position_to_board((5,4), bwidth)
    screen_center = board_to_screen(board_center, screen_width, screen_height, bwidth)
    text_rect.center = (screen_center[0] + 25, screen_center[1] + 25)
    screen.blit(text_surf, text_rect)

    yes_surf = font.render("Yes", True, BLACK)
    yes_rect = yes_surf.get_rect()
    board_center = position_to_board((4,5), bwidth)
    screen_center = board_to_screen(board_center, screen_width, screen_height, bwidth)
    yes_rect.center = (screen_center[0] + 10, screen_center[1] + 25)
    screen.blit(yes_surf, yes_rect)

    no_surf = font.render("No", True, BLACK)
    no_rect = no_surf.get_rect()
    board_center = position_to_board((6,5), bwidth)
    screen_center = board_to_screen(board_center, screen_width, screen_height, bwidth)
    no_rect.center = (screen_center[0] + 40, screen_center[1] + 25)
    screen.blit(no_surf, no_rect)

    return {'yes':yes_button_rect, 'no':no_button_rect}
    """

def update_piece_center(piece, pos):
    piece.rect.topleft = pos

def draw_pieces(screen, screen_width, screen_height, bwidth, shogi_board):
    """
    Draws pieces on top of board
    board       - pygame Surface
    shogi_board - game data
    """
    # Draw pieces in play
    tile_width = bwidth // 9
    for s in shogi_board.all_pieces:
        if s.on_board:
            board_position = position_to_board(s.position, bwidth)
            screen_position = board_to_screen(board_position, screen_width, screen_height, bwidth)
            update_piece_center(s, screen_position)
            screen.blit(s.image, screen_position)

    # Draw sente drop pieces
    x = 0
    for s in shogi_board.sente_dropcount:
        for p in shogi_board.sente_pieces:
            if p.id == s and shogi_board.sente_dropcount[s] > 0 and p.on_board is False:
                screen_position = board_to_screen((x, -tile_width), screen_width, screen_height, bwidth)
                update_piece_center(p, screen_position)
                screen.blit(p.image, screen_position)
                x += tile_width
                break

    # Draw gote drop pieces
    x = 0
    for s in shogi_board.gote_dropcount:
        for p in shogi_board.gote_pieces:
            if p.id == s and shogi_board.gote_dropcount[s] > 0 and p.on_board is False:
                screen_position = board_to_screen((x, bwidth), screen_width, screen_height, bwidth)
                update_piece_center(p, screen_position)
                screen.blit(p.image, screen_position)
                x += tile_width
                break

def draw_targets(positions, screen, screen_width, screen_height, bwidth):
    """ Draws the squares that are targeted by the selected piece """
    tile_width = bwidth // 9
    targets = []
    for pos in positions:
        # Get position of the targeted square
        board_pos = position_to_board(pos, bwidth)
        screen_pos = board_to_screen(board_pos, screen_width, screen_height, bwidth)
        # Draw the square
        s = pygame.Surface((PIECE_WIDTH, PIECE_WIDTH))
        s.set_alpha(255 * 0.5)
        s.fill(RED)
        targets.append(s.get_rect(topleft=screen_pos))
        screen.blit(s, screen_pos)
    return targets

def draw_board(screen, screen_width, screen_height, bwidth, colors=[WHITE, GREY]):
    """
    Draws the board onto the screen
    """
    width = bwidth
    # A Shogi board is a 9x9 square
    tile_width = width // 9
    board = pygame.Surface((width, width))
    stand = pygame.Surface((width, tile_width))
    y = 0
    # Create tiles, alternate their color
    while y < width:
        x = 0
        while x < width:
            row = y // tile_width
            col = x // tile_width
            pygame.draw.rect(
                            board,
                            colors[(row + col)%2],
                            pygame.Rect(x,y,tile_width,tile_width))
            x += tile_width
        y += tile_width
    board_loc = board_to_screen((0,0), screen_width, screen_height, bwidth)
    screen.blit(board, board_loc)

    # Draw drop piece stands
    x = 0
    while x < width:
        col = x // tile_width
        pygame.draw.rect(
                        stand,
                        (100, 0, 200),
                        pygame.Rect(x, 0, tile_width, tile_width))
        x += tile_width
    # Top stand
    board_loc1 = board_to_screen((0, -tile_width), screen_width, screen_height, bwidth)
    # Bottom stand
    board_loc2 = board_to_screen((0, bwidth), screen_width, screen_height, bwidth)
    screen.blit(stand, board_loc1)
    screen.blit(stand, board_loc2)
