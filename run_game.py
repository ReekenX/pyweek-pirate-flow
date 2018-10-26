#! /usr/bin/env python

import os
import math
import pygame
import pygame.locals
import configparser

# constants
SCREEN_WIDTH = 928
SCREEN_HEIGHT = 736
TILE_WIDTH = 32
TILE_HEIGHT = 32


class Game(object):
    def __init__(self):
        # enemy objects
        self.bullets = []
        self.cannons = []
        self.explosions = []

        # load player ship configuration
        self.player = Player(self)

        # load level/map configuration
        self.level = Level(self)
        self.level.load_file('./data/levels/1.map')
        self.clock = pygame.time.Clock()

    def tick(self):
        self.clock_elapsed = game.clock.tick(50)
        return self.clock_elapsed


class Cannon(object):
    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y
        self.max_distance = 10
        self.sprite = pygame.image.load('./data/sprites/cannon.png').convert_alpha()
        self.fire_timer = 0
        self.fire_frequency = 2000 # in miliseconds

    def should_fire(self):
        return math.sqrt((self.x - self.game.player.x) ** 2 + (self.y - self.game.player.y)**2) < self.max_distance

    def image(self):
        return self.sprite

    def move(self):
        if self.fire_timer > 0:
            self.fire_timer -= self.game.clock_elapsed

        if self.should_fire() and self.fire_timer <= 0:
            self.fire_timer = self.fire_frequency
            self.game.bullets.append(Bullet(self.x, self.y, 'down'))


class Explosion(object):
    def __init__(self, game, x, y, size):
        self.game = game
        self.x = x
        self.y = y
        self.frame_no = -1
        self.frame_frequency = 70 # in miliseconds
        self.frame_time = 0
        self.frames = [
            pygame.image.load('./data/sprites/explosion3.png').convert_alpha(),
            pygame.image.load('./data/sprites/explosion2.png').convert_alpha(),
            pygame.image.load('./data/sprites/explosion1.png').convert_alpha(),
        ]
        if size == 'tiny':
            self.size = (TILE_WIDTH, TILE_HEIGHT)
        elif size == 'small':
            self.size = (TILE_WIDTH * 2, TILE_HEIGHT * 2)
        elif size == 'medium':
            self.size = (TILE_WIDTH * 3, TILE_HEIGHT * 3)

    def image(self):
        if self.frame_time > 0:
            self.frame_time -= self.game.clock_elapsed
        else:
            self.frame_time = self.frame_frequency
            self.frame_no += 1
        return pygame.transform.scale(self.frames[self.frame_no], self.size)

    def finished(self):
        return self.frame_no == len(self.frames) - 1


class Bullet(object):
    def __init__(self, x, y, position):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.max_distance = 8
        self.position = position
        self.sprite = pygame.transform.scale(pygame.image.load('./data/sprites/bullet.png').convert_alpha(), (TILE_WIDTH * 2, TILE_HEIGHT * 2))

    def image(self):
        return self.sprite

    def finished(self):
        return abs(self.start_x - self.x) > self.max_distance or abs(self.start_y - self.y) > self.max_distance

    def move(self):
        if self.position == 'up': self.y -= 1
        if self.position == 'down': self.y += 1
        if self.position == 'right': self.x += 1
        if self.position == 'left': self.x -= 1

    def reaches(self, obj):
        return math.sqrt((self.x - obj.x) ** 2 + (self.y - obj.y)**2) < 1


