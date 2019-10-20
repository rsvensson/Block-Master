#!/usr/bin/env python

import cocos
import cocos.collision_model as cm
import cocos.euclid as eu
from cocos import scene
from cocos.text import Label
from cocos.layer import Layer, ColorLayer
from cocos.sprite import Sprite
from cocos.director import director
from cocos.actions import *
from cocos.scenes import *
from pyglet.window.key import symbol_string
from pyglet.window import key
from random import randint


class Mover(Move):
    def step(self, dt):
        super().step(dt)
        vel_x = (keyboard[key.RIGHT] - keyboard[key.LEFT]) * 500
        vel_y = (keyboard[key.UP] - keyboard[key.DOWN]) * 500
        self.target.velocity = (vel_x, vel_y)


class Block(Sprite):
    def __init__(self, block, xy = (0, 0)):
        blocktypes = {0: "I.png",
                      1: "J.png",
                      2: "L.png",
                      3: "O.png",
                      4: "S.png",
                      5: "T.png",
                      6: "Z.png"}

        super(Block, self).__init__("data/" + blocktypes[block], xy)

        self.velocity = (0, 0)
        self.do(Mover())


class BlockLayer(Layer):
    is_event_handler = True

    def __init__(self):
        super(BlockLayer, self).__init__()

        # Keep track of which blocks have appeared, mimicking behavior of TGM1
        self.bag = [6, 6, 6 ,6]  # Start with 4 Z-blocks in bag

        # List of previous blocks
        self.old_blocks = []

        self.block = self.next_block()
        self.block.position = 320, 240
        self.add(self.block)

    def next_block(self):
        """Based on TGM1 behavior"""

        # Pick a number at random and see if it's in the bag
        # If it can't get a unique one in 4 tries it gives up
        for i in range(0, 4):
            new = randint(0, 6)
            if new in self.bag:
                continue
            else:
                break

        # Insert new block at start of the bag, then remove the last block
        self.bag.insert(0, new)
        self.bag.pop(4)

        return Block(new)

    def update(self):
        self.block = self.next_block()
        self.block.position = 320, 240
        self.add(self.block)

"""    def on_key_press(self, key, modifiers):
        move_left = MoveBy((-42, 0), 0)
        move_down = MoveBy((0, -42), 0)
        rot_left = RotateBy(-90, 0)

        if symbol_string(key) == "LEFT":
            self.block.do(move_left)
        elif symbol_string(key) == "RIGHT":
            self.block.do(Reverse(move_left))
        elif symbol_string(key) == "DOWN":
            self.block.do(move_down)
        elif symbol_string(key) == "SPACE":
            self.update()

        if symbol_string(key) == "A":
            self.block.do(rot_left)
        elif symbol_string(key) == "O":
            self.block.do(Reverse(rot_left))"""


if __name__ == "__main__":
    director.init(width=1280, height=720, caption="Block Master")

    keyboard = key.KeyStateHandler()
    director.window.push_handlers(keyboard)
    
    director.run(scene.Scene(BlockLayer()))