from tabnanny import check
from time import sleep
from tkinter import BUTT
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

    def on_click(self, tiles: list): # changing color of clicked tile
        global t

        def move(indexes, color, steps): # going through one line of blocks
            step_x = steps[0]
            step_y = steps[1]
            on_axis = []
            while in_range(step_x + indexes[0]) and in_range(step_y + indexes[1]):
                ind_x = int(indexes[0] + step_x)
                ind_y = int(indexes[1] + step_y)
                if tiles[ind_x][ind_y].color == DESKCOLOR or tiles[ind_x][ind_y].color == PLAYERCOLOR and len(on_axis) == 0:
                    return False
                elif tiles[ind_x][ind_y].color == color and len(on_axis) > 0:
                    return True
                else:
                    if tiles[ind_x][ind_y].color == BOTCOLOR:
                        on_axis.append(tiles[ind_x][ind_y])
                    step_x += steps[0]
                    step_y += steps[1]

        def get_index(): # returns tuple ind(x, y)
            x_ind = (self.pos.x - x_offset) / BLOCKSIZE
            y_ind = (self.pos.y - y_offset) / BLOCKSIZE
            return x_ind, y_ind

        def in_range(ind):
            return ind >= 0 and ind < SIDE

        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x, y) and self.color == DESKCOLOR:
            ind = get_index()
            if move(ind, PLAYERCOLOR, (1, 0)) or move(ind, PLAYERCOLOR, (-1, 0)) or move(ind, PLAYERCOLOR, (0, 1)) or move(ind, PLAYERCOLOR, (0, -1)) or \
               move(ind, PLAYERCOLOR, (1, 1)) or move(ind, PLAYERCOLOR, (-1, 1)) or move(ind, PLAYERCOLOR, (1, -1)) or move(ind, PLAYERCOLOR, (-1, -1)) :
                self.color = PLAYERCOLOR
                self.image.fill(self.color)
                return self.pos

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

    def render_desk(self, x, y, color): # checking and changing tiles color when necessary

        def in_range(ind): # checking is index in range of list
            return ind < SIDE and ind >=0

        def to_index(x, y): # gets index by position
            x_ind = (x - x_offset) / BLOCKSIZE
            y_ind = (y - y_offset) / BLOCKSIZE
            return x_ind, y_ind

        def move(indexes, color, steps): # going through one line of blocks
            step_x = steps[0]
            step_y = steps[1]
            on_axis = []
            while in_range(indexes[0]+step_x) and in_range(indexes[1]+step_y):
                ind_x = int(indexes[0] + step_x)
                ind_y = int(indexes[1] + step_y)
                if self.tiles[ind_x][ind_y].color == DESKCOLOR or self.tiles[ind_x][ind_y].color == color and len(on_axis) == 0:
                    break
                elif self.tiles[ind_x][ind_y].color == color: 
                    for tile in on_axis:
                        tile.color = color
                    break
                else:
                    if color != self.tiles[ind_x][ind_y]:
                        on_axis.append(self.tiles[ind_x][ind_y])
                    step_x += steps[0]
                    step_y += steps[1]

        ind_x, ind_y = to_index(x, y)
        #print(ind)

        if ind_x != None:
            move((ind_x, ind_y), color, (1, 0)) # down
            move((ind_x, ind_y), color, (-1, 0)) # up
            move((ind_x, ind_y), color, (0, -1)) # left
            move((ind_x, ind_y), color, (0, 1)) # right
            move((ind_x, ind_y), color, (-1, -1)) # left top
            move((ind_x, ind_y), color, (1, -1)) # right top
            move((ind_x, ind_y), color, (1, 1)) # right down
            move((ind_x, ind_y), color, (-1, 1)) # left down


def bot_move(tiles: Tile):
    global BOTCOLOR
    c = 0

    def in_range(ind):
            return ind >= 0 and ind < SIDE

    def move(indexes, color, steps): # going through one line of blocks
        step_x = steps[0]
        step_y = steps[1]
        on_axis = []
        while in_range(indexes[0] + step_x) and in_range(indexes[1]+step_y):
            ind_x = int(indexes[0] + step_x)
            ind_y = int(indexes[1] + step_y)
            if tiles[ind_x][ind_y].color == DESKCOLOR or tiles[ind_x][ind_y].color == BOTCOLOR and len(on_axis) == 0:
                return False
            elif tiles[ind_x][ind_y].color == color and len(on_axis) > 0:  #TOFIX
                return True
            else:
                if tiles[ind_x][ind_y].color == PLAYERCOLOR:
                    on_axis.append(tiles[ind_x][ind_y])
                step_x += steps[0]
                step_y += steps[1]
    
    s = set()
    while True:
        pre_len = len(s) 
        ind_x = random.randint(0, SIDE-1)
        ind_y = random.randint(0, SIDE-1)
        to_s = str(ind_x) + str(ind_y)
        s.add(to_s)
        if pre_len == len(s):
            continue
        if len(s) >= 63:
            return None
        ind = (ind_x, ind_y)
        if tiles[ind_x][ind_y].color != PLAYERCOLOR and tiles[ind_x][ind_y].color != BOTCOLOR:
            if move(ind, BOTCOLOR, (1, 0)) or move(ind, BOTCOLOR, (-1, 0)) or move(ind, BOTCOLOR, (0, 1)) or move(ind, BOTCOLOR, (0, -1)) or \
               move(ind, BOTCOLOR, (1, 1)) or move(ind, BOTCOLOR, (-1, 1)) or move(ind, BOTCOLOR, (1, -1)) or move(ind, BOTCOLOR, (-1, -1)) :
                break

    return Position(ind[0], ind[1])




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
    print("asss")

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
                ind = bot_move(desk.tiles)
                if ind != None:
                    desk.tiles[ind.x][ind.y].color = BOTCOLOR
                    desk.render_desk(desk.tiles[ind.x][ind.y].pos.x, desk.tiles[ind.x][ind.y].pos.y, BOTCOLOR)
                    break

            for i in range(SIDE):
                for k in range(SIDE):
                    pos = desk.tiles[i][k].on_click(desk.tiles)
                    if pos:
                        desk.render_desk(pos.x, pos.y, PLAYERCOLOR)
                        desk.update_tiles(screen)
                        pygame.display.flip()
                        sleep(1)
                        ind = bot_move(desk.tiles)
                        if ind != None:
                            desk.tiles[ind.x][ind.y].color = BOTCOLOR
                            desk.render_desk(desk.tiles[ind.x][ind.y].pos.x, desk.tiles[ind.x][ind.y].pos.y, BOTCOLOR)
                        game_over()

    screen.fill((0, 0, 0))
    buttons.draw(screen)
    desk.update_tiles(screen)
    pygame.display.flip() # while doing +1 or -1 we are just moving to the next column
