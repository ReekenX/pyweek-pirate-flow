#! /usr/bin/env python

import os
import math
import wave
import configparser
import pygame
import pygame.locals

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
        self.hearths = []
        self.explosions = []

        # load player ship configuration
        self.player = Player(self)

        # load level/map configuration
        self.level = Level(self)
        self.level.load_file('./data/levels/1.map')
        self.clock = pygame.time.Clock()

        # fonts used in the game
        self.regular_font = pygame.font.Font('./data/fonts/font.ttf', 16)
        self.title_font = pygame.font.Font('./data/fonts/font.ttf', 64)

        # has gameplay started?
        self.started = False

        # load background music
        pygame.mixer.init()
        pygame.mixer.music.load("./data/music/bg.mp3")
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1, 0.0)

    def tick(self):
        # Method used to calculate time elapsed (for animations)
        self.clock_elapsed = game.clock.tick(50)
        return self.clock_elapsed


class Hearth(object):
    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y
        self.sprite = pygame.transform.scale(pygame.image.load('./data/sprites/hearth.png').convert_alpha(), (TILE_WIDTH, TILE_HEIGHT))

    def image(self):
        return self.sprite

    def reaches(self, obj):
        return math.sqrt((self.x - obj.x) ** 2 + (self.y - obj.y)**2) < 1


class Cannon(object):
    def __init__(self, game, x, y, position):
        self.game = game
        self.x = x
        self.y = y
        self.position = position
        self.max_distance = 6

        # rotate canon based on it's position
        if self.position == 'left':
            self.sprite = pygame.transform.rotate(pygame.image.load('./data/sprites/cannon.png').convert_alpha(), 180)
        elif self.position == 'right':
            self.sprite = pygame.image.load('./data/sprites/cannon.png').convert_alpha()
        elif self.position == 'up':
            self.sprite = pygame.transform.rotate(pygame.image.load('./data/sprites/cannon.png').convert_alpha(), 90)
        elif self.position == 'down':
            self.sprite = pygame.transform.rotate(pygame.image.load('./data/sprites/cannon.png').convert_alpha(), 270)

        self.fire_timer = 0
        self.fire_frequency = 2000 # in miliseconds

    def distance_from_player(self):
        return math.sqrt((self.x - self.game.player.x) ** 2 + (self.y - self.game.player.y)**2)

    def should_fire(self):
        # no need to fire if game has not started yet
        if not self.game.started:
            return False

        # no need to fire when player is dead
        if not self.game.player.is_alive:
            return False

        # no need to fire is player is behind
        if self.position == 'down' and self.y > self.game.player.y:
            return False
        elif self.position == 'up' and self.y < self.game.player.y:
            return False
        elif self.position == 'right' and self.x > self.game.player.x:
            return False
        elif self.position == 'left' and self.x < self.game.player.x:
            return False

        # calculate distance between player and canon and if it's close enough - fire
        return self.distance_from_player() < self.max_distance + 2

    def image(self):
        return self.sprite

    def move(self):
        if self.fire_timer > 0:
            self.fire_timer -= self.game.clock_elapsed

        if self.should_fire() and self.fire_timer <= 0:
            self.fire_timer = self.fire_frequency
            self.game.bullets.append(Bullet(self.x, self.y, self.position, int(self.distance_from_player()) - 1))


class Explosion(object):
    def __init__(self, game, x, y, size):
        self.game = game
        self.x = x
        self.y = y
        self.frame_no = -1
        self.frame_frequency = 50 # in miliseconds
        self.frame_time = 0

        # explosion size is based on exploded object size
        if size == 'tiny':
            self.size = (TILE_WIDTH, TILE_HEIGHT)
        elif size == 'small':
            self.size = (TILE_WIDTH * 2, TILE_HEIGHT * 2)
        elif size == 'medium':
            self.size = (TILE_WIDTH * 3, TILE_HEIGHT * 3)

        # set and scale animation frames
        self.frames = [
            pygame.transform.scale(pygame.image.load('./data/sprites/explosion3.png').convert_alpha(), self.size),
            pygame.transform.scale(pygame.image.load('./data/sprites/explosion2.png').convert_alpha(), self.size),
            pygame.transform.scale(pygame.image.load('./data/sprites/explosion1.png').convert_alpha(), self.size),
        ]

    def image(self):
        if self.frame_time > 0:
            self.frame_time -= self.game.clock_elapsed
        else:
            self.frame_time = self.frame_frequency
            self.frame_no += 1

        return self.frames[self.frame_no]

    def finished(self):
        return self.frame_no == len(self.frames) - 1


