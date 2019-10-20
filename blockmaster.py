import math

import pygame
import random

"""
10 x 20 square grid
shapes: S, Z, I, O, J, L, T
represented in order by 0 - 6
"""

# TODO: Fix fall speed
# TODO: Block can rotate into other blocks
# TODO: Occasional glitch when clearing rows
# TODO: Implement grade system
# TODO: Fix the scoring system

pygame.font.init()

# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 20 height per block
block_size = 300 // 10
grid_size = (10, 20)  # 10 x 20 grid

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height


# SHAPE FORMATS

S = [['.....',
      '......',
      '..00..',
      '.00...',
      '.....'],
     ['.....',
      '.0...',
      '.00..',
      '..0..',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '...0.',
      '..00.',
      '..0..',
      '.....']]

I = [['.....',
      '0000.',
      '.....',
      '.....',
      '.....'],
     ['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(141, 0, 141), (0, 148, 0), (203, 20, 10), (200, 200, 0), (0, 32, 190), (200, 85, 0), (0, 130, 175)]
# index 0 - 6 represent shape

bag = [1, 1, 1, 1]  # Start bag with 4 Z pieces, emulating TGM1


class Block(object):
    def __init__(self, x, y, shape, grid):
        self.x = x
        self.y = y
        self.shape = shape
        self.grid = grid
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0

    def move(self, direction):
        if direction is "left":
            self.x -= 1
            if not self._valid_space():
                self.x += 1
                return False
        elif direction is "right":
            self.x += 1
            if not self._valid_space():
                self.x -= 1
                return False
        elif direction is "down":
            self.y += 1
            if not self._valid_space():
                self.y -= 1
                return False

        return True

    def rotate(self, direction):
        new_rotation = self.rotation
        if direction is "left":
            new_rotation += 1
        else:
            new_rotation -= 1

        if self.y < 0:
            if self._valid_space(new_rotation):
                self.rotation = new_rotation
            else:  # Try wallkicking
                self.x += 1  # Right
                if self._valid_space(new_rotation):
                    self.rotation = new_rotation
                else:
                    self.x -= 2  # Left
                    if self._valid_space(new_rotation):
                        self.rotation = new_rotation
                    else:
                        self.x += 2
        else:
            self.rotation = new_rotation

    def _valid_space(self, rotation=None):
        """Ensures that we don't move outside the grid, and that the grid position is not occupied"""
        if rotation is None:
            rotation = self.rotation

        # Create list of grid positions that are not occupied
        accepted_pos = [[(j, i) for j in range(len(self.grid[1])) if self.grid[i][j] == (0, 0, 0)] for i in range(len(self.grid))]
        accepted_pos = [j for sub in accepted_pos for j in sub]  # Flatten to 1 dimension

        formatted = self._convert_shape_format(rotation)

        for pos in formatted:
            if pos not in accepted_pos:
                if pos[1] > -1:
                    return False
                if pos[0] > -1 and pos[0] < 10:
                    return False

        return True

    def _convert_shape_format(self, rotation=None):
        if rotation is None:
            rotation = self.rotation

        positions = []
        print(rotation % len(self.shape))
        format = self.shape[rotation % len(self.shape)]  # Get sub-list of shape

        # Find shape position in list
        for i, line in enumerate(format):
            row = list(line)
            for j, col in enumerate(row):
                if col == "0":
                    positions.append((self.x + j, self.y + i))

        # Offset shape to top left
        for i, pos in enumerate(positions):
            positions[i] = (pos[0] - 2, pos[1] - 4)

        return positions


class Input(object):
    def __init__(self):
        pass

    def move(self, direction):
        pass


class Playfield(object):
    def __init__(self, x, y, width, height, surface):
        self.top_left_x = x
        self.top_left_y = y
        self.pfield_width = width
        self.pfield_height = height
        self.block_size = self.pfield_width // 10
        self.locked_positions={}
        self.grid = self._create_grid()
        self.gravity = 4 / 256
        self.ARE_delay = 41 * 16  # 41 frames @ 60hz
        self.lock_delay = 30 * 16 # 30 frames @ 60hz
        self.surface = surface

    def _create_grid(self):
        grid = [[(0,0,0) for x in range(grid_size[0])] for x in range(grid_size[1])]

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if (j, i) in self.locked_positions:
                    c = self.locked_positions[(j, i)]
                    grid[i][j] = c

        return grid

    def _check_lost(self):
        for pos in self.locked_positions:
            x, y = pos
            if y < 1:  # Above grid
                return True

        return False

    def _clear_rows(self):
        inc = 0  # How many rows to shift down
        for i in range(len(self.grid) - 1, -1, -1):  # Start check grid from below
            row = self.grid[i]
            if (0, 0, 0) not in row:
                inc += 1
                ind = i  # Index of row that is removed
                for j in range(len(row)):
                    del self.locked_positions[(j, i)]  # Remove the block from locked positions

        # Shift down above rows
        if inc > 0:
            for key in sorted(list(self.locked_positions), key=lambda x: x[1])[::-1]:  # Check locked from below to prevent overwriting keys
                x, y = key
                if y < ind:
                    new_key = (x, y + inc)  # Create new keys for rows above the one we deleted
                    self.locked_positions[new_key] = self.locked_positions.pop(key)  # Insert old blocks into new locked position and remove old positions

        # Lock and ARE delay
        pygame.time.delay(self.lock_delay) if inc == 0 else pygame.time.delay(self.ARE_delay)

        return inc

    def _draw_next_shape(self, block):
        font = pygame.font.SysFont("comicsans", 30)
        label = font.render("Next", 1, (255,255,255))

        sx = self.top_left_x + self.pfield_width + 50
        sy = self.top_left_y + self.pfield_height / 2 - 100
        format = block.shape[block.rotation % len(block.shape)]

        for i, line in enumerate(format):
            row = list(line)
            for j, col in enumerate(row):
                if col == "0":
                    pygame.draw.rect(self.surface, block.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)
                    pygame.draw.rect(self.surface, (200,200,200), (sx + j * block_size, sy + i * block_size, block_size, block_size), 1)

        self.surface.blit(label, (sx + 10, sy - 30))

    def _draw_window(self, score=0, last_score=0):
        self.surface.fill((0, 0, 0))
        pygame.font.init()
        font = pygame.font.SysFont('comicsans', 60)
        label = font.render("Blockmaster", 1, (255, 255, 255))
        self.surface.blit(label, (top_left_x + play_width / 2 - label.get_width() / 2, 30))

        # Current score
        font = pygame.font.SysFont("comicsans", 30)
        label = font.render("Score: " + str(score), 1, (255, 255, 255))
        sx = top_left_x + play_width + 50
        sy = top_left_y + play_height / 2 - 100
        self.surface.blit(label, (sx + 10, sy + 160))

        # High score
        label = font.render("High Score:", 1, (255, 255, 255))
        highscore = font.render(str(last_score), 1, (255, 255, 255))
        sx = top_left_x - 200
        sy = top_left_y + 300
        self.surface.blit(label, (sx + 10, sy + 160))
        self.surface.blit(highscore, (sx + 10, sy + 195))

        sx = self.top_left_x
        sy = self.top_left_y
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                pygame.draw.rect(self.surface, self.grid[i][j],
                                 (sx + j * self.block_size, sy + i * self.block_size, self.block_size, self.block_size), 0)
                if not self.grid[i][j] == (0, 0, 0):  # Draw white lines on blocks
                    pygame.draw.rect(self.surface, (200, 200, 200),
                                     (sx + j * self.block_size, sy + i * self.block_size, self.block_size, self.block_size), 1)

        # Playfield border
        pygame.draw.rect(self.surface, (255, 0, 0), (sx, sy, self.pfield_width, self.pfield_height), 5)

    def _draw_text_middle(self, text, size, color):
        font = pygame.font.SysFont("comicsans", size, bold=True)
        label = font.render(text, 1, color)

        sx = self.top_left_x
        sy = self.top_left_y

        self.surface.blit(label, (sx + self.pfield_width / 2 - (label.get_width() / 2),
                                  sy + self.pfield_height / 2 - (label.get_height() * 2)))

    def update(self, block: Block, next_block: Block, change_block: bool,
               score=0, high_score=0):
        self.grid = self._create_grid()

        # Add color of piece to the grid for drawing
        shape_pos = convert_shape_format(block)
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:  # If not above the grid
                self.grid[y][x] = block.color

        if change_block:
            # Add current block to locked positions in grid
            for pos in shape_pos:
                p = (pos[0], pos[1])
                self.locked_positions[p] = block.color
                change_block = False

        self._draw_window(score, high_score)
        self._draw_next_shape(next_block)
        pygame.display.update()

        if self._check_lost():
            self._draw_text_middle("YOU LOST!", 80, (255,255,255))
            pygame.display.update()
            pygame.time.delay(2000)

def create_grid(locked_positions={}):
    grid = [[(0,0,0) for x in range(grid_size[0])] for x in range(grid_size[1])]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c

    return grid


def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]  # Get sub-list of shape

    # Find shape position in list
    for i, line in enumerate(format):
        row = list(line)
        for j, col in enumerate(row):
            if col == "0":
                positions.append((shape.x + j, shape.y + i))

    # Offset shape to top left
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    """Ensures that we don't move outside the grid, and that the grid position is not occupied"""

    # Create list of grid positions that are not occupied
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]  # Flatten to 1 dimension

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False

    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:  # Above grid
            return True

    return False