class Player(object):
    def __init__(self, game):
        self.game = game
        self.x = 0
        self.y = 0
        self.position = 'down'
        self.energy = 5
        self.down_image = image = pygame.transform.scale(
                pygame.image.load('./data/sprites/player.png').convert_alpha(),
                (TILE_WIDTH * 2, TILE_HEIGHT * 2))
        self.fire_timer = 0
        self.fire_frequency = 1000 # in miliseconds

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def image(self):
        if self.position == 'right':
            return pygame.transform.rotate(self.down_image, 90)
        if self.position == 'up':
            return pygame.transform.rotate(self.down_image, 180)
        if self.position == 'left':
            return pygame.transform.rotate(self.down_image, 270)
        else:
            return self.down_image

    def move(self):
        if self.fire_timer > 0:
            self.fire_timer -= self.game.clock_elapsed

    def up(self):
        if self.game.level.get_tile(self.x, self.y - 1)['name'] != 'sand' and self.game.level.get_tile(self.x, self.y - 2)['name'] != 'sand':
            self.y -= 1
            self.position = 'up'
            return True
        else:
            return False

    def down(self):
        if self.game.level.get_tile(self.x, self.y + 1)['name'] != 'sand' and self.game.level.get_tile(self.x, self.y + 2)['name'] != 'sand':
            self.y += 1
            self.position = 'down'
            return True
        else:
            return False

    def left(self):
        if self.game.level.get_tile(self.x - 1, self.y)['name'] != 'sand' and self.game.level.get_tile(self.x - 2, self.y)['name'] != 'sand':
            self.x -= 1
            self.position = 'left'
            return True
        else:
            return False

    def right(self):
        if self.game.level.get_tile(self.x + 1, self.y)['name'] != 'sand' and self.game.level.get_tile(self.x + 2, self.y)['name'] != 'sand':
            self.x += 1
            self.position = 'right'
            return True
        else:
            return False

    def fire(self):
        if self.fire_timer <= 0:
            self.game.bullets.append(Bullet(self.x, self.y, self.position))
            self.fire_timer = self.fire_frequency


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
    def __init__(self, game):
        self.game = game

    def load_file(self, filename):
        self.map = []
        self.images = {}

        # read level appearance
        parser = configparser.ConfigParser()
        parser.read(filename)
        area = parser.get("level", "map").split("\n")

        # read all available objects configurations
        self.keys = {}
        for section in parser.sections():
            desc = dict(parser.items(section))
            if 'name' in desc:
                self.keys[section] = desc

        # save map resolution
        self.width = len(area[0])
        self.height = len(area)

        # construct map
        for y in range(0, self.height):
            self.map.append([])
            for x in range(0, self.width):
                meta = dict(self.keys[area[y][x]])
                meta['image'] = meta['name']
                self.map[y].append(meta)

        self.original_map = self.map

        # normalize map
        for x in range(0, self.width):
            for y in range(0, self.height):
                if self.get_real_tile(x, y)['complex'] == 'no': continue

                tile = self.get_real_tile(x, y)
                if tile['name'] == 'cannon':
                    self.game.cannons.append(Cannon(self.game, x, y))
                    self.map[y][x] = self.keys[tile['act_as']]
                    self.map[y][x]['image'] = self.keys[tile['act_as']]['name']
                    continue
                elif tile['name'] == 'player':
                    self.map[y][x] = self.keys['.']
                    self.map[y][x]['image'] = 'water'
                    self.game.player.set_position(x, y)

                name = self.get_tile(x, y)['name']
                left = self.get_tile(x - 1, y)['name']
                right = self.get_tile(x + 1, y)['name']
                top = self.get_tile(x, y - 1)['name']
                bottom = self.get_tile(x, y + 1)['name']

                hashed = left[0] + right[0] + top[0] + bottom[0]

                # choose sand sprite based on sand/land position
                if os.path.isfile('./data/sprites/{}-{}.png'.format(name, hashed)):
                    self.map[y][x]['image'] = '{}-{}'.format(name, hashed)
                else:
                    self.map[y][x]['image'] = 'water' # so we can spot missing sprite in the game

    def get_sprite(self, name):
        # try to get image from cache
        if name in self.images:
            return self.images[name]

        # cache image for quick reuse
        image = pygame.transform.scale(
                pygame.image.load('./data/sprites/' + name + '.png').convert_alpha(),
                (TILE_WIDTH, TILE_HEIGHT))
        self.images[name] = image
        return self.images[name]

    def get_tile(self, x, y):
        try:
            tile = self.map[y][x]
            if 'act_as' in tile:
                tile = dict(self.keys[tile['act_as']])
                tile['image'] = tile['name']
                return tile
            return tile
        except IndexError:
            return self.keys['.']

    def get_real_tile(self, x, y):
        try:
            return self.original_map[y][x]
        except IndexError:
            return self.keys['.']


