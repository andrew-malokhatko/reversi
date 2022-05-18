import pygame
from collections import namedtuple

Position = namedtuple("Position", ["x", "y"])

BLOCKSIZE = 100
SCREENSIZE = Position(1600, 900)  # constants
SIDE = 8
PLAYERCOLOR = (255, 255, 255)
BOTCOLOR = (0, 0, 0)
DESKCOLOR = (40, 255, 80)

screen = pygame.display.set_mode(SCREENSIZE) #variables
game_on = True
t = 0 # is for turns

x_offset = (SCREENSIZE.x - BLOCKSIZE * 8) / 2
y_offset = (SCREENSIZE.y - BLOCKSIZE * 8) / 2

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

    def on_click(self): # changing color of clicked tile
        global t
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x, y) and self.color == DESKCOLOR:
            self.color = PLAYERCOLOR if t % 2 == 1 else BOTCOLOR
            self.image.fill(self.color)
            t += 1
            return self.pos

    def draw(self, screen: pygame.Surface):
        self.image.fill(self.color)
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (20, 140, 20), self.rect, 2, 0, 0, 0, 0, 0) # drawing borders change borders color here!

class Desk: # list of tiles also its doing all operations with them
    def __init__(self): # doing SIDE x SIDE desk filled with tiles
        self.tiles = []
        for i in range(SIDE):
            for k in range(SIDE):
                tile = Tile(x_offset + BLOCKSIZE * i, y_offset + BLOCKSIZE * k, BLOCKSIZE)
                self.tiles.append(tile)

    def update_tiles(self, screen : pygame.Surface):
        for tile in self.tiles:
            tile.update(screen)

    def render_desk(self, x, y): # checking and changing tiles color when necessary

        def in_range(ind): # checking is index in range of list
            return ind >= 0 and ind < SIDE * SIDE

        def to_index(x, y): # gets index by position
            for tile in self.tiles:
                if tile.pos.x == x and tile.pos.y == y:
                    return self.tiles.index(tile)
            return None

        def move(ind, color, step): # going through one line of blocks
            i = step
            on_axis = []
            while in_range(ind + i):
                if self.tiles[ind + i].color == DESKCOLOR: 
                    break
                elif self.tiles[ind + i].color == color: 
                    for tile in on_axis:
                        tile.color = color
                    break
                else:
                    on_axis.append(self.tiles[ind + i])
                    i += step

        ind = to_index(x, y)
        print(ind)

        if ind != None:
            color = self.tiles[ind].color
            move(ind, color, 1) # down
            move(ind, color, -1) # up
            move(ind, color, -8) # left
            move(ind, color, 8) # right
            move(ind, color, -9) # left top
            move(ind, color, 7) # right top
            move(ind, color, 9) # right down
            move(ind, color, -7) # left down
            
desk = Desk()
        
while game_on:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_on = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            for tile in desk.tiles:
                pos = tile.on_click()
                if pos:
                    desk.render_desk(pos.x, pos.y)

    screen.fill((0, 0, 0))
    desk.update_tiles(screen)
    pygame.display.flip()
