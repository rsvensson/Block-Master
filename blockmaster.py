import math

import pygame
import random

"""
10 x 20 square grid
shapes: S, Z, I, O, J, L, T
represented in order by 0 - 6
"""

# TODO: Occasional glitch when clearing rows
# TODO: Implement grade system
# TODO: Wall kicks still don't behave quite as they should
# TODO: Lock timer needs to be implemented better
# TODO: Blocks don't fall instantly to the bottom on level 500+

pygame.font.init()

# GLOBALS VARS
S_WIDTH = 800
S_HEIGHT = 700
PLAY_WIDTH = 300  # meaning 300 // 10 = 30 width per block
PLAY_HEIGHT = 600  # meaning 600 // 20 = 20 height per block
BLOCK_SIZE = 300 // 10
GRID_SIZE = (10, 20)  # 10 x 20 grid
TOP_LEFT_X = (S_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = S_HEIGHT - PLAY_HEIGHT
MAX_FPS = 60


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

# Gravity
DENOMINATOR = 256
INTERNAL_GRAVITY = {0: 4,
                    30: 6,
                    35: 8,
                    40: 10,
                    50: 12,
                    60: 16,
                    70: 32,
                    80: 48,
                    90: 64,
                    100: 80,
                    120: 96,
                    140: 112,
                    160: 128,
                    170: 144,
                    200: 4,
                    220: 32,
                    230: 64,
                    233: 96,
                    236: 128,
                    239: 160,
                    243: 192,
                    247: 224,
                    251: 256,
                    300: 512,
                    330: 768,
                    360: 1024,
                    400: 1280,
                    420: 1024,
                    450: 768,
                    500: 5120}


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

        if self.y > 0:
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
                        self.x += 1
        else:
            self.rotation = new_rotation

    def _valid_space(self, rotation=None):
        """Ensures that we don't move outside the grid, and that the grid position is not occupied"""
        if rotation is None:
            rotation = self.rotation

        # Create list of grid positions that are not occupied
        accepted_pos = [[(j, i) for j in range(len(self.grid.grid[1])) if self.grid.grid[i][j] == (0, 0, 0)] for i in range(len(self.grid.grid))]
        accepted_pos = [j for sub in accepted_pos for j in sub]  # Flatten to 1 dimension

        formatted = self.convert_shape_format(rotation)

        for pos in formatted:
            if pos not in accepted_pos:
                if pos[0] < 0 or pos[0] >= len(self.grid.grid[1]):
                    return False
                if pos[1] > -1:
                    return False

        return True

    def convert_shape_format(self, rotation=None):
        if rotation is None:
            rotation = self.rotation

        positions = []
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


class Grid(object):
    def __init__(self):
        self.locked_positions = {}
        self.grid = self.create_grid()

    def create_grid(self):
        grid = [[(0,0,0) for x in range(GRID_SIZE[0])] for x in range(GRID_SIZE[1])]

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if (j, i) in self.locked_positions:
                    c = self.locked_positions[(j, i)]
                    grid[i][j] = c

        return grid

    def clear_rows(self) -> int:
        self.grid = self.create_grid()
        inc = 0  # How many rows to shift down
        for i in range(len(self.grid) - 1, -1, -1):  # Start check grid from below
            row = self.grid[i]
            if (0, 0, 0) not in row:
                inc += 1
                ind = i  # Index of row that is removed
                for j in range(len(row)):
                    del self.locked_positions[(j, i)]  # Remove the block from locked positions

        # Shift down rows above inc
        if inc > 0:
            for key in sorted(list(self.locked_positions), key=lambda x: x[1])[::-1]:  # Check positions from below to prevent overwriting keys
                x, y = key
                if y < ind:
                    new_key = (x, y + inc)  # Create new keys for rows above the one we deleted
                    self.locked_positions[new_key] = self.locked_positions.pop(key)  # Insert old blocks into new locked position and remove old positions

        return inc

    def check_lost(self):
        for pos in self.locked_positions:
            x, y = pos
            if y < 0:  # Above grid
                print("Hep!")
                return True

        return False

    def update(self, block: Block):
        # Add color of block to the grid for drawing
        shape_pos = block.convert_shape_format(block.rotation)
        for i in range(len(shape_pos)):
           x, y = shape_pos[i]
           if y > -1:  # If not above the grid
               self.grid[y][x] = block.color

class Playfield(object):
    def __init__(self, surface, x, y, width, height, grid: Grid):
        self.top_left_x = x
        self.top_left_y = y
        self.pfield_width = width
        self.pfield_height = height
        self.block_size = self.pfield_width // 10
        self.surface = surface
        self.grid = grid

    def _draw_next_shape(self, block):
        font = pygame.font.SysFont("comicsans", 30)
        label = font.render("Next", 1, (255,255,255))

        sx = self.top_left_x + self.pfield_width + 50
        sy = self.top_left_y
        format = block.shape[block.rotation % len(block.shape)]

        for i, line in enumerate(format):
            row = list(line)
            for j, col in enumerate(row):
                if col == "0":
                    pygame.draw.rect(self.surface, block.color, (sx + j * BLOCK_SIZE, sy + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
                    pygame.draw.rect(self.surface, (200,200,200), (sx + j * BLOCK_SIZE, sy + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

        self.surface.blit(label, (sx + 10, sy))

    def _draw_window(self, score=0, last_score=0, level=0):
        self.surface.fill((0, 0, 0))
        pygame.font.init()
        font = pygame.font.SysFont('comicsans', 60)
        label = font.render("Block Master", 1, (255, 255, 255))
        self.surface.blit(label, (self.top_left_x + self.pfield_width / 2 - label.get_width() / 2, 30))

        # Current score
        font = pygame.font.SysFont("comicsans", 30)
        label = font.render("Score: " + str(score), 1, (255, 255, 255))
        sx = self.top_left_x + self.pfield_width + 50
        sy = self.top_left_y + self.pfield_height / 2 + 100
        self.surface.blit(label, (sx, sy))

        # High score
        label = font.render("High Score:", 1, (255, 255, 255))
        highscore = font.render(str(last_score), 1, (255, 255, 255))
        sx = self.top_left_x + self.pfield_width + 50
        sy = self.top_left_y + self.pfield_height / 2
        self.surface.blit(label, (sx, sy))
        self.surface.blit(highscore, (sx, sy + 20))

        # Level
        label = font.render("Level: " + str(level), 1, (255, 255, 255))
        sx = self.top_left_x + self.pfield_width + 50
        sy = self.top_left_y + self.pfield_height / 2 - 100
        self.surface.blit(label, (sx, sy))

        # Blocks
        sx = self.top_left_x
        sy = self.top_left_y
        for i in range(len(self.grid.grid)):
            for j in range(len(self.grid.grid[i])):
                pygame.draw.rect(self.surface, self.grid.grid[i][j],
                                 (sx + j * self.block_size, sy + i * self.block_size, self.block_size, self.block_size), 0)
                if not self.grid.grid[i][j] == (0, 0, 0):  # Draw white lines on blocks
                    pygame.draw.rect(self.surface, (200, 200, 200),
                                     (sx + j * self.block_size, sy + i * self.block_size, self.block_size, self.block_size), 1)

        # Playfield border
        pygame.draw.rect(self.surface, (255, 0, 0), (sx, sy, self.pfield_width, self.pfield_height), 5)

    def draw_text_middle(self, text, size, color):
        font = pygame.font.SysFont("comicsans", size, bold=True)
        label = font.render(text, 1, color)

        sx = self.top_left_x
        sy = self.top_left_y

        self.surface.blit(label, (sx + self.pfield_width / 2 - (label.get_width() / 2),
                                  sy + self.pfield_height / 2 - (label.get_height() * 2)))
        pygame.display.update()

    def update(self, block: Block, next_block: Block,
               score=0, high_score=0, level=0):
        self._draw_window(score, high_score, level)
        self._draw_next_shape(next_block)
        pygame.display.update()


def get_block(grid, first=False) -> Block:
    """Piece randomizer that behaves like in TGM1. It tries to generate a unique piece 4 times before giving up.
       Additionally, it never deals a S, Z, or O as the first piece."""

    x = len(grid.grid[1]) // 2
    y = 0

    if first:
        c = random.choice([I, J, L, T])
#        if c == 0
        new = Block(x, y, random.choice([I, J, L, T]), grid)
    else:
        for i in range(4):
            new = Block(x, y, random.choice(shapes), grid)
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

    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (label.get_width() / 2), TOP_LEFT_Y + PLAY_HEIGHT / 2 - label.get_height() * 2))


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


def new_score(lines, level=1, combo=1, soft=1, bravo=1):
    return math.ceil(((level + lines) / 4) + soft) * lines * combo * bravo


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


def main(win):
    grid = Grid()
    playfield = Playfield(win, TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT, grid)

    change_block = False
    run = True
    current_block = get_block(playfield.grid, first=True)
    next_block = get_block(playfield.grid)
    has_rotated = False
    clock = pygame.time.Clock()
    ARE_delay = 41 * 16  # ~41 frames @ 60hz
    lock_delay = 30 * 16  # ~30 frames @ 60hz
    lock_time = 0
    lock = False
    fall_time = 0

    # Scoring variables
    high_score = max_score()
    score = 0
    level = 0
    soft = 1
    combo = 1

    # Fall speed
    gravity = DENOMINATOR / INTERNAL_GRAVITY[0]

    while run:
        grid.grid = grid.create_grid()

        # Fall on delta time
        dt = clock.tick(MAX_FPS)
        fall_time += clock.get_rawtime()
        # print(gravity, dt, fall_time)
        if fall_time / dt > gravity:
            fall_time = 0
            if not current_block.move("down"):
                lock = True
            else:
                lock = False
                lock_time = 0

        if lock:
            lock_time += dt
            #print(lock_time, 30*16)
            if lock_time > 30*16:
                change_block = True

        for event in pygame.event.get():
            # Quitting
            if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                run = False
            else:
                if event.type == pygame.MOUSEMOTION:
                    continue
                # Handle rotation
                if event.type == pygame.KEYDOWN and not has_rotated:
                    if event.key == pygame.K_z:
                        current_block.rotate("left")
                        has_rotated = True
                    if event.key == pygame.K_x:
                        current_block.rotate("right")
                        has_rotated = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_z or event.key == pygame.K_x:
                        has_rotated = False
                    if event.key == pygame.K_DOWN:
                        change_block = False
                # Handle movement
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    current_block.move("left")
                if keys[pygame.K_RIGHT]:
                    current_block.move("right")
                if keys[pygame.K_DOWN]:
                    if not current_block.move("down"):
                        change_block = True
                        soft += dt

        grid.update(current_block)
        playfield.update(current_block, next_block, score, high_score, level)

        # Block hit ground
        if change_block:
            # Double check if we should really change block. Not sure if needed.
            if current_block.move("down"):
                lock_time = 0
                lock = False
                change_block = False
            else:
                # Add current piece to locked positions in grid
                shape_pos = current_block.convert_shape_format()
                for pos in shape_pos:
                    p = (pos[0], pos[1])
                    grid.locked_positions[p] = current_block.color

                # Handle scoring and redrawing of the screen if rows are removed
                lines = grid.clear_rows()
                if lines > 0:
                    combo += lines
                    score += new_score(lines, level, combo, soft)
                    level += lines

                    # Remove the rows immediately
                    grid.grid = grid.create_grid()
                    playfield.update(current_block, next_block, score, high_score, level)
                else:
                    combo = 1
                    level += 1
                soft = 1

            # Reset variables for next block
            current_block = next_block
            next_block = get_block(grid)
            change_block = False
            lock = False
            lock_time = 0

            # Check gravity
            if level <= 500:  # Level 500 and above is max speed
                gkeys = list(INTERNAL_GRAVITY.keys())
                for i in range(len(gkeys)):
                    if gkeys[i] == level or gkeys[i] < level < gkeys[i+1]:
                        gravity = DENOMINATOR / INTERNAL_GRAVITY[gkeys[i]]
            else:
                gravity = DENOMINATOR / INTERNAL_GRAVITY[500]

            # Lock and ARE delay
            pygame.time.delay(lock_delay) if lines == 0 else pygame.time.delay(ARE_delay)

        if grid.check_lost():
            playfield.draw_text_middle("YOU LOST!", 80, (255,255,255))
            pygame.time.delay(2000)
            update_score(score)
            run = False

        if level == 1000:
            playfield.draw_text_middle("YOU WON!!", 80, (255,255,255))
            pygame.time.delay(2000)
            update_score(score)
            run = False


if __name__ == "__main__":
    win = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
    pygame.display.set_caption("Block Master")
    pygame.key.set_repeat(256, 17)
    main_menu(win)