if __name__=='__main__':
    # init pygame
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption('Pirate Flow - Pygame #26')
    pygame.key.set_repeat(100, 100)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF, 32)
    screen.fill((255, 255, 255))

    # load game storage
    game = Game()

    # load screen configuration
    camera = Camera(game.level.width * TILE_WIDTH - SCREEN_WIDTH, game.level.height * TILE_HEIGHT - SCREEN_HEIGHT)

    # get background tile - water
    water_tile = pygame.image.load('./data/sprites/water.png').convert_alpha()
    water_tile = pygame.transform.scale(water_tile, (TILE_WIDTH, TILE_HEIGHT))

    sandbg = pygame.image.load('./data/sprites/sandbg.png').convert_alpha()
    sandbg = pygame.transform.scale(sandbg, (TILE_WIDTH, TILE_HEIGHT))

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
                tile = game.level.get_tile(x + camera_x, y + camera_y)
                if tile['name'] != 'water':
                    if tile['name'] == 'sand':
                        screen.blit(sandbg, (x * TILE_WIDTH, y * TILE_HEIGHT))
                    screen.blit(game.level.get_sprite(tile['image']), (x * TILE_WIDTH, y * TILE_HEIGHT))

        # render player
        game.player.move()
        image = game.player.image()
        screen.blit(image, (int((game.player.x - camera_x) * TILE_WIDTH) + int(TILE_WIDTH / 2) - int(image.get_width() / 2), int((game.player.y - camera_y) * TILE_HEIGHT) + int(TILE_HEIGHT / 2) - int(image.get_height() / 2)))

        # render bullets and see if somebody hit somebody
        for bullet in game.bullets:
            bullet.move()
            if bullet.finished():
                missed = True
                if bullet.reaches(game.player):
                    missed = False
                    game.explosions.append(Explosion(game, bullet.x, bullet.y, 'medium'))
                else:
                    for cannon in game.cannons:
                        if bullet.reaches(cannon):
                            missed = False
                            game.cannons.remove(cannon)
                            game.explosions.append(Explosion(game, bullet.x, bullet.y, 'small'))
                            break # same bullet can't hit few items
                game.bullets.remove(bullet)
            else:
                image = bullet.image()
                screen.blit(image, (int((bullet.x - camera_x) * TILE_WIDTH) + int(TILE_WIDTH / 2) - int(image.get_width() / 2), int((bullet.y - camera_y) * TILE_HEIGHT) + int(TILE_HEIGHT / 2) - int(image.get_height() / 2)))

        # render bullet explosions
        for explosion in game.explosions:
            if explosion.finished():
                game.explosions.remove(explosion)
            else:
                image = explosion.image()
                screen.blit(image, (int((explosion.x - camera_x) * TILE_WIDTH) + int(TILE_WIDTH / 2) - int(image.get_width() / 2), int((explosion.y - camera_y) * TILE_HEIGHT) + int(TILE_HEIGHT / 2) - int(image.get_height() / 2)))

        # render first enemy group - cannons
        for cannon in game.cannons:
            cannon.move()
            image = cannon.image()
            screen.blit(image, (int((cannon.x - camera_x) * TILE_WIDTH) + int(TILE_WIDTH / 2) - int(image.get_width() / 2), int((cannon.y - camera_y) * TILE_HEIGHT) + int(TILE_HEIGHT / 2) - int(image.get_height() / 2)))

        # debug text
        #  text = myfont.render('{} bullets'.format(len(player.bullets)), False, (0, 0, 0))
        #  screen.blit(text, (10, 10))

        # render and limit fps to 50
        pygame.display.flip()
        game.tick()

        # handle keypresses/gameplay
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                playing = False
            elif event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    if game.player.down():
                        camera.down()
                elif event.key == pygame.K_UP:
                    if game.player.up():
                        camera.up()
                elif event.key == pygame.K_LEFT:
                    if game.player.left():
                        camera.left()
                elif event.key == pygame.K_RIGHT:
                    if game.player.right():
                        camera.right()
                elif event.key == pygame.K_SPACE:
                    game.player.fire()
