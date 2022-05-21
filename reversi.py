from email.mime import base
from itertools import product
from textwrap import indent
from time import sleep
import pygame
from collections import namedtuple
import random

Position = namedtuple("Position", ["x", "y"])

BLOCKSIZE = 100
SCREENSIZE = Position(1600, 900) # constants
SIDE = 8
PLAYERCOLOR = (255, 255, 255)
BOTCOLOR = (0, 0, 0)
DESKCOLOR = (40, 255, 80)

screen = pygame.display.set_mode(SCREENSIZE) # variables
game_on = True
t = 0 # is for turns
buttons = pygame.sprite.Group()

x_offset = (SCREENSIZE.x - BLOCKSIZE * 8) / 2
y_offset = (SCREENSIZE.y - BLOCKSIZE * 8) / 2

class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, func):
        super().__init__()
        self.pos = Position(x, y)
        self.size = (width, height)
        self.color = color
        self.func = func
        self.image = pygame.Surface(self.size)
        self.image.fill(self.color)
        self.rect = self.image.get_rect(topleft = self.pos)

    def check_pressed(self):
        x, y = pygame.mouse.get_pos()
        if x > self.pos.x and x < self.pos.x + self.size[0]:
            if y > self.pos.y and y < self.pos.x + self.size[1]:
                self.func()
                return True

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.pos = Position(x, y)
        self.size = size
        self.color = (40, 255, 80)
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(topleft=(self.pos))

    def update(self, screen):
        self.draw(screen)

    def change_color(self, color):
        self.color = color
        self.image.fill(self.color)

    def draw(self, screen: pygame.Surface):
        self.image.fill(self.color)
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (20, 140, 20), self.rect, 2, 0, 0, 0, 0, 0) # drawing borders change borders color here!

class Desk: # list of tiles also its doing all operations with them
    def __init__(self): # doing SIDE x SIDE desk filled with tiles
        self.tiles = []
        for i in range(SIDE):
            rowed_tiles = []
            for k in range(SIDE):
                tile = Tile(x_offset + BLOCKSIZE * i, y_offset + BLOCKSIZE * k, BLOCKSIZE)
                rowed_tiles.append(tile)
            self.tiles.append(rowed_tiles)
        self.tiles[3][3].color = BOTCOLOR
        self.tiles[3][4].color = PLAYERCOLOR
        self.tiles[4][3].color = PLAYERCOLOR
        self.tiles[4][4].color = BOTCOLOR

    def update_tiles(self, screen: pygame.Surface):
        for i in range(SIDE):
            for k in range(SIDE):
                self.tiles[i][k].update(screen)

    def move(self, indexes, color, steps, change_color): # going through one line of blocks
        step_x, step_y = steps
        on_axis = []
        while self.in_range(indexes[0]+step_x) and self.in_range(indexes[1]+step_y):
            ind_x = int(indexes[0] + step_x)
            ind_y = int(indexes[1] + step_y)

            if self.tiles[ind_x][ind_y].color == DESKCOLOR or self.tiles[ind_x][ind_y].color == color and len(on_axis) == 0:
                return False

            elif self.tiles[ind_x][ind_y].color == color: 
                if change_color:
                    for tile in on_axis:
                        tile.color = color
                return True

            else:
                if color != self.tiles[ind_x][ind_y]:
                    on_axis.append(self.tiles[ind_x][ind_y])
                step_x += steps[0]
                step_y += steps[1]
        return False

    def in_range(self, ind): # checking is index in range of list
        return ind < SIDE and ind >=0

    def on_click(self, tiles: list): # changing color of clicked tile(big fuck up)
        x, y = pygame.mouse.get_pos()
        good_choice = False
        for i, k in product(range(SIDE), range(SIDE)):

            if not self.tiles[i][k].rect.collidepoint(x, y) or not self.tiles[i][k].color == DESKCOLOR:
                continue
                
            for j, l in product((-1, 0, 1), (-1, 0, 1)):

                if j == 0 and l == 0:
                    continue

                if self.move((i, k), PLAYERCOLOR, (j, l), False):
                    good_choice = True

            if good_choice:
                self.tiles[i][k].change_color(PLAYERCOLOR)
                print(i, k)
                return i, k

    def render_desk(self, ind, color): # checking and changing tiles color when necessary
        ind_x, ind_y = ind

        if ind_x == None:
            return

        for i, k in product((-1, 0, 1), (-1, 0, 1)):
            if i == 0 and k == 0:
                continue
            self.move((ind_x, ind_y), color, (i, k), True)


    def bot_move(self, tiles: Tile):
        global BOTCOLOR
        s = SIDE - 1
        possible_moves = [] # all moves are indices (x, y)
        bad_possible_moves = [] 
        good_moves = [(0, 0), (s, 0), (s, s), (0, s)]

        bad_moves = [(0, 1), (1, 1), (1, 0),
                     (0, s - 1), (1, s - 1), (1, s),
                     (0, s - 1), (1, s - 1), (1, s),
                     (s, s - 1), (s - 1, s - 1), (s, s - 1)]

        for i, j in product(range(SIDE), range(SIDE)):
            possible = False

            if tiles[i][j].color == PLAYERCOLOR or tiles[i][j].color == BOTCOLOR:
                continue
            
            for k, l in product((-1, 0, 1), (-1, 0, 1)):
                
                if k == 0 and l == 0:
                    continue
                
                if self.move((i, j), BOTCOLOR, (k, l), False):
                    print("ind : ", i, j,"step :", k,l)
                    possible = True
            
            # print(possible)
            
            if possible:
                possible_moves.append((i, j))

        for move in possible_moves:
            
            for good_move in good_moves:
                if move == good_move:
                    return Position(move[0], move[1])

            def is_bad(move):
                for bad_move in bad_moves:
                    if bad_move == move:
                        return True
                return False

            if is_bad(move):
                    possible_moves.remove(move)
                    bad_possible_moves.append(move)
            else:
                return Position(move[0], move[1])

        random_move = bad_possible_moves[random.randint(len(possible_moves))]
        return Position(random_move[0], random_move[1])

