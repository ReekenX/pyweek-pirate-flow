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
        self.images = {}

        # read level appearance
        parser = configparser.ConfigParser()
        parser.read(filename)
        area = parser.get("level", "map").split("\n")

        # read all available objects configurations
        keys = {}
        for section in parser.sections():
            if len(section) == 1:
                desc = dict(parser.items(section))
                keys[section] = desc

        # save map resolution
        self.width = len(area[0])
        self.height = len(area)

        # construct map
        for y in range(0, self.height):
            self.map.append([])
            for x in range(0, self.width):
                name = keys[area[y][x]]['name']
                if name == 'sand':
                    self.map[y].append({
                        'name': 'sand',
                        'image': 'sand1'
                    })
                else:
                    self.map[y].append({'name': name, 'image': name})

        # normalize map
        for x in range(0, self.width):
            for y in range(0, self.height):
                if self.get_tile(x, y)['name'] != 'sand': continue

                name = self.get_tile(x, y)['name']
                left = self.get_tile(x - 1, y)['name']
                right = self.get_tile(x + 1, y)['name']
                top = self.get_tile(x, y - 1)['name']
                bottom = self.get_tile(x, y + 1)['name']

                hashed = left[0] + right[0] + top[0] + bottom[0]

                # choose sand sprite based on sand/land position
                if hashed == 'wsws': self.map[y][x]['image'] = 'sand1'
                elif hashed == 'sswg': self.map[y][x]['image'] = 'sand2'
                elif hashed == 'swws': self.map[y][x]['image'] = 'sand3'
                elif hashed == 'wgss': self.map[y][x]['image'] = 'sand4'
                elif hashed == 'gwss': self.map[y][x]['image'] = 'sand5'
                elif hashed == 'wssw': self.map[y][x]['image'] = 'sand6'
                elif hashed == 'ssgw': self.map[y][x]['image'] = 'sand7'
                elif hashed == 'swsw': self.map[y][x]['image'] = 'sand8'
                else: self.map[y][x]['image'] = 'water'

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
            return self.map[y][x]
        except IndexError:
            return {'name': 'water'}


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
    for x in range(0, int(SCREEN_WIDTH / TILE_WIDTH) + 1):
        for y in range(0, int(SCREEN_HEIGHT / TILE_HEIGHT) + 1):
            screen.blit(water_tile, (x * TILE_WIDTH, y * TILE_HEIGHT))
            tile = level.get_tile(x, y)
            if tile['name'] != 'water':
                screen.blit(level.get_sprite(tile['image']), (x * TILE_WIDTH, y * TILE_HEIGHT))

    pygame.display.flip()
    while pygame.event.wait().type != pygame.locals.QUIT:
        pass