def get_shape(grid, first=False):
    """Piece randomizer that behaves like in TGM1. It tries to generate a unique piece 4 times before giving up.
       Additionally, it never deals a S, Z, or O as the first piece."""

    if first:
        new = Block(5, 0, random.choice([I, J, L, T]), grid)
    else:
        for i in range(4):
            new = Block(5, 0, random.choice(shapes), grid)
            if new.shape in bag:
                continue
            else:
                break

    # Update bag
    bag.insert(0, new.shape)
    bag.pop()

    return new


def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width()/2), top_left_y + play_height/2 - label.get_height()*2))


def clear_rows(grid, locked):
    inc = 0  # How many rows to shift down
    for i in range(len(grid)-1, -1, -1):  # Start check grid from below
        row = grid[i]
        if (0,0,0) not in row:
            inc += 1
            ind = i  # Index of row that is removed
            for j in range(len(row)):
                del locked[(j,i)]  # Remove the block from locked positions

    # Shift down above rows
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:  # Check locked from below to prevent overwriting keys
            x, y = key
            if y < ind:
                new_key = (x, y + inc)  # Create new keys for rows above the one we deleted
                locked[new_key] = locked.pop(key)  # Insert old blocks into new locked position and remove old positions

    # Lock and ARE delay
    if inc == 0:
        pygame.time.delay(30*16)
    else:
        pygame.time.delay(41*16)

    return inc