class Bullet(object):
    def __init__(self, x, y, position, max_distance):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.max_distance = max_distance
        self.position = position
        self.sprite = pygame.image.load('./data/sprites/bullet.png').convert_alpha()
        self.increase_size = 5
        self.increase_step = 3

    def image(self):
        # make bullet animation - in the middle of distance bullet should be bigger
        if self.percents_traveled() < 50:
            self.increase_size += self.increase_step
        else:
            self.increase_size -= self.increase_step

        size = (int(TILE_WIDTH * 2.5) + int(self.increase_size), int(TILE_HEIGHT * 2.5) + int(self.increase_size))
        return pygame.transform.scale(pygame.image.load('./data/sprites/bullet.png').convert_alpha(), size)

    def percents_traveled(self):
        if self.position == 'up' or self.position == 'down':
            current_distance = abs(self.start_y - self.y)
            return int(current_distance * 100 / self.max_distance)

        if self.position == 'right' or self.position == 'left':
            current_distance = abs(self.start_x - self.x)
            return int(current_distance * 100 / self.max_distance) % 100

    def finished(self):
        return abs(self.start_x - self.x) > self.max_distance or abs(self.start_y - self.y) > self.max_distance

    def move(self):
        if self.position == 'up': self.y -= 0.6
        if self.position == 'down': self.y += 0.6
        if self.position == 'right': self.x += 0.6
        if self.position == 'left': self.x -= 0.6

    def reaches(self, obj):
        return math.sqrt((self.x - obj.x) ** 2 + (self.y - obj.y)**2) < 1


