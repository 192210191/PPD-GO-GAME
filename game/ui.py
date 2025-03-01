import pygame
import os
import sys

"""
This file is the GUI on top of the game backend.
"""

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

BACKGROUND = resource_path('game/images/ramin.jpg')
HOME_ICON = resource_path('game/images/home.png')
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BACKGROUND_COLOR = (219, 186, 130)


def get_rbg(color):
    if color == 'white':
        return 255, 255, 255
    elif color == 'black':
        return 0, 0, 0
    else:
        return 0, 133, 211


class UI:
    def __init__(self, board_size=19):
        """Create, initialize and draw an empty board."""
        self.board_size = board_size
        # Adjust cell size only for 19x19 to fit screen
        self.cell_size = 30 if board_size == 19 else 40
        self.margin = 45  # margin from edge
        
        # Calculate board dimensions
        self.board_pixels = (self.board_size - 1) * self.cell_size
        self.outline = pygame.Rect(self.margin, self.margin, self.board_pixels, self.board_pixels)
        self.screen = None
        self.background = None
        self.font = None
        # Keep original score rect but adjust width for 19x19
        self.score_rect = pygame.Rect(45, self.margin + self.board_pixels + 15, 
                                    self.board_pixels + 100, 35)
        
        # Pass button
        self.pass_button = None
        self.pass_text = None
        
        # Restart button
        self.restart_button = None
        self.restart_text = None

        # Home button
        self.home_button = None
        self.home_icon = None

    def initialize(self):
        """Initialize the game board."""
        pygame.init()
        pygame.display.set_caption('Go Game')
        
        # Set window size based on board size with minimum width
        window_width = max(820, self.margin * 2 + self.board_pixels + 200)
        window_height = self.margin * 2 + self.board_pixels + 100
        self.screen = pygame.display.set_mode((window_width, window_height), 0, 32)
        self.background = pygame.image.load(BACKGROUND).convert()
        self.font = pygame.font.SysFont('Arial', 20)

        # Initialize home button - position in top left corner
        self.home_icon = pygame.image.load(HOME_ICON)
        self.home_icon = pygame.transform.scale(self.home_icon, (30, 30))  # Scale the icon to appropriate size
        self.home_button = pygame.Rect(10, 10, 30, 30)  # Position it in the top-left corner
        
        # Initialize pass button - position relative to board
        button_y = self.margin + self.board_pixels + 15
        self.pass_button = pygame.Rect(self.margin + self.board_pixels - 100, button_y, 100, 30)
        self.pass_text = self.font.render('Pass Turn', True, (0, 0, 0))

        # Initialize restart button - position below pass button
        restart_y = button_y + 40
        self.restart_button = pygame.Rect(self.margin + self.board_pixels - 100, restart_y, 100, 30)
        self.restart_text = self.font.render('Restart', True, (0, 0, 0))
        
        # Draw the board outline
        pygame.draw.rect(self.background, BLACK, self.outline, 3)
        
        # Draw the grid lines
        for i in range(self.board_size):
            # Vertical lines
            start_pos = (self.margin + (self.cell_size * i), self.margin)
            end_pos = (self.margin + (self.cell_size * i), self.margin + self.board_pixels)
            pygame.draw.line(self.background, BLACK, start_pos, end_pos, 1)
            
            # Horizontal lines
            start_pos = (self.margin, self.margin + (self.cell_size * i))
            end_pos = (self.margin + self.board_pixels, self.margin + (self.cell_size * i))
            pygame.draw.line(self.background, BLACK, start_pos, end_pos, 1)

        # Draw star points (hoshi)
        if self.board_size == 19:
            star_points = [(3, 3), (3, 9), (3, 15),
                          (9, 3), (9, 9), (9, 15),
                          (15, 3), (15, 9), (15, 15)]
        elif self.board_size == 13:
            star_points = [(3, 3), (3, 9),
                          (6, 6),
                          (9, 3), (9, 9)]
        else:  # 9x9
            star_points = [(2, 2), (2, 6),
                          (4, 4),
                          (6, 2), (6, 6)]

        for x, y in star_points:
            pos = (self.margin + x * self.cell_size, self.margin + y * self.cell_size)
            pygame.draw.circle(self.background, BLACK, pos, 5, 0)

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.home_icon, self.home_button)
        pygame.display.update()

    def coords(self, point):
        """Return the coordinate of a stone drawn on board"""
        return (self.margin + point[0] * self.cell_size, 
                self.margin + point[1] * self.cell_size)

    def leftup_corner(self, point):
        """Return the top-left corner for the area to clear when removing a stone"""
        return (self.margin - 20 + point[0] * self.cell_size, 
                self.margin - 20 + point[1] * self.cell_size)

    def draw(self, point, color, size=15):
        """Draw a stone at the specified intersection with a growing animation effect."""
        rgb_color = get_rbg(color)
        position = self.coords(point)
        
        # Animate stone placement with growing effect
        for r in range(5, size + 1, 2):
            pygame.draw.circle(self.screen, rgb_color, position, r, 0)
            pygame.display.update()
            pygame.time.wait(10)  # Short delay for smooth animation
            
            # If not at final size, clear the previous circle
            if r < size:
                # Draw a slightly larger circle in background color to clean up
                pygame.draw.circle(self.screen, BACKGROUND_COLOR, position, r + 1, 0)
                
                # Redraw the grid lines that might have been covered
                # Get the grid area around the stone
                area_rect = pygame.Rect(position[0] - r - 1, position[1] - r - 1, 
                                      (r + 1) * 2, (r + 1) * 2)
                stone_area = self.background.subsurface(area_rect).copy()
                self.screen.blit(stone_area, area_rect)
        
        # Draw final stone
        pygame.draw.circle(self.screen, rgb_color, position, size, 0)
        pygame.display.update()

    def remove(self, point):
        """Remove a stone from the board at the given point."""
        x, y = point
        screen_x = self.margin + (x * self.cell_size)
        screen_y = self.margin + (y * self.cell_size)
        
        # Get the corresponding area from the background (which has only the grid)
        area_rect = pygame.Rect(screen_x - 20, screen_y - 20, self.cell_size, self.cell_size)
        stone_area = self.background.subsurface(area_rect).copy()
        
        # Blit the clean background area (with only grid lines) onto the screen
        self.screen.blit(stone_area, area_rect)
        pygame.display.update()

    def save_image(self, path_to_save):
        pygame.image.save(self.screen, path_to_save)

    def pixel_to_board_coords(self, x, y):
        """Convert pixel coordinates to board coordinates.
        Returns None if click is outside the valid board area."""
        if self.outline.collidepoint(x, y):
            board_x = int(round(((x - self.margin) / self.cell_size), 0))
            board_y = int(round(((y - self.margin) / self.cell_size), 0))
            # Ensure coordinates are within valid board range (1-19)
            if 1 <= board_x <= self.board_size and 1 <= board_y <= self.board_size:
                return (board_x, board_y)
        return None

    def update_score_display(self, black_score, white_score, game_over=False):
        """Update the score display at the bottom of the board."""
        # Clear the score area
        pygame.draw.rect(self.screen, (255, 255, 255), self.score_rect)
        
        # Create score text
        black_text = f"Black: {black_score:.1f}"
        white_text = f"White: {white_score:.1f}"
        
        # Render score text
        black_surface = self.font.render(black_text, True, (0, 0, 0))
        white_surface = self.font.render(white_text, True, (0, 0, 0))
        
        # Position and display scores - adjust spacing for 19x19
        spacing = 200 if self.board_size == 19 else 250
        self.screen.blit(black_surface, (50, self.margin + self.board_pixels + 20))
        self.screen.blit(white_surface, (50 + spacing, self.margin + self.board_pixels + 20))
        
        # If game is over, display winner
        if game_over:
            winner = "Black" if black_score > white_score else "White"
            winner_text = f"Winner: {winner}!"
            winner_surface = self.font.render(winner_text, True, (0, 100, 0))
            self.screen.blit(winner_surface, (50 + spacing * 2, self.margin + self.board_pixels + 20))
        
        pygame.display.update()

    def draw_game_state(self, current_player, board):
        """Draw game state information including current player, scores, and pass button"""
        # Clear the info area
        info_rect = pygame.Rect(self.margin + self.board_pixels + 20, self.margin + 20, 180, 200)
        pygame.draw.rect(self.screen, BACKGROUND_COLOR, info_rect)
        
        # Get current scores
        scores = board.get_score()
        
        # Colors for different sections
        current_player_bg = (135, 206, 235)  # Sky blue
        black_score_bg = (144, 238, 144)  # Light green
        white_score_bg = (255, 182, 193)  # Light pink
        
        # Draw current player indicator with rounded rectangle background
        current_rect = pygame.Rect(self.margin + self.board_pixels + 25, self.margin + 25, 160, 30)
        pygame.draw.rect(self.screen, current_player_bg, current_rect, border_radius=15)
        player_text = self.font.render(f"Current: {current_player}", True, (0, 0, 0))
        self.screen.blit(player_text, (self.margin + self.board_pixels + 35, self.margin + 30))
        
        # Draw black score with rounded rectangle background
        black_rect = pygame.Rect(self.margin + self.board_pixels + 25, self.margin + 65, 160, 30)
        pygame.draw.rect(self.screen, black_score_bg, black_rect, border_radius=15)
        black_text = self.font.render(f"Black: {scores['black']:.1f}", True, (0, 0, 0))
        self.screen.blit(black_text, (self.margin + self.board_pixels + 35, self.margin + 70))
        
        # Draw white score with rounded rectangle background
        white_rect = pygame.Rect(self.margin + self.board_pixels + 25, self.margin + 105, 160, 30)
        pygame.draw.rect(self.screen, white_score_bg, white_rect, border_radius=15)
        white_text = self.font.render(f"White: {scores['white']:.1f}", True, (0, 0, 0))
        self.screen.blit(white_text, (self.margin + self.board_pixels + 35, self.margin + 110))
        
        # Draw buttons with enhanced styling
        # Pass button
        pygame.draw.rect(self.screen, (220, 220, 220), self.pass_button)
        pygame.draw.rect(self.screen, (100, 100, 100), self.pass_button, 2)
        pass_text_rect = self.pass_text.get_rect(center=self.pass_button.center)
        self.screen.blit(self.pass_text, pass_text_rect)
        
        # Restart button
        pygame.draw.rect(self.screen, (220, 220, 220), self.restart_button)
        pygame.draw.rect(self.screen, (100, 100, 100), self.restart_button, 2)
        restart_text_rect = self.restart_text.get_rect(center=self.restart_button.center)
        self.screen.blit(self.restart_text, restart_text_rect)
        
        # Show pass count if any
        if board.passes > 0:
            pass_rect = pygame.Rect(self.margin + self.board_pixels + 30, self.margin + 130, 100, 30)
            pygame.draw.rect(self.screen, (255, 220, 220), pass_rect)
            pygame.draw.rect(self.screen, (200, 0, 0), pass_rect, 2)
            pass_count = self.font.render(f"Passes: {board.passes}", True, (200, 0, 0))
            text_rect = pass_count.get_rect(center=pass_rect.center)
            self.screen.blit(pass_count, text_rect)
        
        pygame.display.update()

    def draw_buttons(self, board):
        """Draw the pass and restart buttons."""
        # Colors for buttons
        button_bg = (255, 165, 0)  # Orange
        button_hover_bg = (255, 140, 0)  # Darker orange for hover
        
        # Pass button
        self.pass_button = pygame.Rect(self.margin + self.board_pixels + 25, self.margin + 150, 160, 35)
        button_color = button_hover_bg if self.pass_button.collidepoint(pygame.mouse.get_pos()) else button_bg
        pygame.draw.rect(self.screen, button_color, self.pass_button, border_radius=17)
        
        # Pass button text
        pass_font = pygame.font.SysFont('Arial', 20, bold=True)
        self.pass_text = pass_font.render("Pass Turn", True, (0, 0, 0))
        pass_text_rect = self.pass_text.get_rect(center=self.pass_button.center)
        self.screen.blit(self.pass_text, pass_text_rect)
        
        # Restart button
        self.restart_button = pygame.Rect(self.margin + self.board_pixels + 25, self.margin + 195, 160, 35)
        button_color = button_hover_bg if self.restart_button.collidepoint(pygame.mouse.get_pos()) else button_bg
        pygame.draw.rect(self.screen, button_color, self.restart_button, border_radius=17)
        
        # Restart button text
        restart_font = pygame.font.SysFont('Arial', 20, bold=True)
        self.restart_text = restart_font.render("Restart Game", True, (0, 0, 0))
        restart_text_rect = self.restart_text.get_rect(center=self.restart_button.center)
        self.screen.blit(self.restart_text, restart_text_rect)
        
        pygame.display.update()

    def show_game_over(self, black_score, white_score, board):
        """Display game over screen with final scores and details"""
        # Store current window dimensions
        screen_width = max(820, self.margin * 2 + self.board_pixels + 200)
        screen_height = self.margin * 2 + self.board_pixels + 100
        
        # Create a new surface for the game over screen
        game_over_surface = pygame.Surface((screen_width, screen_height))
        
        # Load and scale background image for game over screen
        try:
            bg_image = pygame.image.load(BACKGROUND).convert()
            bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))
            game_over_surface.blit(bg_image, (0, 0))
        except pygame.error:
            game_over_surface.fill(BACKGROUND_COLOR)
        
        # Create semi-transparent overlay for better text visibility
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        game_over_surface.blit(overlay, (0, 0))
        
        # Fonts for different text elements
        game_over_font = pygame.font.SysFont('Arial', 48, bold=True)
        score_font = pygame.font.SysFont('Arial', 36, bold=True)
        detail_font = pygame.font.SysFont('Arial', 24)
        instruction_font = pygame.font.SysFont('Arial', 20)

        # Colors for different sections
        title_color = (255, 215, 0)  # Gold
        black_score_bg = (144, 238, 144)  # Light green
        white_score_bg = (255, 182, 193)  # Light pink
        text_color = (255, 255, 255)  # White text
        
        # Game Over text
        game_over_text = game_over_font.render("Game Over!", True, title_color)
        text_rect = game_over_text.get_rect(center=(screen_width//2, screen_height//4))
        game_over_surface.blit(game_over_text, text_rect)
        
        # Black score details
        black_captures = board.captured_stones['black']
        black_score_text = score_font.render(f"Black Total: {black_score:.1f}", True, text_color)
        black_detail = detail_font.render(f"(Territory + {black_captures} captures)", True, text_color)
        
        # Position black score text
        black_score_rect = black_score_text.get_rect(center=(screen_width//2, screen_height//2 - 60))
        black_detail_rect = black_detail.get_rect(center=(screen_width//2, screen_height//2 - 20))
        game_over_surface.blit(black_score_text, black_score_rect)
        game_over_surface.blit(black_detail, black_detail_rect)
        
        # White score details
        white_captures = board.captured_stones['white']
        white_score_text = score_font.render(f"White Total: {white_score:.1f}", True, text_color)
        white_detail = detail_font.render(f"(Territory + {white_captures} captures + {board.komi} komi)", True, text_color)
        
        # Position white score text
        white_score_rect = white_score_text.get_rect(center=(screen_width//2, screen_height//2 + 40))
        white_detail_rect = white_detail.get_rect(center=(screen_width//2, screen_height//2 + 80))
        game_over_surface.blit(white_score_text, white_score_rect)
        game_over_surface.blit(white_detail, white_detail_rect)
        
        # Add winner announcement
        winner = "Black" if black_score > white_score else "White"
        winner_color = black_score_bg if winner == "Black" else white_score_bg
        winner_text = score_font.render(f"{winner} Wins!", True, winner_color)
        winner_rect = winner_text.get_rect(center=(screen_width//2, screen_height//2 + 140))
        game_over_surface.blit(winner_text, winner_rect)
        
        # Add instruction text
        instruction_text = instruction_font.render("Click anywhere to return to game", True, text_color)
        instruction_rect = instruction_text.get_rect(center=(screen_width//2, screen_height - 50))
        game_over_surface.blit(instruction_text, instruction_rect)
        
        # Display the game over screen
        self.screen.blit(game_over_surface, (0, 0))
        pygame.display.update()
        
        # Wait for click to exit
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
        
        # Redraw the game board and all its elements
        self.initialize()
        self.draw_board()
        return True

    def draw_board(self):
        """Draw the empty board."""
        # Draw the background
        self.screen.blit(self.background, (0, 0))

        # Draw the home button
        self.screen.blit(self.home_icon, self.home_button)

        # Draw the board outline
        pygame.draw.rect(self.screen, BLACK, self.outline, 2)
        
        # Draw the grid lines
        for i in range(self.board_size):
            # Vertical lines
            start_pos = (self.margin + (self.cell_size * i), self.margin)
            end_pos = (self.margin + (self.cell_size * i), self.margin + self.board_pixels)
            pygame.draw.line(self.screen, BLACK, start_pos, end_pos, 1)
            
            # Horizontal lines
            start_pos = (self.margin, self.margin + (self.cell_size * i))
            end_pos = (self.margin + self.board_pixels, self.margin + (self.cell_size * i))
            pygame.draw.line(self.screen, BLACK, start_pos, end_pos, 1)
        
        # Draw star points (for 19x19 board)
        if self.board_size == 19:
            star_points = [(3, 3), (9, 3), (15, 3),
                         (3, 9), (9, 9), (15, 9),
                         (3, 15), (9, 15), (15, 15)]
            for point in star_points:
                x = self.margin + point[0] * self.cell_size
                y = self.margin + point[1] * self.cell_size
                pygame.draw.circle(self.screen, BLACK, (x, y), 3)
        
        pygame.display.update()

    def clear_board(self):
        """Clear the board for restart."""
        self.draw_board()
        pygame.display.flip()

    def _draw_grid_lines(self):
        """Draw the grid lines on the board."""
        for i in range(self.board_size):
            # Vertical lines
            start_pos = (self.margin + (self.cell_size * i), self.margin)
            end_pos = (self.margin + (self.cell_size * i), self.margin + self.board_pixels)
            pygame.draw.line(self.screen, BLACK, start_pos, end_pos, 1)
            
            # Horizontal lines
            start_pos = (self.margin, self.margin + (self.cell_size * i))
            end_pos = (self.margin + self.board_pixels, self.margin + (self.cell_size * i))
            pygame.draw.line(self.screen, BLACK, start_pos, end_pos, 1)
            end_pos = (self.margin + (self.cell_size * i), self.margin + self.board_pixels)
            pygame.draw.line(self.screen, BLACK, start_pos, end_pos, 1)
            
            # Horizontal lines
            start_pos = (self.margin, self.margin + (self.cell_size * i))
            end_pos = (self.margin + self.board_pixels, self.margin + (self.cell_size * i))
            pygame.draw.line(self.screen, BLACK, start_pos, end_pos, 1)

    def handle_click(self, pos):
        """Handle mouse click event."""
        # Check if home button was clicked
        if self.home_button.collidepoint(pos):
            return 'home'
            
        # Check if pass button was clicked
        if self.pass_button.collidepoint(pos):
            return 'pass'
            
        # Check if restart button was clicked
        if self.restart_button.collidepoint(pos):
            return 'restart'
