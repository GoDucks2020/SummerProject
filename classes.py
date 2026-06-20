import pygame
import threading as th
from time import *
from math import *

pygame.init()

info = pygame.display.Info()

SCREEN_WIDTH = info.current_w / 1.5
SCREEN_HEIGHT = info.current_h / 1.5

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
pygame.display.set_caption('Enemies')

cameraY = 0
cameraX = 0
grav = 0
tick = 0
bframe = 0
pshoot = True

clock = pygame.time.Clock()
FPS = 60

grassImage = pygame.image.load('/Users/levikerr/PycharmProjects/PythonProject3/.venv/pixilart-drawing-9.png')
bowSpriteSheet = pygame.image.load('/Users/levikerr/PycharmProjects/Final/.venv/sprite_sheet.png').convert_alpha()
arrowImage = pygame.image.load('/Users/levikerr/PycharmProjects/Final/.venv/pixil-frame-0 (5).png').convert_alpha()

def getImage(sheet, xframe, yframe, width, height, scale, color):
    image = pygame.Surface((width, height)).convert_alpha()
    image.blit(sheet, (0, 0), ((xframe * width), (yframe * height), width, height))
    image = pygame.transform.scale(image, (width * scale, height * scale))
    image.set_colorkey(color)
    return image

arrowSprite = getImage(arrowImage, 0, 0, 20, 5, 2, (0, 0, 0))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((20, 20))
        self.rect = self.image.get_rect()
        self.image.fill(color)
        self.x = x
        self.y = y
        self.bx = 0
        self.by = 0
        self.intx = self.x
        self.inty = self.y - y
        self.health = 6
        self.healthBar = HealthBar(self, self.health)
        enemyHealth.add(self.healthBar)

    def update(self):
        if self.rect.x < player.rect.x:
            self.x += 5
        elif self.rect.x - 5 > player.rect.x:
            self.x -= 5
        self.bx = self.intx + cameraX + self.x
        self.by = self.inty + cameraY + self.y
        self.rect.x = self.bx
        self.rect.y = self.by
        if self.health <= 0:
            self.kill()


class HealthBar(pygame.sprite.Sprite):
    def __init__(self, enemy, intHealth):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, 10))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.enemy = enemy
        self.rect.x = enemy.rect.x - enemy.rect.width / 2
        self.rect.y = enemy.rect.y - 20
        self.intHealth = intHealth
        self.healthy = Health(self, self.enemy)
        HEALTH.add(self.healthy)

    def update(self):
        if self.enemy.health <= 0:
            self.kill()
        self.rect.x = self.enemy.rect.x - self.enemy.rect.width / 2
        self.rect.y = self.enemy.rect.y - 20


class Health(pygame.sprite.Sprite):
    def __init__(self, healthBar, enemy):
        pygame.sprite.Sprite.__init__(self)
        self.healthBar = healthBar
        self.enemy = enemy
        self.image = pygame.Surface((36, 6))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()

    def update(self):
        if self.enemy.health <= 0:
            self.kill()
        try:
            self.image = pygame.Surface((self.enemy.health * 6, 6))
            self.image.fill((255, 0, 0))
        except:
            pass
        self.rect.x = self.healthBar.rect.x + 2
        self.rect.centery = self.healthBar.rect.centery
        pass



class Projectile(pygame.sprite.Sprite):
    def __init__(self, intx, inty, mouseX, mouseY, sped, damage):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface((10, 10))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT / 2
        self.rect.x = self.x
        self.rect.y = self.y
        self.intx = intx
        self.inty = inty
        self.mouseX = mouseX
        self.mouseY = mouseY
        self.sped = sped
        self.angle = atan2(self.mouseY - self.y, self.mouseX - self.x)
        self. damage = damage

    def update(self, player):
        self.x += cos(self.angle) * self.sped
        self.y += sin(self.angle) * self.sped
        self.rect.x = self.x + cameraX - self.intx
        self.rect.y = self.y + cameraY - self.inty
        rotatedArrow = pygame.transform.rotate(arrowSprite.convert_alpha(), (((atan2(
        self.mouseY + (sin(pi) * atan2(player.rect.x * 12.5, player.rect.y - 19)) - player.rect.y
            - player.rect.height / 2, self.mouseX + (sin(pi) * atan2(player.rect.x * 12.5, player.rect.y - 19)) -
                    player.rect.x - player.rect.width / 2 - (sin(pi) * atan2(player.rect.x * 12.5, player.rect.y -
                19)))- 2 * pi + (sin(pi) * atan2(player.rect.x * 12.5, player.rect.y - 19))) * -1) * 180 / pi))
        screen.blit(rotatedArrow, (self.rect.x - ((rotatedArrow.get_width() - 5) / 2) - sin(
            atan2(self.mouseX - player.rect.x - player.rect.width / 2, self.mouseY - player.rect.y -
                  player.rect.height / 2)) * 12 - (sin(pi) * atan2(player.rect.x * 12.5, player.rect.y - 19)),
        self.rect.y - ((rotatedArrow.get_height() - 5) / 2 + (sin(pi) * atan2(player.rect.x *
                12.5, player.rect.y - 19))) - cos(atan2(self.mouseX - player.rect.x - player.rect.width / 2,
                          self.mouseY - player.rect.y - player.rect.height / 2)) * 12))


class Map(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.x: int = 0
        self.y: int = 0
        self.tileSize = 30
        self.grid = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                     [0,0,0,0,0,0,0,0,0,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
                     [0,0,0,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,0,0,0],
                     [1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1],
                     [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
                     [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]]
        self.tiles = pygame.sprite.Group()

    def render(self):
        for row in range(len(self.grid)):
            for column in range(len(self.grid[0])):
                self.x = column * self.tileSize + 5
                self.y = row * self.tileSize + 600
                if self.grid[row][column] == 1:
                    self.tiles.add(Tile(self.x, self.y, self.tileSize, self.tileSize, (100, 100, 200), 1, self.tileSize))
                elif self.grid[row][column] == 2:
                    self.tiles.add(Tile(self.x, self.y, self.tileSize, self.tileSize, (200, 100, 100), 2, self.tileSize))

class Tile(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, width: int, height: int, col: tuple[int,int,int]|str, Type: int, tileSize: int) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height))
        self.image.fill(col)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.intX = x
        self.intY = y
        self.type = Type
        self.tileSize = tileSize
        if self.type == 1:
            self.image = getImage(grassImage, 0, 0, self.tileSize, self.tileSize, 1, (0, 0, 0))
        elif self.type == 2:
            self.image = getImage(grassImage, 0, 1, self.tileSize, self.tileSize, 1, (0, 0, 0))


    def update(self) -> None:
        self.x = self.intX + cameraX
        self.y = self.intY + cameraY
        screen.blit(self.image, (self.x, self.y))
        self.rect.x = self.x
        self.rect.y = self.y


class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface((30, 30))
        self.image.fill((100, 100, 255))
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x
        self.x = x
        self.y = y

