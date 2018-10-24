#! /usr/bin/env python

import pygame
import pygame.locals
import configparser

# constants
SCREEN_WIDTH = 928
SCREEN_HEIGHT = 736
TILE_WIDTH = 32
TILE_HEIGHT = 32


class Player(object):
    def load_file(self, filename):
        parser = configparser.ConfigParser()
        parser.read(filename)
        self.x, self.y = parser.get("player", "coords").split(",")
        self.x = int(self.x)
        self.y = int(self.y)

    def image(self):
        return pygame.image.load('./data/sprites/player-ship1.png')


class Camera(object):
    def __init__(self, world_width, world_height):
        self.x = 0
        self.y = 0
        self.world_width = world_width
        self.world_height = world_height

    def up(self):
        if self.y - TILE_HEIGHT >= 0:
            self.y -= TILE_HEIGHT

    def down(self):
        if self.y + TILE_HEIGHT <= self.world_height:
            self.y += TILE_HEIGHT

    def left(self):
        if self.x - TILE_WIDTH >= 0:
            self.x -= TILE_WIDTH

    def right(self):
        if self.x + TILE_WIDTH <= self.world_width:
            self.x += TILE_WIDTH


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
            desc = dict(parser.items(section))
            if 'name' in desc:
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
    pygame.font.init()
    pygame.display.set_caption('Pirate Flow - Pygame #26')
    pygame.key.set_repeat(500, 100)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill((255, 255, 255))

    # load level configuration
    level = Level()
    level.load_file('./data/levels/1.map')

    # load player ship configuration
    player = Player()
    player.load_file('./data/levels/1.map')

    # load screen configuration
    camera = Camera(level.width * TILE_WIDTH - SCREEN_WIDTH, level.height * TILE_HEIGHT - SCREEN_HEIGHT)

    # get background tile - water
    water_tile = pygame.image.load('./data/sprites/water.png')
    water_tile = pygame.transform.scale(water_tile, (TILE_WIDTH, TILE_HEIGHT))

    myfont = pygame.font.SysFont('Arial', 30)

    water = 0
    playing = True
    while playing:
        water += 2
        if water == 32: water = 0
        for x in range(-1, int(SCREEN_WIDTH / TILE_WIDTH) + 1):
            for y in range(-1, int(SCREEN_HEIGHT / TILE_HEIGHT) + 1):
                # render floating water - background layer
                screen.blit(water_tile, (x * TILE_WIDTH + water, y * TILE_HEIGHT + water))

                camera_x = int(camera.x / TILE_WIDTH)
                camera_y = int(camera.y / TILE_HEIGHT)

                # render tiles
                tile = level.get_tile(x + camera_x, y + camera_y)
                if tile['name'] != 'water':
                    screen.blit(level.get_sprite(tile['image']), (x * TILE_WIDTH, y * TILE_HEIGHT))

                # render player
                screen.blit(player.image(), (int((player.x - camera_x) * TILE_WIDTH), int((player.y - camera_y) * TILE_HEIGHT)))

                # debug text
                text = myfont.render('{} x {}'.format(camera_x, camera_y), False, (0, 0, 0))
                screen.blit(text, (10, 10))

        # render and limit fps to 40
        pygame.display.flip()
        pygame.time.Clock().tick(40)

        # handle keypresses/gameplay
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                playing = False
            elif event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    camera.down()
                elif event.key == pygame.K_UP:
                    camera.up()
                elif event.key == pygame.K_LEFT:
                    camera.left()
                elif event.key == pygame.K_RIGHT:
                    camera.right()