class Player(object):
    def __init__(self, game):
        self.game = game
        self.x = 0
        self.y = 0
        self.position = 'down'
        self.energy = 2
        self.max_energy = 7
        self.down_image = image = pygame.transform.scale(
                pygame.image.load('./data/sprites/player.png').convert_alpha(),
                (TILE_WIDTH * 2, TILE_HEIGHT * 2))
        self.fire_timer = 0
        self.fire_frequency = 1000 # in miliseconds
        self.is_alive = True
        self.fire_distance = 8
        self.dead_timer = 0
        self.dead_delay = 2000 # in miliseconds
        self.score = 0
        self.initialized = False

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.initialized = True

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
        if self.dead_timer > 0:
            self.dead_timer -= self.game.clock_elapsed

    def up(self):
        if self.position == 'down': return False

        if self.game.level.get_tile(self.x, self.y - 1)['name'] != 'sand' and self.game.level.get_tile(self.x, self.y - 2)['name'] != 'sand':
            self.y -= 1
            self.position = 'up'
            return True
        else:
            return False

    def down(self):
        if self.position == 'up': return False

        if self.game.level.get_tile(self.x, self.y + 1)['name'] != 'sand' and self.game.level.get_tile(self.x, self.y + 2)['name'] != 'sand':
            self.y += 1
            self.position = 'down'
            return True
        else:
            return False

    def left(self):
        if self.position == 'right': return False

        if self.game.level.get_tile(self.x - 1, self.y)['name'] != 'sand' and self.game.level.get_tile(self.x - 2, self.y)['name'] != 'sand':
            self.x -= 1
            self.position = 'left'
            return True
        else:
            return False

    def right(self):
        if self.position == 'left': return False

        if self.game.level.get_tile(self.x + 1, self.y)['name'] != 'sand' and self.game.level.get_tile(self.x + 2, self.y)['name'] != 'sand':
            self.x += 1
            self.position = 'right'
            return True
        else:
            return False

    def fire(self):
        if self.fire_timer <= 0:
            self.game.bullets.append(Bullet(self.x, self.y, self.position, self.fire_distance))
            self.fire_timer = self.fire_frequency

    def dead(self):
        self.is_alive = False
        self.dead_timer = self.dead_delay

    def has_lost(self):
        return not self.is_alive and self.dead_timer < 0


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

        # fake map by creating inverse map size to the left
        for y in range(self.height - 1, -1, -1):
            for x in range(self.width - 1, -1, -1):
                meta = dict(self.keys[area[self.height - y - 1][x]])
                meta['image'] = meta['name']
                self.map[y].append(meta)

        # save new faked map resolution
        self.width = len(self.map[0])
        self.height = len(self.map)

        # fake map by creating inverse map to the bottom
        #  for y in range(0, self.height - 1):
            #  self.map.append(self.map[y])

        # save new faked map resolution
        self.width = len(self.map[0])
        self.height = len(self.map)
        self.original_map = self.map

        # normalize map
        for x in range(0, self.width):
            for y in range(0, self.height):
                if self.get_real_tile(x, y)['complex'] == 'no': continue

                tile = self.get_real_tile(x, y)
                if tile['name'] == 'cannon':
                    # fint closest water source so we know where cannon is pointing at
                    position = None
                    if self.get_tile(x - 3, y)['name'] == 'water': position = 'left'
                    if self.get_tile(x + 3, y)['name'] == 'water': position = 'right'
                    if self.get_tile(x, y - 3)['name'] == 'water': position = 'up'
                    if self.get_tile(x, y + 3)['name'] == 'water': position = 'down'
                    self.game.cannons.append(Cannon(self.game, x, y, position))

                    # replace cannon in the map with water
                    self.map[y][x] = self.keys[tile['act_as']]
                    self.map[y][x]['image'] = self.keys[tile['act_as']]['name']
                    continue
                elif tile['name'] == 'player':
                    # set player coordinates from the map
                    if not self.game.player.initialized:
                        self.game.player.set_position(x, y)

                    # replace player place in the map with the water
                    self.map[y][x] = self.keys['.']
                    self.map[y][x]['image'] = 'water'
                elif tile['name'] == 'hearth':
                    # add hearth to the map
                    self.game.hearths.append(Hearth(self.game, x, y))

                    # replace player place in the map with the water
                    self.map[y][x] = self.keys['.']
                    self.map[y][x]['image'] = 'water'

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
        if game.player.is_alive:
            image = game.player.image()
            screen.blit(image, (int((game.player.x - camera_x) * TILE_WIDTH) + int(TILE_WIDTH / 2) - int(image.get_width() / 2), int((game.player.y - camera_y) * TILE_HEIGHT) + int(TILE_HEIGHT / 2) - int(image.get_height() / 2)))

        # render bullets and see if somebody hit somebody
        for bullet in game.bullets:
            bullet.move()
            if bullet.finished():
                missed = True
                if bullet.reaches(game.player):
                    missed = False
                    game.player.energy -= 1
                    if game.player.energy <= 0:
                        game.player.dead()
                    game.explosions.append(Explosion(game, bullet.x, bullet.y, 'medium'))
                    sound = pygame.mixer.Sound('./data/music/explosion.wav')
                    sound.set_volume(0.6)
                    sound.play()
                else:
                    for cannon in game.cannons:
                        if bullet.reaches(cannon):
                            game.player.score += 100
                            missed = False
                            game.cannons.remove(cannon)
                            game.explosions.append(Explosion(game, bullet.x, bullet.y, 'small'))

                            sound = pygame.mixer.Sound('./data/music/explosion.wav')
                            sound.set_volume(0.5)
                            sound.play()
                            break # same bullet can't hit few items
                if missed:
                    game.explosions.append(Explosion(game, bullet.x, bullet.y, 'tiny'))
                    sound = pygame.mixer.Sound('./data/music/explosion.wav')
                    sound.set_volume(0.05)
                    sound.play()
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

        # render special items - hearths
        for hearth in game.hearths:
            if hearth.reaches(game.player):
                # play powerup song
                sound = pygame.mixer.Sound('./data/music/powerup.wav')
                sound.set_volume(0.1)
                sound.play()

                # add health to the user
                if game.player.energy < game.player.max_energy:
                    game.player.energy += 1

                # drop collected item
                game.hearths.remove(hearth)
            else:
                image = hearth.image()
                screen.blit(image, (int((hearth.x - camera_x) * TILE_WIDTH) + int(TILE_WIDTH / 2) - int(image.get_width() / 2), int((hearth.y - camera_y) * TILE_HEIGHT) + int(TILE_HEIGHT / 2) - int(image.get_height() / 2)))

        # render first enemy group - cannons
        for cannon in game.cannons:
            cannon.move()
            image = cannon.image()
            screen.blit(image, (int((cannon.x - camera_x) * TILE_WIDTH) + int(TILE_WIDTH / 2) - int(image.get_width() / 2), int((cannon.y - camera_y) * TILE_HEIGHT) + int(TILE_HEIGHT / 2) - int(image.get_height() / 2)))

        # informational text
        if game.started:
            # draw shadow HEALTH text
            health_text = 'HEALTH: {} / {}'.format(game.player.energy, game.player.max_energy)
            (width, height) = game.regular_font.size(health_text)
            text = game.regular_font.render(health_text, False, (255, 255, 255))
            screen.blit(text, (15, 15))

            # draw normal HEALTH text
            text = game.regular_font.render(health_text, False, (0, 0, 0))
            screen.blit(text, (15 + 1, 15 + 1))

            # draw shadow SCORE text
            score_text = 'Score: {}'.format(game.player.score)
            (width, height) = game.regular_font.size(score_text)
            text = game.regular_font.render(score_text, False, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH - width - 15, 15))

            # draw normal SCORE text
            text = game.regular_font.render(score_text, False, (0, 0, 0))
            screen.blit(text, (SCREEN_WIDTH - width - 15 + 1, 15 + 1))

        # draw text saying that player lost the game
        if game.player.has_lost():
            title = 'GAME OVER'
            (width, height) = game.title_font.size(title)

            # draw shadown GAME OVER text
            text = game.title_font.render(title, False, (0, 0, 0))
            screen.blit(text, (int(SCREEN_WIDTH) / 2 - int(width / 2) + 1, int(SCREEN_HEIGHT / 2) - int(height / 2) + 1))

            # draw normal GAME OVER text
            text = game.title_font.render(title, False, (255, 255, 255))
            screen.blit(text, (int(SCREEN_WIDTH) / 2 - int(width / 2), int(SCREEN_HEIGHT / 2) - int(height / 2)))

            # lower the sound to make everything more sad to the player
            if pygame.mixer.music.get_volume() >= 0.1:
                pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() - 0.02)

        if not game.started:
            title = 'Pirate Flow'
            (width, height) = game.title_font.size(title)

            # draw shadow PIRATE FLOW text
            text = game.title_font.render(title, False, (0, 0, 0))
            screen.blit(text, (int(SCREEN_WIDTH) / 2 - int(width / 2) + 1, int(SCREEN_HEIGHT / 2) - int(height / 2) + 1))

            # draw normal PIRATE FLOW text
            text = game.title_font.render(title, False, (255, 255, 255))
            screen.blit(text, (int(SCREEN_WIDTH) / 2 - int(width / 2), int(SCREEN_HEIGHT / 2) - int(height / 2)))

            # draw shadow PRESS SPACE text
            text = game.regular_font.render('Press SPACE to start the game'.format(game.player.energy, game.player.max_energy), False, (0, 0, 0))
            screen.blit(text, (int(SCREEN_WIDTH) / 2 - int(width / 2) + 1, int(SCREEN_HEIGHT / 2) + int(height / 2) + 1))

            # draw normal PRESS SPACE text
            text = game.regular_font.render('Press SPACE to start the game'.format(game.player.energy, game.player.max_energy), False, (255, 255, 255))
            screen.blit(text, (int(SCREEN_WIDTH) / 2 - int(width / 2), int(SCREEN_HEIGHT / 2) + int(height / 2)))
        else:
            # add some background music volume when game has started
            if pygame.mixer.music.get_volume() < 0.4:
                pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() + 0.01)

        # render and limit fps to 50
        pygame.display.flip()
        game.tick()

        # handle keypresses/gameplay
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                playing = False
            elif event.type == pygame.locals.KEYDOWN:
                if game.player.is_alive:
                    if game.started:
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
                    else:
                        if event.key == pygame.K_SPACE:
                            game.started = True

