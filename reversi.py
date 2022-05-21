from itertools import product
from time import sleep
import pygame
from collections import namedtuple
import random

pygame.init()

Position = namedtuple("Position", ["x", "y"])

BLOCKSIZE = 100
SCREENSIZE = Position(1600, 900) # constants
SIDE = 8
PLAYERCOLOR = (255, 255, 255)
BOTCOLOR = (0, 0, 0)
DESKCOLOR = (40, 255, 80)

font = pygame.font.Font('freesansbold.ttf', 32)
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

    def move(self, indexes, color, steps, change_color, num_of_tiles): # going through one line of blocks
        step_x, step_y = steps
        on_axis = []
        while self.in_range(indexes[0]+step_x) and self.in_range(indexes[1]+step_y):
            ind_x = int(indexes[0] + step_x)
            ind_y = int(indexes[1] + step_y)

            if self.tiles[ind_x][ind_y].color == DESKCOLOR or self.tiles[ind_x][ind_y].color == color and len(on_axis) == 0:
                if num_of_tiles:
                    return False, 0
                return False

            elif self.tiles[ind_x][ind_y].color == color: 
                if change_color:
                    for tile in on_axis:
                        tile.color = color
                if num_of_tiles:
                    return True, len(on_axis)
                return True

            else:
                if color != self.tiles[ind_x][ind_y]:
                    on_axis.append(self.tiles[ind_x][ind_y])
                step_x += steps[0]
                step_y += steps[1]
        if num_of_tiles:
            return False, 0
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

                if self.move((i, k), PLAYERCOLOR, (j, l), False, False):
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
            self.move((ind_x, ind_y), color, (i, k), True, False)


    def bot_move(self, tiles: Tile):
        global BOTCOLOR
        move = namedtuple("move", ["indices", "tiles"])
        s = SIDE - 1
        possible_moves = [] # all moves are indices (x, y)
        bad_possible_moves = []
        to_remove = []
        possible_nice_moves = []
        good_moves = [(0, 0), (s, 0), (s, s), (0, s)]

        bad_moves = [(0, 1), (1, 1), (1, 0),
                     (s - 1, 0), (s - 1, 1), (s, 1),
                     (0, s - 1), (1, s - 1), (1, s),
                     (s - 1, s), (s - 1, s - 1), (s, s - 1)]
                    
        nice_moves = [(s - 2, 0), (s - 3, 0), (s - 4, 0), (s - 5, 0),
                      (s - 2, s), (s - 3, s), (s - 4, s), (s - 5, s),
                      (0, s - 2), (0, s - 3), (0, s - 4), (0, s - 5),
                      (s, s - 2), (s, s - 3), (s, s - 4), (s, s - 5)]

        for i, j in product(range(SIDE), range(SIDE)):
            possible = False
            used_tiles = 0

            if tiles[i][j].color == PLAYERCOLOR or tiles[i][j].color == BOTCOLOR:
                continue
            
            for k, l in product((-1, 0, 1), (-1, 0, 1)):
                
                if k == 0 and l == 0:
                    continue
                
                is_possible, tiless = self.move((i, j), BOTCOLOR, (k, l), False, True)
                used_tiles += tiless
                if is_possible:
                    possible = True

            if possible:
                possible_moves.append(move(Position(i, j), used_tiles))

        for move in possible_moves:
            
            for good_move in good_moves:
                if move.indices == good_move:
                    return Position(move.indices[0], move.indices[1])

            def is_bad(move, moves):
                for bad_move in moves: 
                    if bad_move == move.indices:
                        return True
                return False

            if is_bad(move, bad_moves):
                to_remove.append(move)
                bad_possible_moves.append(move)

            if is_bad(move, nice_moves):
                to_remove.append(move)
                possible_nice_moves.append(move)

        for move in to_remove:
            possible_moves.remove(move)
        
        nice_m = len(possible_nice_moves)
        moves = len(possible_moves)
        bmoves = len(bad_possible_moves)

        print("nice_moves:", possible_nice_moves)
        print("possible_moves: ", possible_moves)
        print("bad moves: ", bad_possible_moves)

        def most_captured(list):
            move = namedtuple("move", ["indices", "tiles"])
            max_tiles = move(Position(-1, -1), -1)
            for move in list:
                if move.tiles > max_tiles.tiles:
                    max_tiles = move
            return max_tiles
            

        if nice_m != 0:
            the_move = most_captured(possible_nice_moves)
            return Position(the_move.indices[0], the_move.indices[1])

        elif moves != 0:
            the_move = most_captured(possible_moves)
            return Position(the_move.indices[0], the_move.indices[1])

        elif bmoves != 0:
            the_move = most_captured(bad_possible_moves)
            return Position(the_move.indices[0], the_move.indices[1])
        else:
            return None

def game_over():
    player_points = 0
    bot_points = 0
    for i, k in product(range(SIDE), range(SIDE)):
        if desk.tiles[i][k].color == PLAYERCOLOR:
            player_points += 1
        elif desk.tiles[i][k].color == BOTCOLOR:
            bot_points += 1
    return bot_points, player_points
    


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

    screen.fill((0, 0, 0))
    buttons.draw(screen)

    bot_points, player_points = game_over()
    player_surf = font.render(f"player_points: {player_points}", True, (200, 100, 100), None)
    bot_surf = font.render(f"bot points: {bot_points}", True, (200, 100, 100), None)
    screen.blit(player_surf, (1250, 500))
    screen.blit(bot_surf, (1250, 600))

    desk.update_tiles(screen)
    pygame.display.flip() # while doing +1 or -1 we are just moving to the next column