def draw_next_shape(shape, surface):
    font = pygame.font.SysFont("comicsans", 30)
    label = font.render("Next", 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, col in enumerate(row):
            if col == "0":
                pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)
                pygame.draw.rect(surface, (200,200,200), (sx + j * block_size, sy + i * block_size, block_size, block_size), 1)

    surface.blit(label, (sx + 10, sy - 30))


def update_score(nscore):
    score = max_score()

    with open("data/score.txt", "w") as f:
        if score > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))


def max_score():
    with open("data/score.txt", "r") as f:
        lines = f.readlines()
        score = lines[0].strip()

    return int(score)


def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        # Horizontal lines
        pygame.draw.line(surface, (128,128,128), (sx, sy + i*block_size), (sx+play_width, sy + i*block_size))
        for j in range(len(grid[i])):
            # Vertical lines
            pygame.draw.line(surface, (128,128,128), (sx + j*block_size, sy), (sx + j*block_size, sy + play_height))


def draw_window(surface, grid, locked, score=0, last_score=0):
    surface.fill((0,0,0))
    pygame.font.init()
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render("Blockmaster", 1, (255,255,255))
    surface.blit(label, (top_left_x + play_width/2 - label.get_width()/2, 30))

    # Current score
    font = pygame.font.SysFont("comicsans", 30)
    label = font.render("Score: " + str(score), 1, (255,255,255))
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    surface.blit(label, (sx + 10, sy + 160))

    # High score
    label = font.render("High Score:", 1, (255,255,255))
    highscore = font.render(str(last_score), 1, (255,255,255))
    sx = top_left_x - 200
    sy = top_left_y + 300
    surface.blit(label, (sx + 10, sy + 160))
    surface.blit(highscore, (sx + 10, sy + 195))

    sx = top_left_x
    sy = top_left_y
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)
            if not grid[i][j] == (0,0,0):
                pygame.draw.rect(surface, (200,200,200), (sx + j*block_size, sy + i*block_size, block_size, block_size), 1)

    pygame.draw.rect(surface, (255,0,0), (top_left_x, top_left_y, play_width, play_height), 5)


