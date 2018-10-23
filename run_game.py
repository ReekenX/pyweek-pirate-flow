#! /usr/bin/env python

import pygame
import pygame.locals
import configparser

# constants
SCREEN_WIDTH = 928
SCREEN_HEIGHT = 736
TILE_WIDTH = 32
TILE_HEIGHT = 32

class Level(object):
    def load_file(self, filename):
        self.map = []
        self.key = {}
        self.images = {}
        parser = configparser.ConfigParser()
        parser.read(filename)
        self.map = parser.get("level", "map").split("\n")
        for section in parser.sections():
            if len(section) == 1:
                desc = dict(parser.items(section))
                self.key[section] = desc

        self.width = len(self.map[0])
        self.height = len(self.map)

    def get_sprite(self, name):
        # try to get image from cache
        if name in self.images:
            return self.images[name]

        # cache image for quick reuse
        image = pygame.transform.scale(
                pygame.image.load('./data/sprites/' + name + '.png'),
                (TILE_WIDTH, TILE_HEIGHT))
        self.images[name] = image
        return self.images[name]

    def get_tile(self, x, y):
        try:
            char = self.map[y][x]
        except IndexError:
            return None

        try:
            return self.key[char]
        except KeyError:
            return None


if __name__=='__main__':

    # init pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill((255, 255, 255))

    # load level configuration
    level = Level()
    level.load_file('./data/levels/1.map')

    # draw background - water
    water_tile = pygame.image.load('./data/sprites/water.png')
    water_tile = pygame.transform.scale(water_tile, (TILE_WIDTH, TILE_HEIGHT))
    for x in range(0, int(SCREEN_WIDTH / TILE_WIDTH)):
        for y in range(0, int(SCREEN_HEIGHT / TILE_HEIGHT)):
            screen.blit(water_tile, (x * TILE_WIDTH, y * TILE_HEIGHT))
            tile = level.get_tile(x, y)
            if tile is not None and tile['name'] != 'water':
                screen.blit(level.get_sprite(tile['name']), (x * TILE_WIDTH, y * TILE_HEIGHT))

    pygame.display.flip()
    while pygame.event.wait().type != pygame.locals.QUIT:
        pass
