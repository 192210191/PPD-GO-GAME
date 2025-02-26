#!/usr/bin/env python
from copy import deepcopy
from game.util import PointDict
"""
This file is the full backend environment of the game.
"""

BOARD_SIZE = 20  # number of rows/cols = BOARD_SIZE - 1


def opponent_color(color):
    if color == 'WHITE':
        return 'BLACK'
    elif color == 'BLACK':
        return 'WHITE'
    else:
        print('Invalid color: ' + color)
        return KeyError

def neighbors(point, board_size):
    """Return a list of neighboring points."""
    neighboring = [(point[0] - 1, point[1]),
                   (point[0] + 1, point[1]),
                   (point[0], point[1] - 1),
                   (point[0], point[1] + 1)]
    return [point for point in neighboring if 0 < point[0] < board_size and 0 < point[1] < board_size]


def cal_liberty(points, board):
    """Find and return the liberties of the point."""
    liberties = [point for point in neighbors(points, board.size)
                 if not board.stonedict.get_groups('BLACK', point) and not board.stonedict.get_groups('WHITE', point)]
    return set(liberties)


class Group(object):
    def __init__(self, point, color, liberties):
        """
        Create and initialize a new group.
        :param point: the initial stone in the group
        :param color:
        :param liberties:
        """
        self.color = color
        if isinstance(point, list):
            self.points = point
        else:
            self.points = [point]
        self.liberties = liberties

    @property
    def num_liberty(self):
        return len(self.liberties)

    def add_stones(self, pointlist):
        """Only update stones, not liberties"""
        self.points.extend(pointlist)
    
    def remove_liberty(self, point):
        self.liberties.remove(point)

    def __str__(self):
        """Summarize color, stones, liberties."""
        return '%s - stones: [%s]; liberties: [%s]' % \
               (self.color,
                ', '.join([str(point) for point in self.points]),
                ', '.join([str(point) for point in self.liberties]))
    
    def __repr__(self):
        return str(self)


