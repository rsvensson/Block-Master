#!/usr/bin/env python
import random
import sys
import os
import pygame
from pygame.locals import *
from pygame.math import Vector2


def load_image(name, colorkey=None):
    fullname = os.path.join("data", name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as err:
        print("Cannot load image: ", fullname)
        raise SystemExit(err)
    return image, image.get_rect()


class Input:
    def __init__(self, block):
        self.block = block

    def move(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    self.block.movepos[0] -= 1
                elif event.key == K_RIGHT:
                    self.block.movepos[0] += 1
                elif event.key == K_DOWN:
                    self.block.movepos[1] += 1
            elif event.type == KEYUP:
                self.block.movepos[0] = 0
                self.block.movepos[1] = 0


class Block(pygame.sprite.Sprite):

    def __init__(self, shape):
        shapes = {"I": "I.png",
                  "J": "J.png",
                  "L": "L.png",
                  "O": "O.png",
                  "S": "S.png",
                  "Z": "Z.png",
                  "T": "T.png"}

        pivot = {"I": (10, 20),
                 "J": (10, 20)}

        super(Block, self).__init__()
        self.image, self.rect = load_image(shapes[shape])
        self.orig_image = self.image
        self.pos = Vector2(pivot[shape])
        self.offset = Vector2(50, 0)
        self.angle = 0
        self.screen = pygame.display.get_surface()
        self.area = self.screen.get_rect()
        self.movepos = [0, 0]

    def move(self, dir):
        if dir == "left":
            self.movepos[0] = self.movepos[0] - 42
        elif dir == "right":
            self.movepos[0] = self.movepos[0] + 42
        elif dir == "down":
            self.movepos[1] = self.movepos[1] + 42

    def rotate(self, dir):
        if dir == "left":
            self.image = pygame.transform.rotate(self.orig_image, self.angle + 90)
            offset_rotated = self.offset.rotate(self.angle + 90)
            self.rect = self.image.get_rect(center=self.pos+offset_rotated)
            if self.angle == 270:
                self.angle = 0
            else:
                self.angle += 90
        elif dir == "right":
            self.image = pygame.transform.rotate(self.orig_image, self.angle - 90)
            offset_rotated = self.offset.rotate(self.angle - 90)
            self.rect = self.image.get_rect(center=self.pos+offset_rotated)
            if self.angle == 90:
                self.angle = 0
            else:
                self.angle -= 90

    def update(self):
        newpos = self.rect.move(self.movepos)
        if self.area.contains(newpos):
            self.rect = newpos
        pygame.event.pump()


class Well(pygame.sprite.Sprite):
    def __init__(self, x_size, y_size):
        pygame.sprite.Sprite.__init__(self)
        self.x_size = x_size
        self.y_size = y_size

    def create_well(self):
        pass
    

def main():
    blocktypes = ["I", "J", "L", "S", "Z", "T", "O"]
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Block Master")

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))

    block = Block("J")
    blocksprite = pygame.sprite.RenderPlain(block)

    inputhandler = Input(block)

    screen.blit(background, (0, 0))
    pygame.display.flip()

    clock = pygame.time.Clock()

    while 1:
        clock.tick(60)

        """for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_LEFT:
                    block.move("left")
                elif event.key == K_RIGHT:
                    block.move("right")
                elif event.key == K_DOWN:
                    block.move("down")
                elif event.key == K_a:
                    block.rotate("left")
                elif event.key == K_o:
                    block.rotate("right")
            elif event.type == KEYUP:
                if event.key == K_LEFT or event.key == K_RIGHT or event.key == K_DOWN:
                    block.movepos = [0, 0]
                    block.moving = False"""
        inputhandler.move()

        screen.blit(background, block.rect, block.rect)
        blocksprite.update()
        blocksprite.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()
