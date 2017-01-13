import pygame as py
from random import randint


class Tile:

    def __init__(self, loc):
        self.loc = loc
        self.rect = py.Rect((loc[0]*8, loc[1]*8), (8, 8))
        self.state = "unclicked"
        self.gupdate = True
        self.value = 0
        self.is_bomb = False

        self.previous_state = ""

    def bombify(self):
        self.is_bomb = True

    def flag(self):
        if self.state == "flag":
            self.state = self.previous_state
            if self.is_bomb:
                return -1
            else:
                return 0
        else:
            self.previous_state = self.state
            self.state = "flag"

            if self.is_bomb:
                return 1
            else:
                return 0

    def reveal(self):
        if not self.is_bomb:
            if self.state != "x":
                self.state = str(self.value)
        else:
            self.state = "bomb"
        self.gupdate = True


class Minesweeper:

    def __init__(self):
        self.screen = py.display.set_mode((640, 576))
        self.surface = py.Surface((160, 144))

        py.display.set_caption("Minesweeper | Created By Isaac Ballone | 1/13/2017",
                               "Minesweeper")

        self.sprite_sheet = py.image.load("sprite.png").convert()
        cursor = py.Surface((16, 20))
        cursor.set_colorkey((144, 136, 192))
        cursor.blit(py.transform.scale2x(self._get_sprite((164, 2), (8, 10))), (0, 0))
        self.sprites = {"frame": self._get_sprite((2, 2), (160, 144)), "unclicked": self._get_sprite((164, 49), (8, 8)),
                        "clicked": self._get_sprite((174, 49), (8, 8)), "0": self._get_sprite((174, 49), (8, 8)),
                        "1": self._get_sprite((184, 49), (8, 8)),
                        "2": self._get_sprite((194, 49), (8, 8)), "3": self._get_sprite((204, 49), (8, 8)),
                        "4": self._get_sprite((214, 49), (8, 8)), "unarmed": self._get_sprite((254, 49), (8, 8)),
                        "5": self._get_sprite((164, 59), (8, 8)), "6": self._get_sprite((174, 59), (8, 8)),
                        "7": self._get_sprite((184, 59), (8, 8)), "8": self._get_sprite((194, 59), (8, 8)),
                        "flag": self._get_sprite((224, 49), (8, 8)), "cursor": cursor,
                        "smile": self._get_sprite((164, 29), (18, 19)), "shock": self._get_sprite((184, 29), (18, 18)),
                        "cool": self._get_sprite((224, 29), (18, 18)),
                        "n0": self._get_sprite((164, 14), (11, 13)), "n1": self._get_sprite((177, 14), (2, 13)),
                        "n2": self._get_sprite((181, 14), (11, 13)), "n3": self._get_sprite((195, 14), (10, 13)),
                        "n4": self._get_sprite((207, 14), (11, 13)), "n5": self._get_sprite((220, 14), (11, 13)),
                        "n6": self._get_sprite((233, 14), (11, 13)), "n7": self._get_sprite((246, 14), (10, 13)),
                        "n8": self._get_sprite((258, 14), (11, 13)), "n9": self._get_sprite((271, 14), (11, 13)),
                        "bomb": self._get_sprite((264, 49), (8, 8)), "x": self._get_sprite((244, 49), (8, 8)),
                        "dead": self._get_sprite((204, 29), (18, 18))}

        icon = py.image.load("icon.png").convert_alpha()
        icon = py.transform.scale(icon, (28, 28))
        py.display.set_icon(icon)

        py.mouse.set_visible(False)

        self.tiles = []
        for x in range(0, 18):
            row = []
            for y in range(0, 11):
                row.append(Tile((x, y)))
            self.tiles.append(row)

        self.total_bombs = 0
        self.discovered_bombs = 0
        self.flags = 0
        self.time = 0
        self.SECOND = py.USEREVENT+1
        py.time.set_timer(self.SECOND, 1000)

        i = randint(15, 20)
        while i != 0:
            x, y = randint(0, 17), randint(0, 10)
            self.tiles[x][y].bombify()
            i -= 1

        for row in self.tiles:
            for tile in row:
                if tile.is_bomb:
                    for x in range(tile.loc[0]-1, tile.loc[0]+2):
                        for y in range(tile.loc[1]-1, tile.loc[1]+2):
                            if tile.loc != (x, y):
                                if not x > 17 and not y > 10:
                                    if not x < 0 and not y < 0:
                                        self.tiles[x][y].value += 1
                    self.total_bombs += 1
        self.flags = self.total_bombs
        self.face_state = "smile"
        self.face_rect = py.Rect((71, 15), (16, 16))

        self.app = True
        self.won = None
        self.loop()

    def loop(self):
        self.surface.blit(self.sprites["frame"], (0, 0))

        while self.app:
            self.input()
            self.update()
            self.draw()

    def input(self):
        for event in py.event.get():
            if event.type == py.QUIT:
                self.app = False
            if event.type == py.MOUSEBUTTONDOWN or event.type == py.MOUSEBUTTONUP:
                self.click(event)
            if event.type == self.SECOND:
                if self.won == None:
                    self.time += 1

    def update(self):
        if self.total_bombs == self.discovered_bombs and self.flags == 0:
                self.won = True
                self.end_game()
        elif not self.won == None:
            self.end_game()
        if self.won:
            if not self.face_state == "reset":
                self.face_state = "cool"
        elif self.won == False:
            if not self.face_state == "reset":
                self.face_state = "dead"

    def end_game(self):
        for row in self.tiles:
            for tile in row:
                if tile.state == "flag":
                    if tile.is_bomb:
                        tile.state = "unarmed"
                    else:
                        tile.state = "x"
                if tile.state == "unclicked":
                    if tile.is_bomb:
                        tile.state = "bomb"

    def draw(self):
        flags = 0
        for row in self.tiles:
            for tile in row:
                if tile.gupdate:
                    self.surface.blit(self.sprites[tile.state], (tile.rect.x+8, tile.rect.y+48))
                if tile.state == "flag":
                    flags += 1
        self.flags = self.total_bombs - flags

        if self.face_state != "reset":
            self.surface.blit(self.sprites[self.face_state], self.face_rect)
        else:
            self.surface.blit(self.sprites["shock"], self.face_rect)
        self.scoreboard()

        self.screen.blit(py.transform.scale(self.surface, (640, 576)), (0, 0))
        self.screen.blit(self.sprites["cursor"], py.mouse.get_pos())
        py.display.update()

    def scoreboard(self):
        if self.flags < 0:
            str_flag = str(0)
        else:
            str_flag = str(self.flags)

        flag_surf = py.Surface((48, 16))
        flag_surf.set_colorkey((144, 136, 192))
        flag_surf.fill((0, 0, 0))
        self.surface.blit(flag_surf, (16, 16))

        i = len(str_flag) - 1
        f = 2
        while i != -1:
            flag_surf.blit(self.sprites["n"+str_flag[i]], (48-self.sprites["n"+str_flag[i]].get_size()[0] - f, 2))
            f += self.sprites["n"+str_flag[i]].get_size()[0] + 2
            i -= 1

        self.surface.blit(flag_surf, (16, 16))

        str_time = str(self.time)

        surf = py.Surface((48, 16))
        surf.set_colorkey((144, 136, 192))
        surf.fill((0, 0, 0))
        self.surface.blit(surf, (96, 16))

        i = len(str_time) - 1
        f = 2
        while i != -1:
            surf.blit(self.sprites["n" + str_time[i]], (48 - self.sprites["n" + str_time[i]].get_size()[0] - f, 2))
            f += self.sprites["n" + str_time[i]].get_size()[0] + 2
            i -= 1

        self.surface.blit(surf, (96, 16))

    def click(self, event):
        mouse_pos = py.mouse.get_pos()
        mouse_pos = (mouse_pos[0]/4-8, mouse_pos[1]/4-48)

        if event.type == py.MOUSEBUTTONDOWN:

            if self.won == None:
                if event.button == 1:  # Right click
                    self.face_state = "shock"
                    for row in self.tiles:
                        for tile in row:
                            if tile.rect.collidepoint(mouse_pos):
                                if tile.state != "flag":
                                    tile.state = "clicked"
                                    tile.gupdate = True
                                    if tile.is_bomb:
                                        self.won = False
            if self.face_rect.collidepoint(py.mouse.get_pos()[0]/4, py.mouse.get_pos()[1]/4):
                self.face_state = "reset"
                self.face_rect.y += 1

            if self.won == None:
                if event.button == 3:
                    for row in self.tiles:
                        for tile in row:
                            if tile.rect.collidepoint(mouse_pos):
                                self.discovered_bombs += tile.flag()

        if event.type == py.MOUSEBUTTONUP:
            if self.face_state == "reset":
                self.face_rect.y -= 1
                self.reset()
            self.face_state = "smile"
            if event.button == 1:  # Right click
                for row in self.tiles:
                    for tile in row:
                        if tile.state == "clicked":
                            tile.reveal()
                            if tile.value == 0:
                                self.reveal_blanks(tile.loc)

    def reveal_blanks(self, loc):
        for x in range(loc[0]-1, loc[0]+2):
            for y in range(loc[1]-1, loc[1]+2):
                if loc != (x, y):
                    if not x > 17 and not y > 10:
                        if not x < 0 and not y < 0:
                            if not self.tiles[x][y].is_bomb:
                                if self.tiles[x][y].value == 0:
                                    if self.tiles[x][y].state == "unclicked":
                                        self.tiles[x][y].reveal()
                                        self.reveal_blanks((x, y))
                                else:
                                    self.tiles[x][y].reveal()

    def _get_sprite(self, loc, size):
        surface = py.Surface(size)
        surface.blit(self.sprite_sheet, (-loc[0], -loc[1]))

        return surface

    def reset(self):
        self.tiles = []
        for x in range(0, 18):
            row = []
            for y in range(0, 11):
                row.append(Tile((x, y)))
            self.tiles.append(row)

        self.total_bombs = 0
        self.discovered_bombs = 0
        self.flags = 0
        self.time = 0

        i = randint(15, 20)
        while i != 0:
            x, y = randint(0, 17), randint(0, 10)
            self.tiles[x][y].bombify()
            i -= 1

        for row in self.tiles:
            for tile in row:
                if tile.is_bomb:
                    for x in range(tile.loc[0] - 1, tile.loc[0] + 2):
                        for y in range(tile.loc[1] - 1, tile.loc[1] + 2):
                            if tile.loc != (x, y):
                                if not x > 17 and not y > 10:
                                    if not x < 0 and not y < 0:
                                        self.tiles[x][y].value += 1
                    self.total_bombs += 1
        self.flags = self.total_bombs

        self.won = None


ms = Minesweeper()