def new_score(lines, level=1):
    combo = 1
    bravo = 1

    return math.ceil((level + lines) / 4) * lines * bravo

def main(win):
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape(grid, first=True)
    next_piece = get_shape(grid)
    has_rotated = False
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    gravity = 256
    level_time = 0
    lock_time = 0
    lock = False
    high_score = max_score()
    score = 0

    while run:
        grid = create_grid(locked_positions)

        # Fall on delta time
        dt = clock.tick(60)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        if fall_time / 1000 > fall_speed:
            fall_time = 0
            # Check if piece should lock and change to next piece
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                lock = True

        if lock:
            lock_time += clock.get_rawtime()
            if lock_time * 60 > 30*16 * dt:
                change_piece = True

        for event in pygame.event.get():
            # Quitting
            if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                run = False
                pygame.display.quit()
            # Handle rotation
            if event.type == pygame.KEYDOWN and not has_rotated:
                if event.key == pygame.K_a:
                    current_piece.rotate("left")
                    has_rotated = True
                if event.key == pygame.K_s:
                    current_piece.rotate("right")
                    has_rotated = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a or event.key == pygame.K_s:
                    has_rotated = False
                if event.key == pygame.K_DOWN:
                    change_piece = False
            # Handle movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                #current_piece.move("left")
                current_piece.x -= 1
                if not valid_space(current_piece, grid):
                    current_piece.x += 1
            if keys[pygame.K_RIGHT]:
                #current_piece.move("right")
                current_piece.x += 1
                if not valid_space(current_piece, grid):
                    current_piece.x -= 1
            if keys[pygame.K_DOWN]:
                #current_piece.move("down")
                current_piece.y += 1
                if not valid_space(current_piece, grid):
                    current_piece.y -= 1
                    change_piece = True

        shape_pos = convert_shape_format(current_piece)

        # Add color of piece to the grid for drawing
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:  # If not above the grid
                grid[y][x] = current_piece.color


        #if level_time / 1000 > 5:
        #    level_time = 0
        #    if fall_speed > 0.12:
        #        fall_speed -= 0.005

        # If piece hit ground
        if change_piece:
            # Add current piece to locked positions in grid
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color

            current_piece = next_piece
            next_piece = get_shape(grid)
            change_piece = False
            lock = False
            lock_time = 0

            # Scoring
            lines = clear_rows(grid, locked_positions)
            if lines > 0:
                print(lines)
                score += new_score(lines)

        draw_window(win, grid, score, high_score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle("YOU LOST!", 80, (255,255,255), win)
            pygame.display.update()
            pygame.time.delay(1500)
            update_score(score)
            run = False

        if pygame.event.get(pygame.QUIT):
            run = False
            pygame.display.quit()
            pygame.quit()


def main_menu(win):
    run = True
    while run:
        win.fill((0,0,0))
        draw_text_middle("Press Any Key To Play", 60, (255,255,255), win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.type == pygame.K_ESCAPE:
                    run = False
                main(win)

    pygame.quit()

if __name__ == "__main__":
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption("Blockmaster")
    pygame.key.set_repeat(256, 17)
    print(pygame.key.get_repeat())
    main_menu(win)  # start game