def game_over():
    player_points = 0
    bot_points = 0
    for i in range(SIDE):
        for k in range(SIDE):
            if desk.tiles[i][k].color == DESKCOLOR:
                return False
            elif desk.tiles[i][k].color == PLAYERCOLOR:
                player_points += 1
            elif desk.tiles[i][k].color == BOTCOLOR:
                bot_points += 1
    print("bot points: ",bot_points, "player points: ", player_points)


def pass_move():
    pass

def restart():
    for i in range(SIDE):
        for k in range(SIDE):
            desk.tiles[i][k].color = DESKCOLOR
    desk.tiles[3][3].color = BOTCOLOR
    desk.tiles[3][4].color = PLAYERCOLOR
    desk.tiles[4][3].color = PLAYERCOLOR
    desk.tiles[4][4].color = BOTCOLOR

desk = Desk()
pass_btn = Button(1400, 100, 100, 100, (105, 130, 57), pass_move)
restart_btn = Button(1400, 300, 100, 100, (199, 46, 110), restart)
buttons.add(pass_btn, restart_btn)

while game_on:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_on = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if restart_btn.check_pressed():
                break
            is_passed = pass_btn.check_pressed()
            if is_passed:
                sleep(1)
                ind = desk.bot_move(desk.tiles)
                if ind != None:
                    desk.tiles[ind.x][ind.y].color = BOTCOLOR
                    desk.render_desk(ind , BOTCOLOR)
                    break
            ind = desk.on_click(desk.tiles)
            if ind:
                desk.render_desk(ind , PLAYERCOLOR)
                desk.update_tiles(screen)
                pygame.display.flip()
                pygame.time.wait(1000)
                ind = desk.bot_move(desk.tiles)
                if ind != None:
                    desk.tiles[ind.x][ind.y].color = BOTCOLOR
                    desk.render_desk(ind, BOTCOLOR)
                game_over()

    screen.fill((0, 0, 0))
    buttons.draw(screen)
    desk.update_tiles(screen)
    pygame.display.flip() # while doing +1 or -1 we are just moving to the next column
