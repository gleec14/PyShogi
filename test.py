from shogi import Shogi
import graphics
import pygame

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
shogi = Shogi(bwidth, debug=False)

targets = []
window = None
promote_prompt = False
selected_pos = None

def evaluate_player_action(turn, targets, promote_prompt, width, height, bwidth):
    mouse_click_pos = pygame.mouse.get_pos()
    valid_selection = False
    new_pos = None
    for piece in shogi.board.player_pieces[turn]:
        if piece.rect.collidepoint(mouse_click_pos):
            print("player {} {}".format(turn, piece.id))
            shogi.selected_piece = piece
            # If the piece is droppable, we want to update the spaces it
            # can be dropped at
            if shogi.selected_piece.on_board is False:
                shogi.selected_piece.update()
            valid_selection = True
            break
    # If we first clicked a valid piece and then tried to move it
    # Move the piece if the position clicked is a valid target
    if valid_selection is False and shogi.selected_piece is not None:
        if turn == 0:
            for target in targets:
                if target.collidepoint(mouse_click_pos):
                    new_board_pos = graphics.screen_to_board(target.topleft, width, height, bwidth)
                    new_pos = graphics.board_to_position(new_board_pos, bwidth)
                    print("New position is {}".format(new_pos))
                    # Drop vs move
                    if shogi.selected_piece.on_board is False:
                        shogi.move_selected_piece(new_pos, True, False)
                    else:
                        # Give player the option to promote if possible
                        if shogi.selected_piece.promotable:
                            if new_pos[1] > 6 or shogi.selected_piece.position[1] > 6:
                                print("promote")
                                promote_prompt = True
                                valid_selection = True
                            else:
                                shogi.move_selected_piece(new_pos, False, False)
                        else:
                            shogi.move_selected_piece(new_pos, False, False)
                    break
        else:
            for target in targets:
                if target.collidepoint(mouse_click_pos):
                    new_board_pos = graphics.screen_to_board(target.topleft, width, height, bwidth)
                    new_pos = graphics.board_to_position(new_board_pos, bwidth)
                    print("New position is {}".format(new_pos))
                    # Drop vs move
                    if shogi.selected_piece.on_board is False:
                        shogi.move_selected_piece(new_pos, True, False)
                    else:
                        # Give player the option to promote if possible
                        if shogi.selected_piece.promotable:
                            if new_pos[1] < 4 or shogi.selected_piece.position[1] < 4:
                                print("promote")
                                promote_prompt = True
                                valid_selection = True
                            else:
                                shogi.move_selected_piece(new_pos, False, False)
                        else:
                            shogi.move_selected_piece(new_pos, False, False)
                    break
    if valid_selection is False:
        shogi.selected_piece = None
        targets = []
    return promote_prompt, new_pos

def evaluate_promotion(window):
    mouse_click_pos = pygame.mouse.get_pos()
    button = window.click_button(mouse_click_pos)
    if button is not None:
        if button.name == "yes":
            shogi.move_selected_piece(selected_pos, False, True)
        else:
            shogi.move_selected_piece(selected_pos, False, False)
        shogi.selected_piece = None
        targets = []
        return False
    return True


while not done:
    # Event Handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not promote_prompt:
                promote_prompt, selected_pos = evaluate_player_action(shogi.turn, targets, promote_prompt, width, height, bwidth)
            else:
                promote_prompt = evaluate_promotion(window)
    # Drawing
    # Center board to screen
    graphics.draw_board(screen, width, height, bwidth)
    # Draw the pieces
    graphics.draw_pieces(screen, width, height, bwidth, shogi.board)
    # Draw targets if a piece has been clicked
    if shogi.selected_piece:
        targets = graphics.draw_targets(shogi.selected_piece_target_positions, screen, width, height, bwidth)
    # Draw promotion prompt
    if promote_prompt:
        window = graphics.draw_promotion_prompt(screen, width, height, bwidth)
    pygame.display.flip()
    clock.tick(60)
