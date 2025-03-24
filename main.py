#!/usr/bin/env python
from game.go import Board, opponent_color
from game.ui import UI
import pygame
import sys
import time
from os.path import join
import os

def get_resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Match:
    def __init__(self, game_mode="PVP", board_size=19):
        """Initialize game state."""
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 20)
        self.dir_save = None  # Initialize dir_save to None
        
        # Select game mode and board size if not provided
        if game_mode == "PVP" and board_size == 19:
            self.game_mode, self.board_size = self._select_game_mode_and_board_size()
        else:
            self.game_mode = game_mode
            self.board_size = board_size
        
        # Initialize board with Black starting
        self.board = Board(board_size=self.board_size, next_color='black')
        self.ui = UI(board_size=self.board_size)
        self.ui.initialize()
        self.game_over = False
        self.last_move_was_pass = False

    @property
    def winner(self):
        return self.board.winner

    @property
    def next(self):
        return self.board.next

    @property
    def counter_move(self):
        return self.board.counter_move

    def start(self):
        self._start_game()

    def _select_game_mode_and_board_size(self):
        """
        Multi-page selection screen for board size and game mode
        First page: Welcome screen with Rules and Play Game buttons
        Second page: Board Size Selection
        Third page: Game Mode Selection
        """
        pygame.init()
        screen_width, screen_height = 600, 500
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption('Go Game - Welcome')
        
        # Colors
        BUTTON_COLOR = (220, 220, 0)  # Yellow buttons
        HIGHLIGHT_COLOR = (100, 200, 10)  # Green highlight
        SPLASH_TEXT_COLOR = (255, 255, 255)  # White text for splash screen
        MENU_TEXT_COLOR = (0, 0, 0)  # Black text for menus
        TEXT_COLOR = (255, 255, 255)  # White text for better visibility on background
        
        # Fonts
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        button_font = pygame.font.SysFont('Arial', 22)
        subtitle_font = pygame.font.SysFont('Arial', 20)
        rules_font = pygame.font.SysFont('Arial', 16)
        
        # Load and scale background image
        try:
            bg_image = pygame.image.load(get_resource_path('game/images/ramin.jpg'))
            bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))
        except pygame.error:
            print("Warning: Could not load background image")
            bg_image = None

        def draw_welcome_screen():
            if bg_image:
                screen.blit(bg_image, (0, 0))
            else:
                screen.fill((0, 0, 0))  # Black fallback if image fails to load
            
            # Create semi-transparent overlay
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            screen.blit(overlay, (0, 0))
            
            # Draw title
            title = title_font.render("GO GAME", True, SPLASH_TEXT_COLOR)
            title_rect = title.get_rect(center=(screen_width//2, screen_height//4))
            screen.blit(title, title_rect)
            
            # Draw buttons
            button_width, button_height = 200, 50
            button_spacing = 40
            
            # Play Game button
            play_button = pygame.Rect((screen_width - button_width)//2,
                                    screen_height//2 - button_height - button_spacing//2,
                                    button_width, button_height)
            pygame.draw.rect(screen, BUTTON_COLOR, play_button, border_radius=10)
            play_text = button_font.render("Play Game", True, MENU_TEXT_COLOR)
            play_text_rect = play_text.get_rect(center=play_button.center)
            screen.blit(play_text, play_text_rect)
            
            # Rules button
            rules_button = pygame.Rect((screen_width - button_width)//2,
                                     screen_height//2 + button_spacing//2,
                                     button_width, button_height)
            pygame.draw.rect(screen, BUTTON_COLOR, rules_button, border_radius=10)
            rules_text = button_font.render("Rules", True, MENU_TEXT_COLOR)
            rules_text_rect = rules_text.get_rect(center=rules_button.center)
            screen.blit(rules_text, rules_text_rect)
            
            return play_button, rules_button

        def draw_rules_screen():
            if bg_image:
                screen.blit(bg_image, (0, 0))
            else:
                screen.fill((0, 0, 0))  # Black fallback if image fails to load
            
            # Create semi-transparent overlay
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(180)  # More opaque for better text readability
            screen.blit(overlay, (0, 0))
            
            # Load and display rules
            try:
                rules_path = get_resource_path(os.path.join('img', 'Rules of Go Game.txt'))
                with open(rules_path, 'r') as f:
                    rules_text = f.read()
            except Exception as e:
                print(f"Error loading rules: {e}")
                rules_text = "Error: Could not load rules file."
            
            # Initialize scrolling variables
            scroll_y = 0
            scroll_speed = 25
            max_scroll = 0  # Will be calculated after rendering text
            
            # Back button
            button_width, button_height = 100, 40
            back_button = pygame.Rect(20, screen_height - button_height - 20,
                                    button_width, button_height)

            # Create a loop for the rules screen
            viewing_rules = True
            while viewing_rules:
                # Handle events first
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return None
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if back_button.collidepoint(event.pos):
                            return back_button
                        # Scroll with mouse wheel
                        if event.button == 4:  # Mouse wheel up
                            scroll_y = min(0, scroll_y + scroll_speed)
                        if event.button == 5:  # Mouse wheel down
                            scroll_y = max(-(max_scroll - screen_height + 150), scroll_y - scroll_speed)
                    if event.type == pygame.KEYDOWN:
                        # Scroll with arrow keys
                        if event.key == pygame.K_UP:
                            scroll_y = min(0, scroll_y + scroll_speed)
                        if event.key == pygame.K_DOWN:
                            scroll_y = max(-(max_scroll - screen_height + 150), scroll_y - scroll_speed)

                # Clear screen and redraw background
                if bg_image:
                    screen.blit(bg_image, (0, 0))
                else:
                    screen.fill((0, 0, 0))  # Black fallback if image fails to load
                screen.blit(overlay, (0, 0))

                # Draw title
                title = title_font.render("Rules of Go", True, SPLASH_TEXT_COLOR)
                title_rect = title.get_rect(center=(screen_width//2, 40))
                screen.blit(title, title_rect)
                
                # Draw rules text with scrolling
                y_offset = 100 + scroll_y
                line_spacing = 25
                max_scroll = 0  # Reset max_scroll for recalculation
                
                for line in rules_text.split('\n'):
                    if line.strip():  # Skip empty lines
                        if line.strip().endswith(':') or line.strip().isupper():  # Section headers
                            text = subtitle_font.render(line, True, SPLASH_TEXT_COLOR)
                        else:
                            text = rules_font.render(line, True, SPLASH_TEXT_COLOR)
                        text_rect = text.get_rect(left=50, top=y_offset)
                        
                        # Only draw if within visible area
                        if y_offset + text_rect.height > 0 and y_offset < screen_height - button_height - 40:
                            screen.blit(text, text_rect)
                        
                        y_offset += line_spacing
                        max_scroll = max(max_scroll, y_offset)

                # Draw scroll indicators if content is scrollable
                if max_scroll > screen_height:
                    # Up arrow
                    if scroll_y < 0:
                        pygame.draw.polygon(screen, SPLASH_TEXT_COLOR, 
                            [(screen_width - 30, 60), (screen_width - 20, 40), (screen_width - 10, 60)])
                    
                    # Down arrow
                    if scroll_y > -(max_scroll - screen_height + 150):
                        pygame.draw.polygon(screen, SPLASH_TEXT_COLOR,
                            [(screen_width - 30, screen_height - 60), 
                             (screen_width - 20, screen_height - 40),
                             (screen_width - 10, screen_height - 60)])

                # Draw back button
                pygame.draw.rect(screen, BUTTON_COLOR, back_button, border_radius=10)
                back_text = button_font.render("Back", True, MENU_TEXT_COLOR)
                back_text_rect = back_text.get_rect(center=back_button.center)
                screen.blit(back_text, back_text_rect)

                pygame.display.flip()

            return back_button

        # Welcome screen loop
        while True:
            play_button, rules_button = draw_welcome_screen()
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None, None
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if play_button.collidepoint(mouse_pos):
                        # Continue to board size selection
                        return_to_welcome = False
                        break
                    elif rules_button.collidepoint(mouse_pos):
                        # Show rules screen
                        back_button = draw_rules_screen()
                        if back_button:  # If back button was clicked
                            continue  # Return to welcome screen loop
                        else:  # If window was closed
                            return None, None
            
            if 'return_to_welcome' in locals() and not return_to_welcome:
                break
        
        # Logo splash screen
        start_time = time.time()
        while time.time() - start_time < 3:  # 3 second delay
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # Draw background
            if bg_image:
                screen.blit(bg_image, (0, 0))
            else:
                screen.fill((0, 0, 0))  # Black fallback if image fails to load
            
            # Create semi-transparent overlay for better text visibility
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)  # 50% transparent
            screen.blit(overlay, (0, 0))
            
            # Draw game title
            title = title_font.render("GO GAME", True, SPLASH_TEXT_COLOR)
            title_rect = title.get_rect(center=(screen_width//2, screen_height//2))
            screen.blit(title, title_rect)
            
            # Add a loading text
            loading_font = pygame.font.SysFont('Arial', 20)
            loading_text = loading_font.render("Loading...", True, SPLASH_TEXT_COLOR)
            loading_rect = loading_text.get_rect(center=(screen_width//2, screen_height//2 + 50))
            screen.blit(loading_text, loading_rect)
            
            pygame.display.flip()
            pygame.time.wait(100)  # Small delay to prevent high CPU usage
        
        # Clear screen before moving to board size selection
        screen.fill((0, 0, 0))  # Black fallback if image fails to load
        pygame.display.flip()
        
        # Board size buttons with compact layout
        button_width, button_height = 250, 60
        button_spacing = 20
        board_sizes = [
            {"size": 9, "rect": pygame.Rect(0, 0, button_width, button_height), "label": "9x9 - Beginner"},
            {"size": 13, "rect": pygame.Rect(0, 0, button_width, button_height), "label": "13x13 - Intermediate"},
            {"size": 19, "rect": pygame.Rect(0, 0, button_width, button_height), "label": "19x19 - Professional"}
        ]
        
        # Dynamically calculate button positions for perfect centering
        total_height = len(board_sizes) * button_height + (len(board_sizes) - 1) * button_spacing
        start_x = (screen_width - button_width) // 2
        start_y = 220
        
        # Adjust button positions vertically
        for i, board_option in enumerate(board_sizes):
            board_option['rect'].x = start_x
            board_option['rect'].y = start_y + (button_height + button_spacing) * i
        
        # Game mode buttons with improved layout
        game_modes = [
            {"mode": "PVP", "rect": pygame.Rect(100, 180, 400, 80), "label": "Player vs Player"},
            {"mode": "AI_HUMAN", "rect": pygame.Rect(100, 280, 400, 80), "label": "Player vs AI"}
        ]
        
        # Selection state
        selected_size = None
        selected_mode = None
        current_page = 'BOARD_SIZE'
        
        while True:
            screen.fill((0, 0, 0))  # Black fallback if image fails to load
            
            # Page logic
            if current_page == 'BOARD_SIZE':
                # Draw background
                if bg_image:
                    screen.blit(bg_image, (0, 0))
                else:
                    screen.fill((0, 0, 0))  # Black fallback

                # Create semi-transparent overlay
                overlay = pygame.Surface((screen_width, screen_height))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(128)
                screen.blit(overlay, (0, 0))

                # Title for board size selection
                title = title_font.render("Select Board Size", True, SPLASH_TEXT_COLOR)
                title_rect = title.get_rect(centerx=screen_width//2, top=50)
                screen.blit(title, title_rect)
                
                # Subtitle
                subtitle = subtitle_font.render("Choose a board size that suits your skill level", True, SPLASH_TEXT_COLOR)
                subtitle_rect = subtitle.get_rect(centerx=screen_width//2, top=100)
                screen.blit(subtitle, subtitle_rect)
                
                # Draw board size buttons
                for board_option in board_sizes:
                    # Button background
                    pygame.draw.rect(screen, BUTTON_COLOR, board_option['rect'], border_radius=10)
                    pygame.draw.rect(screen, BUTTON_COLOR, board_option['rect'], width=2, border_radius=10)
                    
                    # Button text
                    size_text = button_font.render(board_option['label'], True, MENU_TEXT_COLOR)
                    size_text_rect = size_text.get_rect(center=board_option['rect'].center)
                    screen.blit(size_text, size_text_rect)
                
                # Highlight selected board size
                if selected_size is not None:
                    for board_option in board_sizes:
                        if board_option['size'] == selected_size:
                            pygame.draw.rect(screen, HIGHLIGHT_COLOR, board_option['rect'], width=4, border_radius=10)
            
            elif current_page == 'GAME_MODE':
                # Draw background
                if bg_image:
                    screen.blit(bg_image, (0, 0))
                else:
                    screen.fill((0, 0, 0))  # Black fallback

                # Create semi-transparent overlay
                overlay = pygame.Surface((screen_width, screen_height))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(128)
                screen.blit(overlay, (0, 0))

                # Title for game mode selection
                title = title_font.render("Select Game Mode", True, SPLASH_TEXT_COLOR)
                title_rect = title.get_rect(centerx=screen_width//2, top=50)
                screen.blit(title, title_rect)
                
                # Subtitle
                subtitle = subtitle_font.render("Choose how you want to play Go", True, SPLASH_TEXT_COLOR)
                subtitle_rect = subtitle.get_rect(centerx=screen_width//2, top=100)
                screen.blit(subtitle, subtitle_rect)
                
                # Draw game mode buttons
                for mode_option in game_modes:
                    # Button background
                    pygame.draw.rect(screen, BUTTON_COLOR, mode_option['rect'], border_radius=10)
                    pygame.draw.rect(screen, BUTTON_COLOR, mode_option['rect'], width=2, border_radius=10)
                    
                    # Button text
                    mode_text = button_font.render(mode_option['label'], True, MENU_TEXT_COLOR)
                    mode_text_rect = mode_text.get_rect(center=mode_option['rect'].center)
                    screen.blit(mode_text, mode_text_rect)
                
                # Highlight selected game mode
                if selected_mode is not None:
                    for mode_option in game_modes:
                        if mode_option['mode'] == selected_mode:
                            pygame.draw.rect(screen, HIGHLIGHT_COLOR, mode_option['rect'], width=4, border_radius=10)
                
                # Draw back instruction
                back_text = subtitle_font.render("Press ESC to go back", True, MENU_TEXT_COLOR)
                back_rect = back_text.get_rect(center=(screen_width//2, screen_height - 30))
                screen.blit(back_text, back_rect)
            
            pygame.display.flip()
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return "PVP", 19  # Default to PVP and 19x19 if window is closed
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    
                    if current_page == 'BOARD_SIZE':
                        # Board size selection
                        for board_option in board_sizes:
                            if board_option['rect'].collidepoint(mouse_pos):
                                selected_size = board_option['size']
                                current_page = 'GAME_MODE'
                                break
                    
                    elif current_page == 'GAME_MODE':
                        # Game mode selection
                        for mode_option in game_modes:
                            if mode_option['rect'].collidepoint(mouse_pos):
                                selected_mode = mode_option['mode']
                                # Return selected mode and size
                                return selected_mode, selected_size
            
            # Optional: Add a back button or key to return to board size selection
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE] and current_page == 'GAME_MODE':
                current_page = 'BOARD_SIZE'

    def _handle_game_events(self):
        """Handle game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
                pygame.quit()  # Properly quit pygame
                return True
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Handle UI button clicks first
                click_result = self.ui.handle_click(mouse_pos)
                
                if click_result == 'home':
                    # Properly clean up the current game state
                    pygame.display.quit()
                    pygame.display.init()
                    
                    # Reset the game state
                    self.game_over = False
                    self.last_move_was_pass = False
                    
                    # Get new game mode and board size
                    self.game_mode, self.board_size = self._select_game_mode_and_board_size()
                    if self.game_mode is None:  # If window was closed during selection
                        pygame.quit()
                        return True
                        
                    # Initialize new board and UI
                    self.board = Board(board_size=self.board_size, next_color='black')
                    self.ui = UI(board_size=self.board_size)
                    self.ui.initialize()  # Make sure to initialize the new UI
                    return True
                
                elif click_result == 'restart':
                    self._restart_game()
                    return True
                
                elif click_result == 'pass':
                    if self.last_move_was_pass:
                        # Both players passed consecutively
                        self._show_game_result()
                        self.game_over = True
                    else:
                        # First pass
                        self.last_move_was_pass = True
                        self.board.pass_move()
                        
                        # If AI's turn after pass
                        if self.game_mode == "AI_HUMAN" and self.board.next == 'white':
                            pygame.time.wait(500)
                            self._make_ai_move()
                    return True
                
                elif click_result == 'music':
                    # Music was toggled, just update the display
                    self.ui.draw_game_state(self.board.next, self.board)
                    return True
                
                # Handle stone placement if no button was clicked
                if not self.game_over and click_result is None:
                    board_pos = self.ui.pixel_to_board_coords(*mouse_pos)
                    if board_pos is not None:  # Only proceed if we got valid board coordinates
                        if self.game_mode == "PVP" or (self.game_mode == "AI_HUMAN" and self.board.next == 'black'):
                            success, captured = self.board.put_stone(board_pos)
                            if success:
                                # Reset pass flag since a stone was placed
                                self.last_move_was_pass = False
                                
                                # Remove captured stones
                                for captured_point in captured:
                                    self.ui.remove(captured_point)
                                
                                # Draw the new stone
                                self.ui.draw(board_pos, opponent_color(self.board.next))
                                
                                # Update the game state display
                                self.ui.draw_game_state(self.board.next, self.board)
                                
                                # If AI's turn, make its move
                                if self.game_mode == "AI_HUMAN" and self.board.next == 'white':
                                    pygame.time.wait(500)
                                    self._make_ai_move()
                            else:
                                # Check if it's a suicide move
                                self.board.board[board_pos[0]][board_pos[1]] = self.board.next
                                own_group = self.board._get_group(*board_pos)
                                is_suicide = self.board._count_liberties(own_group) == 0 and not self.board._find_captured_groups(self.board._get_opponent_color())
                                self.board.board[board_pos[0]][board_pos[1]] = None
                                
                                if is_suicide:
                                    self.ui.show_popup("Invalid Move: Suicide not allowed!")
                                    # Redraw the game state to ensure everything is displayed correctly
                                    self.ui.draw_game_state(self.board.next, self.board)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and not self.game_over:  # Pass move
                    if self.last_move_was_pass:
                        # Both players passed consecutively
                        self._show_game_result()
                        self.game_over = True
                    else:
                        # First pass
                        self.last_move_was_pass = True
                        self.board.pass_move()
                    
                    # If AI's turn after pass
                    if self.game_mode == "AI_HUMAN" and self.board.next == 'white':
                        pygame.time.wait(500)
                        self._make_ai_move()
        
        return True

    def _start_game(self):
        """Main game loop."""
        # Initialize game state display
        self.ui.draw_game_state(self.board.next, self.board)
        pygame.display.update()
        
        while not self.game_over:
            # Always update game state at the start of each loop
            self.ui.draw_game_state(self.board.next, self.board)
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                    pygame.quit()
                    sys.exit(0)
                    
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Handle UI button clicks first
                    click_result = self.ui.handle_click(mouse_pos)
                    
                    if click_result == 'pass':
                        if self.last_move_was_pass:
                            # Both players passed consecutively
                            self._show_game_result()
                            self.game_over = True
                        else:
                            # First pass
                            self.last_move_was_pass = True
                            self.board.pass_move()
                            # Update display after pass
                            self.ui.draw_game_state(self.board.next, self.board)
                            pygame.display.update()
                            
                            # If AI's turn after pass
                            if self.game_mode == "AI_HUMAN" and self.board.next == 'white':
                                pygame.time.wait(500)
                                self._make_ai_move()
                        continue
                    
                    elif click_result == 'home':
                        # Properly clean up the current game state
                        pygame.display.quit()
                        pygame.display.init()
                        
                        # Reset the game state
                        self.game_over = False
                        self.last_move_was_pass = False
                        
                        # Get new game mode and board size
                        self.game_mode, self.board_size = self._select_game_mode_and_board_size()
                        if self.game_mode is None:  # If window was closed during selection
                            pygame.quit()
                            sys.exit(0)
                            
                        # Initialize new board and UI
                        self.board = Board(board_size=self.board_size, next_color='black')
                        self.ui = UI(board_size=self.board_size)
                        self.ui.initialize()
                        # Make sure to draw initial state
                        self.ui.draw_game_state(self.board.next, self.board)
                        pygame.display.update()
                        continue
                    
                    elif click_result == 'restart':
                        self._restart_game()
                        continue
                    
                    elif click_result == 'music':
                        # Music was toggled, just update the display
                        self.ui.draw_game_state(self.board.next, self.board)
                        pygame.display.update()
                        continue
                    
                    # Handle stone placement if no button was clicked
                    if not self.game_over:
                        board_pos = self.ui.pixel_to_board_coords(*mouse_pos)
                        if board_pos is not None:  # Only proceed if we got valid board coordinates
                            if self.game_mode == "PVP" or (self.game_mode == "AI_HUMAN" and self.board.next == 'black'):
                                success, captured = self.board.put_stone(board_pos)
                                if success:
                                    # Reset pass flag since a stone was placed
                                    self.last_move_was_pass = False
                                    
                                    # Remove captured stones
                                    for captured_point in captured:
                                        self.ui.remove(captured_point)
                                    
                                    # Draw the new stone
                                    self.ui.draw(board_pos, opponent_color(self.board.next))
                                    
                                    # Update the game state display
                                    self.ui.draw_game_state(self.board.next, self.board)
                                    pygame.display.update()
                                    
                                    # If AI's turn, make its move
                                    if self.game_mode == "AI_HUMAN" and self.board.next == 'white':
                                        pygame.time.wait(500)
                                        self._make_ai_move()
                                else:
                                    # Check if it's a suicide move
                                    self.board.board[board_pos[0]][board_pos[1]] = self.board.next
                                    own_group = self.board._get_group(*board_pos)
                                    is_suicide = self.board._count_liberties(own_group) == 0 and not self.board._find_captured_groups(self.board._get_opponent_color())
                                    self.board.board[board_pos[0]][board_pos[1]] = None
                                    
                                    if is_suicide:
                                        self.ui.show_popup("Invalid Move: Suicide not allowed!")
                                        # Redraw the game state
                                        self.ui.draw_game_state(self.board.next, self.board)
                                        pygame.display.update()
            
            # AI move handling
            if (self.game_mode == "AI_HUMAN" and self.board.next == 'white') or \
               (self.game_mode == "AI_AI" and not self.game_over):
                pygame.time.wait(500)
                self._make_ai_move()
            
            # Small delay to prevent high CPU usage
            pygame.time.wait(10)
            
        self.time_elapsed = time.time() - self.time_elapsed
        if self.dir_save:
            self.ui.save_image(join(self.dir_save, 'final_board.png'))

    def _make_ai_move(self):
        """Advanced AI player with strategic move selection."""
        import random
        import math
        import copy

        def evaluate_move(point, color):
            """Evaluate the strategic value of a potential move."""
            if not self.board.is_valid_move(point):
                return float('-inf')
            
            x, y = point
            score = 0
            
            # Proximity to existing stones (encourage clustering)
            nearby_stones = 0
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                        if self.board.board[nx][ny] is not None:
                            nearby_stones += 1
            score += nearby_stones * 2
            
            # Potential stone capture
            test_board = copy.deepcopy(self.board)
            test_board.board[x][y] = color
            captured_groups = test_board._find_captured_groups(opponent_color(color))
            score += len(captured_groups) * 10
            
            # Territory control (proximity to board center)
            center_x, center_y = self.board_size // 2, self.board_size // 2
            distance_to_center = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            score += (self.board_size - distance_to_center)
            
            # Avoid moves near board edges
            if x < 2 or x > self.board_size - 3 or y < 2 or y > self.board_size - 3:
                score -= 5
            
            return score

        # Find all valid moves
        valid_moves = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board.is_valid_move((i, j)):
                    valid_moves.append((i, j))
        
        if not valid_moves:
            # If no valid moves, pass
            return self.board.pass_move()
        
        # Determine current player color
        current_color = self.board.next
        
        # Rank moves by strategic value
        ranked_moves = [(move, evaluate_move(move, current_color)) for move in valid_moves]
        ranked_moves.sort(key=lambda x: x[1], reverse=True)
        
        # Select top moves, with some randomness to prevent predictability
        top_moves = ranked_moves[:max(3, len(ranked_moves) // 2)]
        best_move = random.choice(top_moves)[0]
        
        # Try to place the stone
        success, captured = self.board.put_stone(best_move)
        if success:
            # Remove captured stones from the board
            for captured_point in captured:
                self.ui.remove(captured_point)
            
            # Draw the new stone 
            self.ui.draw(best_move, current_color)
            return True
        
        return False

    def _show_game_result(self):
        """Display the final game result."""
        # Calculate final scores
        scores = self.board.get_score()
        
        # Show game over screen and get return status
        if not self.ui.show_game_over(scores['black'], scores['white'], self.board):
            pygame.quit()
            sys.exit()
            
        # Reset game state but keep the board visible
        self.game_over = False
        self.last_move_was_pass = False
        
        # Make sure the board and UI are properly redrawn
        self.ui.draw_board()
        self.ui.draw_game_state(self.board.next, self.board)

    def _restart_game(self):
        """Restart the game with the same settings."""
        # Create a new board with the same size
        self.board = Board(board_size=self.board_size, next_color='black')
        
        # Reset game state
        self.game_over = False
        self.last_move_was_pass = False
        
        # Clear the screen
        self.ui.screen.fill((255, 255, 255))
        
        # Draw the empty board
        self.ui.draw_board()
        
        # Draw the initial game state
        self.ui.draw_game_state(self.board.next, self.board)
        
        pygame.display.update()

    def end_game(self):
        """Clean up and end the game."""
        try:
            if hasattr(self, 'dir_save') and self.dir_save:
                self.ui.save_image(join(self.dir_save, 'final_board.png'))
        except Exception:
            pass  # Ignore any saving errors on exit
        
        pygame.quit()
        sys.exit()

def main():
    match = Match()
    match.start()

if __name__ == '__main__':
    main()