class Board(object):
    """
    Implementation of Go game rules including:
    1. Stone capturing (liberty rule)
    2. Ko rule to prevent infinite loops
    3. Suicide rule prevention
    4. Territory scoring
    """
    def __init__(self, board_size=19, next_color='BLACK'):
        """Initialize board with specified size (9x9, 13x13, or 19x19)"""
        if board_size not in [9, 13, 19]:
            raise ValueError("Board size must be 9, 13, or 19")
            
        self.size = board_size
        self.board = [[None for _ in range(self.size + 1)] for _ in range(self.size + 1)]
        self.next = next_color
        self.winner = None
        self.counter_move = 0
        self.last_move = None
        self.ko_point = None
        self.last_board_state = None  # For ko rule checking
        self.passes = 0  # Count consecutive passes for game end
        self.captured_stones = {'BLACK': 0, 'WHITE': 0}  # Count captured stones

        # Set komi to 6.5 for all board sizes
        self.komi = 6.5

    def is_valid_move(self, point):
        """Check if a move is valid according to Go rules."""
        x, y = point
        
        # Check basic validity
        if not (0 <= x < self.size and 0 <= y < self.size):
            return False
        if self.board[x][y] is not None:
            return False
            
        # Check ko rule
        if point == self.ko_point:
            return False
            
        # Try the move
        self.board[x][y] = self.next
        
        # Check if the move captures any opponent stones
        opponent = self._get_opponent_color()
        captured_groups = self._find_captured_groups(opponent)
        
        if captured_groups:
            # Move is valid if it captures opponent stones
            self.board[x][y] = None
            return True
            
        # If no captures, check if the move is suicide
        own_group = self._get_group(x, y)
        if self._count_liberties(own_group) == 0:
            # Move is suicide
            self.board[x][y] = None
            return False
            
        self.board[x][y] = None
        return True

    def put_stone(self, point):
        """Place a stone and handle captures."""
        if not self.is_valid_move(point):
            return False, []  # Return False and empty list of captured points

        x, y = point
        self.passes = 0  # Reset pass counter
        
        # Store current board state for ko rule
        self.last_board_state = [row[:] for row in self.board]
        
        # Place the stone
        self.board[x][y] = self.next
        opponent = self._get_opponent_color()
        
        # Find and remove captured opponent groups
        captured_points = []
        captured_groups = self._find_captured_groups(opponent)
        for group in captured_groups:
            captured_points.extend(group)
            self._remove_group(group)
        
        # If no opponent stones were captured, check if the placed stone's group is captured
        if not captured_points:
            own_group = self._get_group(x, y)
            if self._count_liberties(own_group) == 0:
                # Move is suicide, not allowed
                self.board[x][y] = None
                return False, []
        
        # Update captured stones count
        self.captured_stones[self.next] += len(captured_points)
        
        # Update ko point
        self.ko_point = None
        if len(captured_points) == 1 and len(self._get_group(x, y)) == 1:
            # If exactly one stone was captured and the placed stone is alone,
            # mark the captured point as ko
            self.ko_point = captured_points[0]
        
        self.last_move = point
        self.next = opponent
        self.counter_move += 1
        
        return True, captured_points  # Return success and list of captured points

    def pass_move(self):
        """Pass the current turn."""
        # Reset consecutive passes if the last move wasn't a pass
        if self.last_move is not None:  # There was a stone placed last turn
            self.passes = 0
        self.passes += 1  # Increment consecutive passes
        
        # Store this pass as the last move
        self.last_move = None
        self.ko_point = None
        
        # Switch to next player
        self.next = opponent_color(self.next)
        
        # Return True if both players passed consecutively
        return self.passes >= 2

    def get_score(self):
        """Calculate the score using territory scoring rules."""
        territory = {'BLACK': 0, 'WHITE': 0}
        counted = set()

        # Count territory
        for x in range(self.size):
            for y in range(self.size):
                if (x, y) not in counted and self.board[x][y] is None:
                    territory_points = self._find_territory(x, y)
                    if territory_points:
                        counted.update(territory_points[0])
                        territory[territory_points[1]] += len(territory_points[0])

        # Add captured stones to score
        final_score = {
            'BLACK': territory['BLACK'] + self.captured_stones['BLACK'],
            'WHITE': territory['WHITE'] + self.captured_stones['WHITE'] + self.komi  # Komi
        }

        return final_score

    def _get_opponent_color(self):
        """Get the opponent's color."""
        return 'WHITE' if self.next == 'BLACK' else 'BLACK'

    def _get_neighbors(self, x, y):
        """Get valid neighboring points."""
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                neighbors.append((nx, ny))
        return neighbors

    def _get_group(self, x, y):
        """Get all connected stones of the same color."""
        if self.board[x][y] is None:
            return set()

        color = self.board[x][y]
        group = {(x, y)}
        frontier = [(x, y)]

        while frontier:
            current = frontier.pop()
            for nx, ny in self._get_neighbors(*current):
                if self.board[nx][ny] == color and (nx, ny) not in group:
                    group.add((nx, ny))
                    frontier.append((nx, ny))
        return group

    def _count_liberties(self, group):
        """Count the number of liberties for a group of stones."""
        liberties = set()
        for x, y in group:
            for nx, ny in self._get_neighbors(x, y):
                if self.board[nx][ny] is None:
                    liberties.add((nx, ny))
        return len(liberties)

    def _find_captured_groups(self, color):
        """Find all groups of the given color that have been captured."""
        captured = []
        checked = set()

        for x in range(self.size):
            for y in range(self.size):
                if (x, y) not in checked and self.board[x][y] == color:
                    group = self._get_group(x, y)
                    checked.update(group)
                    if self._count_liberties(group) == 0:
                        captured.append(list(group))
        return captured

    def _remove_group(self, group):
        """Remove a group of stones from the board."""
        for x, y in group:
            self.board[x][y] = None

    def _find_territory(self, x, y):
        """Find territory points and determine owner.
        Returns (territory_points, owner) or None if territory is neutral."""
        if self.board[x][y] is not None:
            return None

        territory = {(x, y)}
        frontier = [(x, y)]
        borders = set()

        while frontier:
            current = frontier.pop()
            for nx, ny in self._get_neighbors(*current):
                if self.board[nx][ny] is None:
                    if (nx, ny) not in territory:
                        territory.add((nx, ny))
                        frontier.append((nx, ny))
                else:
                    borders.add(self.board[nx][ny])

        # Territory must be surrounded by stones of only one color
        if len(borders) == 1:
            return (territory, list(borders)[0])
        return None

    def get_board_state(self):
        """Return the current board state."""
        return [row[:] for row in self.board]

    def __str__(self):
        """String representation of the board."""
        rows = []
        for y in range(self.size):
            row = []
            for x in range(self.size):
                if self.board[x][y] == 'BLACK':
                    row.append('B')
                elif self.board[x][y] == 'WHITE':
                    row.append('W')
                else:
                    row.append('.')
            rows.append(' '.join(row))
        return '\n'.join(rows)
