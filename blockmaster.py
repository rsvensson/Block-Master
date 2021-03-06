#!/usr/bin/env python

import os
import math
import random
import pygame

# TODO: Wall kicks still don't behave quite as they should. Specifically for L, J and T.
# TODO: Blocks don't fall instantly to the bottom on level 500+.
# TODO: There's still some occasional glitches with the clear_rows method.
# TODO: Implement timer display (and use time for determining GM grade)
# TODO: Make blocks spawn exactly like in TGM
# TODO: Make IRS work as in TGM
# TODO: Proper main menu
# TODO: Settings
# TODO: High score list

# GLOBALS VARS
S_WIDTH = 800
S_HEIGHT = 700
PLAY_WIDTH = 300
PLAY_HEIGHT = 600
BLOCK_SIZE = PLAY_WIDTH // 10
GRID_SIZE = (10, 20)  # 10 x 20 grid
TOP_LEFT_X = (S_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = S_HEIGHT - PLAY_HEIGHT - 5  # -5 to ensure our drawing methods leave a 5 pixel buffer at the bottom
MAX_FPS = 60

# COLORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
# TGM Colors
SCOLOR = (141, 0, 141)
ZCOLOR = (0, 148, 0)
ICOLOR = (200, 20, 10)
OCOLOR = (200, 200, 0)
JCOLOR = (0, 32, 190)
LCOLOR = (200, 85, 0)
TCOLOR = (0, 130, 175)
SLOCKED = (90, 0, 90)
ZLOCKED = (0, 80, 0)
ILOCKED = (125, 0, 0)
OLOCKED = (90, 90, 0)
JLOCKED = (0, 15, 110)
LLOCKED = (90, 40, 0)
TLOCKED = (0, 70, 100)

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

# index 0 - 6 represent shape
SHAPES = [S, Z, I, O, J, L, T]
SHAPE_COLORS = [SCOLOR, ZCOLOR, ICOLOR, OCOLOR, JCOLOR, LCOLOR, TCOLOR]
SHAPE_COLORS_LOCKED = [SLOCKED, ZLOCKED, ILOCKED, OLOCKED, JLOCKED, LLOCKED, TLOCKED]

# Start bag with 4 Z blocks, emulating TGM1
BAG = [1, 1, 1, 1]

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

# Grades (key = score)
GRADE = {0:      "9",
         400:    "8",
         800:    "7",
         1400:   "6",
         2000:   "5",
         3500:   "4",
         5500:   "3",
         8000:   "2",
         12000:  "1",
         16000:  "S1",
         22000:  "S2",
         30000:  "S3",
         40000:  "S4",
         52000:  "S5",
         66000:  "S6",
         82000:  "S7",
         100000: "S8",
         120000: "S9",
         126000: "GM"}


class Block(object):
    def __init__(self, x, y, shape, grid):
        self.x = x
        self.y = y
        self.shape = shape
        self.grid = grid
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.locked_color = SHAPE_COLORS_LOCKED[SHAPES.index(shape)]
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
        grid = [[BLACK for x in range(GRID_SIZE[0])] for x in range(GRID_SIZE[1])]

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if (j, i) in self.locked_positions:
                    c = self.locked_positions[(j, i)]
                    grid[i][j] = c

        return grid

    def clear_rows(self) -> int:
        self.grid = self.create_grid()
        rows = []  # Rows to remove
        inc = 0  # How many rows were removed
        for i in range(len(self.grid) - 1, -1, -1):  # Start check grid from below
            row = self.grid[i]
            if BLACK not in row:
                inc += 1
                rows.append(i)  # Index of row that is removed
                for j in range(len(row)):
                    del self.locked_positions[(j, i)]  # Remove the block from locked positions

        # Shift down rows in the grid
        if inc > 0:
            for _ in range(len(rows)):
                row = rows.pop()
                # Sort positions by y-value and go through the list bottom-to-top
                for key in sorted(list(self.locked_positions), key=lambda x: x[1])[::-1]:
                    x, y = key
                    if y < row:  # Below the row that we removed
                        new_key = (x, y + 1)
                        self.locked_positions[new_key] = self.locked_positions.pop(key)

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
        font = pygame.font.SysFont(None, 30)
        label = font.render("Next", 1, WHITE)

        sx = self.top_left_x + self.pfield_width + 50
        sy = self.top_left_y
        format = block.shape[block.rotation % len(block.shape)]

        for i, line in enumerate(format):
            row = list(line)
            for j, col in enumerate(row):
                if col == "0":
                    pygame.draw.rect(self.surface, block.color, (sx + j * BLOCK_SIZE, sy + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
                    pygame.draw.rect(self.surface, WHITE, (sx + j * BLOCK_SIZE, sy + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

        self.surface.blit(label, (sx + 10, sy))

    def _draw_window(self, score=0, last_score=0, grade=0, level=0):
        self.surface.fill((0, 0, 0))
        pygame.font.init()
        font = pygame.font.SysFont(None, 60)
        label = font.render("Block Master", 1, WHITE)
        self.surface.blit(label, (self.top_left_x + self.pfield_width / 2 - label.get_width() / 2, 30))

        # Current score
        font = pygame.font.SysFont(None, 30)
        label = font.render("Score: " + str(score), 1, WHITE)
        sx = self.top_left_x + self.pfield_width + 50
        sy = self.top_left_y + self.pfield_height / 2 + 100
        self.surface.blit(label, (sx, sy))

        # High score
        label = font.render("High Score:", 1, WHITE)
        highscore = font.render(str(last_score), 1, WHITE)
        sx = self.top_left_x + self.pfield_width + 50
        sy = self.top_left_y + self.pfield_height / 2
        self.surface.blit(label, (sx, sy))
        self.surface.blit(highscore, (sx, sy + 20))

        # Level
        label = font.render("Level: " + str(level), 1, WHITE)
        sx = self.top_left_x + self.pfield_width + 50
        sy = self.top_left_y + self.pfield_height / 2 - 100
        self.surface.blit(label, (sx, sy))

        # Grade
        label = font.render("Grade: " + str(grade), 1, WHITE)
        sx = self.top_left_x + self.pfield_width + 50
        sy = self.top_left_y + self.pfield_height / 2 - 125
        self.surface.blit(label, (sx, sy))

        # Blocks
        sx = self.top_left_x
        sy = self.top_left_y
        for i in range(len(self.grid.grid)):
            for j in range(len(self.grid.grid[i])):
                pygame.draw.rect(self.surface, self.grid.grid[i][j],
                                 (sx + j * self.block_size, sy + i * self.block_size, self.block_size, self.block_size), 0)
                if not self.grid.grid[i][j] == BLACK:  # Draw white or gray lines on blocks
                    line_color = WHITE if self.grid.grid[i][j] in SHAPE_COLORS else GRAY
                    pygame.draw.rect(self.surface, line_color,
                                     (sx + j * self.block_size, sy + i * self.block_size, self.block_size, self.block_size), 1)

        # Playfield border
        pygame.draw.rect(self.surface, RED, (sx, sy, self.pfield_width, self.pfield_height), 5)

    def draw_text_middle(self, text, size, color):
        font = pygame.font.SysFont(None, size, bold=True)
        label = font.render(text, 1, color)

        sx = self.top_left_x
        sy = self.top_left_y

        self.surface.blit(label, (sx + self.pfield_width / 2 - (label.get_width() / 2),
                                  sy + self.pfield_height / 2 - (label.get_height() * 2)))
        pygame.display.update()

    def update(self, block: Block, next_block: Block,
               score=0, high_score=0, grade=0, level=0):
        self._draw_window(score, high_score, grade, level)
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
            new = Block(x, y, random.choice(SHAPES), grid)
            if new.shape in BAG:
                continue
            else:
                break

    # Update bag
    BAG.insert(0, new.shape)
    BAG.pop()

    return new


def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont(None, size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (label.get_width() / 2), TOP_LEFT_Y + PLAY_HEIGHT / 2 - label.get_height() * 2))


def set_highscore(score):
    """Write high score to disk"""
    try:
        f = open("data/score.txt", "w+")
    except FileNotFoundError:
        os.mkdir("data", 0o755)
        f = open("data/score.txt", "w+")

    f.write(str(score))
    f.close()

def get_highscore():
    """Read high score from disk"""
    try:
        with open("data/score.txt", "r") as f:
            lines = f.readlines()
            score = lines[0].strip()
    except FileNotFoundError:
        return 0

    return int(score)


def get_score(lines, level=1, combo=1, soft=1, bravo=1):
    """Calculates score depending on lines cleared, current level, combos etc.
       lines: How many lines were cleared.
       level: Which level we're at.
       combo: How many blocks in a row that have cleared lines.
       soft: How many frames the player pressed down.
       bravo: Did the block completely clear the well?"""

    return (math.ceil((level + lines) / 4) + soft) * lines * combo * bravo


def get_grade(score, t1=None, t2=None, t3=None):
    """Determines the grade based on score.
       score: the score to determine grade from.
       t1: Time to level 300
       t2: Time to level 500
       t3: Time to level 999"""

    grade = "9"
    gscores = list(GRADE)
    for i, gscore in enumerate(gscores):
        if gscores[i] < score < gscores[i+1]:
            grade = GRADE[gscore]
            break

    if grade is "GM":
        if t1 is not None and t2 is not None and t3 is not None:
            # Make sure we pass the time constraints
            # t1 <= 4:15, t2 <= 7:00, t3 <= 13:30
            if t1 <= 255 and t2 <= 420 and t3 <= 810:
                pass
        else:
            grade = "S9"

    return grade


def main_menu(win):
    run = True
    while run:
        win.fill(BLACK)
        draw_text_middle("Press Any Key To Play", 60, WHITE, win)
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

    # Movement
    imove = True  # Initial move
    moving = False
    mleft = False
    mright = False
    mdown = False
    mtime = 0

    # Scoring variables
    high_score = get_highscore()
    score = 0
    level = 0
    soft = 1
    combo = 1
    grade = get_grade(score)

    # Fall speed
    gravity = DENOMINATOR / INTERNAL_GRAVITY[0]

    while run:
        grid.grid = grid.create_grid()

        # Fall on delta time
        dt = clock.tick(MAX_FPS)
        fall_time += dt
        if fall_time > gravity * dt:
            fall_time = 0
            if not current_block.move("down"):
                lock = True
            else:
                lock = False
                lock_time = 0

        if lock:
            lock_time += dt
            if lock_time > 30*16:
                change_block = True

        # User input
        for event in pygame.event.get():
            # Quitting
            if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                run = False
            else:
                if event.type == pygame.MOUSEMOTION:
                    continue
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z and not has_rotated:
                        current_block.rotate("left")
                        has_rotated = True
                    if event.key == pygame.K_x and not has_rotated:
                        current_block.rotate("right")
                        has_rotated = True
                    if event.key == pygame.K_LEFT:
                        mleft = True
                    if event.key == pygame.K_RIGHT:
                        mright = True
                    if event.key == pygame.K_DOWN:
                        mdown = True
                        soft += dt
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_z or event.key == pygame.K_x:
                        has_rotated = False
                    if event.key == pygame.K_LEFT:
                        mleft = False
                    if event.key == pygame.K_RIGHT:
                        mright = False
                    if event.key == pygame.K_DOWN:
                        mdown = False
                        change_block = False

        # Movement
        if not mleft and not mright and not mdown:
            # TODO: The logic makes it possible to keep "momentum" if you switch directions quickly
            mtime = 0
            imove = True
            moving = False
        else:
            mdelay = 0 if imove else 16 if moving else 256
            if mtime >= mdelay:
                if mleft:
                    current_block.move("left")
                if mright:
                    current_block.move("right")
                if mdown:
                    if not current_block.move("down"):
                        change_block = True

                if imove:
                    imove = False
                    moving = False
                elif moving:
                    imove = False
                else:
                    imove = False
                    moving = True
                mtime = 0
            mtime += dt

        # Block hit ground
        if change_block:
            # Double check if we should really change block.
            if current_block.move("down"):
                lock_time = 0
                lock = False
                change_block = False
            else:
                # Add current piece to locked positions in grid
                shape_pos = current_block.convert_shape_format()
                for pos in shape_pos:
                    p = (pos[0], pos[1])
                    grid.locked_positions[p] = current_block.locked_color

                # Handle scoring
                lines = grid.clear_rows()
                if lines > 0:
                    bravo = 4 if len(grid.locked_positions) == 0 else 1
                    combo += 2*lines-2 if combo > 1 else lines
                    score += get_score(lines, level, combo, soft, bravo)
                    level += lines
                else:
                    combo = 1
                    level += 1
                soft = 1
                grade = get_grade(score)

                # Update immediately
                grid.grid = grid.create_grid()
                playfield.update(current_block, next_block, score, high_score, grade,
                                 level-lines-1 if lines == 0 else level-lines)  # Don't update level until next loop

                # Reset variables for next block
                current_block = next_block
                next_block = get_block(grid)
                change_block = False
                lock = False
                lock_time = 0

                # Check gravity
                if level < 500:  # Level 500 and above is max speed
                    gkeys = list(INTERNAL_GRAVITY)
                    for i in range(len(gkeys)):
                        if gkeys[i] == level or gkeys[i] < level < gkeys[i+1]:
                            gravity = DENOMINATOR / INTERNAL_GRAVITY[gkeys[i]]
                else:
                    gravity = DENOMINATOR / INTERNAL_GRAVITY[500]

                # Lock and ARE delay
                pygame.time.delay(lock_delay) if lines == 0 else pygame.time.delay(ARE_delay)

        grid.update(current_block)
        playfield.update(current_block, next_block, score, high_score, grade, level)

        if grid.check_lost():
            playfield.draw_text_middle("YOU LOST!", 80, WHITE)
            pygame.time.delay(2000)
            run = False

        if level == 1000:
            playfield.draw_text_middle("YOU WON!!", 80, WHITE)
            pygame.time.delay(2000)
            run = False

    # Write new high score to file
    if score > high_score:
        set_highscore(score)


if __name__ == "__main__":
    pygame.font.init()
    win = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
    pygame.display.set_caption("Block Master")
    main_menu(win)
