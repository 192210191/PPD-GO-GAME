from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line
from kivy.metrics import dp
from functools import partial
import copy

class GoBoard(Widget):
    def __init__(self, size=19, **kwargs):
        super().__init__(**kwargs)
        self.board_size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.current_player = 'B'  # Black starts
        self.last_move = None
        self.bind(size=self._update_board_size)
        
    def _update_board_size(self, instance, value):
        self.draw_board()
        
    def draw_board(self):
        self.canvas.clear()
        with self.canvas:
            # Draw board background
            Color(0.87, 0.72, 0.53)  # Wooden color
            self.canvas.add(Rectangle(pos=self.pos, size=self.size))
            
            # Draw grid lines
            Color(0, 0, 0)
            cell_size = min(self.width, self.height) / (self.board_size + 1)
            for i in range(self.board_size):
                # Vertical lines
                x = self.pos[0] + cell_size * (i + 1)
                Line(points=[x, self.pos[1] + cell_size, 
                           x, self.pos[1] + cell_size * self.board_size])
                
                # Horizontal lines
                y = self.pos[1] + cell_size * (i + 1)
                Line(points=[self.pos[0] + cell_size, y,
                           self.pos[0] + cell_size * self.board_size, y])
            
            # Draw stones
            for i in range(self.board_size):
                for j in range(self.board_size):
                    if self.board[i][j]:
                        x = self.pos[0] + cell_size * (i + 1)
                        y = self.pos[1] + cell_size * (j + 1)
                        Color(0, 0, 0) if self.board[i][j] == 'B' else Color(1, 1, 1)
                        Ellipse(pos=(x - cell_size/2, y - cell_size/2),
                               size=(cell_size, cell_size))

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        
        cell_size = min(self.width, self.height) / (self.board_size + 1)
        x = int((touch.pos[0] - self.pos[0]) / cell_size - 0.5)
        y = int((touch.pos[1] - self.pos[1]) / cell_size - 0.5)
        
        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            if self.is_valid_move(x, y):
                self.make_move(x, y)
                self.draw_board()

    def is_valid_move(self, x, y):
        if self.board[x][y] is not None:
            return False
            
        # Make temporary move
        self.board[x][y] = self.current_player
        
        # Check if move creates a liberty
        has_liberty = self._check_liberties(x, y)
        
        # Undo temporary move
        self.board[x][y] = None
        
        return has_liberty

    def _check_liberties(self, x, y):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.board_size and 
                0 <= ny < self.board_size and 
                self.board[nx][ny] is None):
                return True
        return False

    def make_move(self, x, y):
        self.board[x][y] = self.current_player
        self.last_move = (x, y)
        self.current_player = 'W' if self.current_player == 'B' else 'B'

class GoApp(App):
    def build(self):
        # Main layout
        layout = BoxLayout(orientation='vertical')
        
        # Top bar with current player and pass button
        top_bar = BoxLayout(size_hint_y=0.1)
        self.player_label = Label(text='Current Player: Black')
        pass_button = Button(text='Pass', size_hint_x=0.3)
        pass_button.bind(on_press=self.pass_move)
        top_bar.add_widget(self.player_label)
        top_bar.add_widget(pass_button)
        
        # Go board
        self.board = GoBoard()
        
        # Add widgets to main layout
        layout.add_widget(top_bar)
        layout.add_widget(self.board)
        
        return layout
    
    def pass_move(self, instance):
        self.board.current_player = 'W' if self.board.current_player == 'B' else 'B'
        self.player_label.text = f'Current Player: {"Black" if self.board.current_player == "B" else "White"}'

if __name__ == '__main__':
    GoApp().run()
