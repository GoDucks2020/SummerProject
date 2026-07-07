import pygame
import threading as th
from time import sleep
from math import sin, cos, pi, atan2

pygame.init()

info = pygame.display.Info()

SCREEN_WIDTH = info.current_w / 1.5
SCREEN_HEIGHT = info.current_h / 1.5

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
pygame.display.set_caption('Enemies')

key_history = []
cameraY = 0
cameraX = 0
tick = 0
bFrame = 0
pFrame = 0
rTick = 0
iFrame = 0
points = 0
jumpable = True
invulnerable = False

clock = pygame.time.Clock()
FPS = 60

textFont = pygame.font.Font('pressStart.ttf', 20)

grassImage = pygame.image.load('grass.png')
bowSpriteSheet = pygame.image.load('bowSpriteSheet.png').convert_alpha()
arrowImage = pygame.image.load('arrow.png').convert_alpha()
forceImage = pygame.image.load('forceImage.png')


def drawText(text, font, textColor, x, y):
    img = font.render(text, True, textColor)
    screen.blit(img, (x, y))

def getImage(sheet, xframe, yframe, width, height, scale, color):
    image = pygame.Surface((width, height)).convert_alpha()
    image.blit(sheet, (0, 0), ((xframe * width), (yframe * height), width, height))
    image = pygame.transform.scale(image, (width * scale, height * scale))
    image.set_colorkey(color)
    return image

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((20, 20))
        self.group = pygame.sprite.Group()
        self.group.add(self)
        self.rect = self.image.get_rect()
        self.image.fill(color)
        self.x = x
        self.y = y
        self.intx = self.x
        self.inty = self.y - y
        self.bx = 0
        self.by = 0
        self.jx = 0
        self.grav = 0
        self.health = 6
        self.jumpable = False
        self.direction = None
        self.healthBar = HealthBar(self, 6)
        healthBars.add(self.healthBar)

    def update(self):
        global points
        self.y += self.grav
        self.bx = self.intx + cameraX + self.x
        self.by = self.inty + cameraY + self.y
        self.rect.x = self.bx
        self.rect.y = self.by
        for mp in maps:
            while (pygame.sprite.spritecollide(self, mp.nonPhaseableTiles, False) or
                   pygame.sprite.spritecollide(self, mp.barrierTiles, False)):
                self.y -= 1
                self.bx = self.intx + cameraX + self.x
                self.by = self.inty + cameraY + self.y
                self.rect.x = self.bx
                self.rect.y = self.by
                self.grav = 0
                if self.x != self.jx:
                    self.jumpable = True

        if self.rect.x < player.rect.x:
            self.x += 5
            self.direction = 'right'
        elif self.rect.x - 5 > player.rect.x:
            self.x -= 5
            self.direction = 'left'
        self.bx = self.intx + cameraX + self.x
        self.by = self.inty + cameraY + self.y
        self.rect.x = self.bx
        self.rect.y = self.by
        for mp in maps:
            if (pygame.sprite.spritecollide(self, mp.nonPhaseableTiles, False) or
                pygame.sprite.spritecollide(self, mp.barrierTiles, False)):
                while (pygame.sprite.spritecollide(self, mp.nonPhaseableTiles, False) or
                       pygame.sprite.spritecollide(self, mp.barrierTiles, False)):
                    if self.direction == 'right':
                        self.x -= 1
                    else:
                        self.x += 1
                    self.bx = self.intx + cameraX + self.x
                    self.by = self.inty + cameraY + self.y
                    self.rect.x = self.bx
                    self.rect.y = self.by
                if self.jumpable:
                    self.jx = self.x
                    self.grav = -11
                    self.y += self.grav
                    self.bx = self.intx + cameraX + self.x
                    self.by = self.inty + cameraY + self.y
                    self.rect.x = self.bx
                    self.rect.y = self.by
                    self.jumpable = False
        if self.health <= 0:
            self.kill()
            points += 1
        self.grav += 1

class HealthBar(pygame.sprite.Sprite):
    def __init__(self, target, intHealth):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, 10))
        self.health = pygame.Rect(0, 0, 36, 6)
        self.healthInc = 6
        if target == player:
            self.image = pygame.Surface((58, 12))
            self.health = pygame.Rect(0, 0, target.health * 9, 8)
            self.healthInc = 9
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.target = target
        self.intHealth = intHealth
        self.hp = intHealth

    def update(self):
        self.hp = self.target.health
        self.rect.x = self.target.rect.x - self.target.rect.width / 2
        self.rect.y = self.target.rect.y - 20
        self.health.left = self.rect.x + 2
        self.health.centery = self.rect.centery
        self.health.width = self.hp * self.healthInc
        if self.target.health <= 0:
            self.kill()

    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0), self.health)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, intx, inty, mx, my, sped, damage):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface((20, 20))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT / 2
        self.rect.x = self.x
        self.rect.y = self.y
        self.intx = intx
        self.inty = inty
        self.mouseX = mx
        self.mouseY = my
        self.sped = sped
        self.angle = atan2(self.mouseY - self.y, self.mouseX - self.x)
        self.damage = damage

    def update(self):
        self.x += cos(self.angle) * self.sped
        self.y += sin(self.angle) * self.sped
        self.rect.x = self.x + cameraX - self.intx
        self.rect.y = self.y + cameraY - self.inty - 10
        rotatedArrow = pygame.transform.rotate(arrowSprite.convert_alpha(), (((atan2(self.mouseY + (sin(pi) * atan2(player.rect.x * 12.5, player.rect.y - 19)) - player.rect.y - player.rect.height / 2, self.mouseX + (sin(pi) * atan2(player.rect.x * 12.5, player.rect.y - 19)) - player.rect.x - player.rect.width / 2 - (sin(pi) * atan2(player.rect.x * 12.5, player.rect.y - 19))) - 2 * pi + (sin(pi) * atan2(player.rect.x * 12.5, player.rect.y - 19))) * -1) * 180 / pi))
        screen.blit(rotatedArrow, (self.rect.x - ((rotatedArrow.get_width() - 5) / 2) - sin(atan2(self.mouseX - player.rect.x - player.rect.width / 2, self.mouseY - player.rect.y - player.rect.height / 2)) * 12 - (sin(pi) * atan2(player.rect.x * 12.5, player.rect.y - 19)), self.rect.y - ((rotatedArrow.get_height() - 5) / 2 + (sin(pi) * atan2(player.rect.x * 12.5, player.rect.y - 19))) - cos(atan2(self.mouseX - player.rect.x - player.rect.width / 2, self.mouseY - player.rect.y - player.rect.height / 2)) * 12 + 7))

class Map(pygame.sprite.Sprite):
    def __init__(self, x, y, grid):
        pygame.sprite.Sprite.__init__(self)
        self.intx = x
        self.inty = y
        self.x = 0
        self.y = 0
        self.tileSize = 50
        self.grid = grid
        self.nonPhaseableTiles = pygame.sprite.Group()
        self.barrierTiles = pygame.sprite.Group()
        self.phaseableTiles = pygame.sprite.Group()
        maps.append(self)

    def render(self):
        for row in range(len(self.grid)):
            for column in range(len(self.grid[0])):
                self.x = column * self.tileSize + self.intx + 515
                self.y = row * self.tileSize + self.inty - 510
                if self.grid[row][column] == 1:
                    self.nonPhaseableTiles.add(Tile(self.x, self.y, self.tileSize, self.tileSize, (100, 100, 200), 1, self.tileSize))
                elif self.grid[row][column] == 2:
                    self.nonPhaseableTiles.add(Tile(self.x, self.y, self.tileSize, self.tileSize, (200, 100, 100), 2, self.tileSize))
                elif self.grid[row][column] == 3:
                    self.barrierTiles.add(Tile(self.x, self.y, self.tileSize, self.tileSize, (255, 255, 200), 3, self.tileSize))
                elif self.grid[row][column] == 4:
                    self.phaseableTiles.add(Tile(self.x, self.y, self.tileSize, self.tileSize, (171, 117, 83), 4, self.tileSize))

    def update(self):
        self.nonPhaseableTiles.update()
        self.barrierTiles.update()
        self.phaseableTiles.update()

    def draw(self, surface):
        self.nonPhaseableTiles.draw(surface)
        self.barrierTiles.draw(surface)
        self.phaseableTiles.draw(surface)

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, col, Type, tileSize):
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
        elif self.type == 3:
            self.image = getImage(forceImage, pFrame % 3, 0, 16, 16, 1.875, (0, 0, 0))

    def update(self) -> None:
        if self.type == 3:
            self.image = getImage(forceImage, pFrame % 3, 0, 16, 16, 1.875, (0, 0, 0))
        self.x = self.intX + cameraX
        self.y = self.intY + cameraY
        self.rect.x = self.x
        self.rect.y = self.y

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface((30, 30))
        self.image.fill((100, 100, 255))
        self.rect = self.image.get_rect()
        self.direction = None
        self.jumpable = True
        self.sCooldown = False
        self.rect.y = y
        self.rect.x = 615
        self.health = 6
        self.friction = 1.5
        self.grav = 0
        self.sped = 0
        self.x = x
        self.y = y

    def update(self):
        global cameraX
        cameraX += self.sped
        if not -0.5 < player.sped < 0.5:
            player.sped = round(self.sped / self.friction, 3)
        else:
            player.sped = 0

    def shoot(self, sped, damage):
        MouseX = pygame.mouse.get_pos()[0]
        MouseY = pygame.mouse.get_pos()[1]
        if not self.sCooldown:
            self.sCooldown = True
            if MouseX < SCREEN_WIDTH / 2:
                projectiles.add(Projectile(cameraX, cameraY, MouseX, MouseY, sped, damage))
            else:
                projectiles.add(Projectile(cameraX, cameraY, MouseX, MouseY, sped, damage))
            sleep(1)
            self.sCooldown = False

    def jump(self):
        if self.jumpable:
            self.jumpable = False
            sleep(0.02)
            self.grav = -20
            self.jumpable = True

def checkCollisionY() -> bool:
    for mp in maps:
        for t in mp.nonPhaseableTiles:
            if t.type == 1:
                if t.rect.top == player.rect.bottom and player.rect.left - player.rect.width < t.rect.x < player.rect.right:
                    return True
    return False

maps = []

arrowSprite = getImage(arrowImage, 0, 0, 20, 5, 2, (0, 0, 0))

player = Player(SCREEN_WIDTH / 2 - 15, SCREEN_HEIGHT / 2 - 15)
chunk1 = Map(0, 0, [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                               [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
                               [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                               [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]])
chunk2 = Map(1320, 0, [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                               [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                               [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]])

players = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()
healthBars = pygame.sprite.Group()
HEALTH = pygame.sprite.Group()

players.add(player)
# enemies.add(Enemy(250, 580, 'red'))
healthBars.add(HealthBar(player, player.health))

for m in maps:
    m.render()

running = True
while running:
    rTick += 1
    if rTick % 240 == 0 and player.health > 0 and len(list(enemies)) < 3:
        # enemies.add(Enemy(250, 580, 'red'))
        pass
    if iFrame != 0:
        iFrame -= 1
        invulnerable = True
    else:
        invulnerable = False
    if rTick % 6 == 0:
        pFrame += 1

    bow_animations = getImage(bowSpriteSheet, bFrame, 0, 100, 100, 1, (0, 0, 0))

    clock.tick(FPS)
    enemies.update()
    HEALTH.update()
    healthBars.update()
    projectiles.update()

    for m in maps:
        m.draw(screen)
    players.draw(screen)
    enemies.draw(screen)
    HEALTH.draw(screen)
    healthBars.draw(screen)
    for h in healthBars:
        h.draw()

    if player.health <= 0:
        drawText(f"You ended with {points} points!", textFont, 'black', SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 5)

    for enemy in enemies:
        if pygame.sprite.spritecollide(enemy, projectiles, False):
            for projectile in projectiles:
                if pygame.sprite.spritecollide(projectile, enemies, False):
                    projectile.kill()
                    enemy.health -= projectile.damage
                    print('damage:' + str(projectile.damage) + 'health:' + str(enemy.health))
    for m in maps:
        for tile in m.nonPhaseableTiles:
            if pygame.sprite.spritecollide(tile, projectiles, False):
                for proj in projectiles:
                    if (pygame.sprite.spritecollide(proj, m.nonPhaseableTiles, False) or
                        pygame.sprite.spritecollide(proj, m.barrierTiles, False)):
                            proj.kill()
        for tile in m.barrierTiles:
            if pygame.sprite.spritecollide(tile, projectiles, False):
                for proj in projectiles:
                    if (pygame.sprite.spritecollide(proj, m.nonPhaseableTiles, False) or
                        pygame.sprite.spritecollide(proj, m.barrierTiles, False)):
                            proj.kill()
    if pygame.sprite.spritecollide(player, enemies, False) and not invulnerable:
        player.health -= 2
        iFrame = 60

    cameraY -= player.grav
    for m in maps:
        m.update()

    for mp in maps:
        if pygame.sprite.spritecollide(player, mp.nonPhaseableTiles, False):
            while pygame.sprite.spritecollide(player, mp.nonPhaseableTiles, False):
                if player.grav < 0:
                    cameraY -= 1
                else:
                    cameraY += 1
                mp.update()
            player.grav = 0

    mouse = pygame.mouse.get_pos()
    mouseHeld = pygame.mouse.get_pressed()

    if mouseHeld[0] and player.shoot:
        if tick < 30:
            tick += 1
        else:
            if bFrame < 2:
                bFrame += 1
            tick = 0
        bowRect = bow_animations.get_rect()
        abc = sin(atan2(mouse[0] - player.rect.x - player.rect.width / 2, mouse[1] - player.rect.y - player.rect.height / 2)) * 40
        cba = cos(atan2(mouse[0] - player.rect.x - player.rect.width / 2, mouse[1] - player.rect.y - player.rect.height / 2)) * 40
        if mouse[0] > player.rect.x:
            new = pygame.transform.rotate(bow_animations, (((atan2(mouse[1] - player.rect.y - player.rect.height / 2, mouse[0] - player.rect.x - player.rect.width / 2)) * -1) * 180 / pi))
            bowRect.x -= ((new.get_width() - 100) / 2) - abc - SCREEN_WIDTH / 2 + 15
            bowRect.y -= ((new.get_height() - 100) / 2) - cba - SCREEN_HEIGHT / 2 + 50
            screen.blit(new.convert_alpha(), bowRect)
        else:
            new2 = pygame.transform.rotate(bow_animations, (((atan2(mouse[1] - player.rect.y - player.rect.height / 2, mouse[0] - player.rect.x - player.rect.width / 2)) * -1) * 180 / pi))
            bowRect.x -= ((new2.get_width() - 100) / 2) - abc - SCREEN_WIDTH / 2 + 15
            bowRect.y -= ((new2.get_height() - 100) / 2) - cba - SCREEN_HEIGHT / 2 + 50
            screen.blit(new2.convert_alpha(), bowRect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_p:
                pygame.display.toggle_fullscreen()
            if event.key == pygame.K_r:
                cameraX = 0
                cameraY = 0
        elif event.type == pygame.MOUSEBUTTONDOWN:
            bFrame = 0
            mouse = pygame.mouse.get_pos()
            mouseX = mouse[0]
            mouseY = mouse[1]
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and player.shoot:
                if bFrame == 0:
                    th.Thread(target=player.shoot, args=(12.5, 1)).start()
                elif bFrame == 1:
                    th.Thread(target=player.shoot, args=(17.5, 3)).start()
                elif bFrame == 2:
                    th.Thread(target=player.shoot, args=(30, 5)).start()
                bFrame = 0

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and not keys[pygame.K_d] and player.health > 0:
        player.sped = 10
        player.direction = 'left'
    if keys[pygame.K_d] and not keys[pygame.K_a] and player.health > 0:
        player.sped = -10
        player.direction = 'right'
    if keys[pygame.K_SPACE] and checkCollisionY() and player.health > 0:
        th.Thread(target=player.jump).start()

    player.update()
    player.grav += 1
    for m in maps:
        m.update()
    for m in maps:
        while pygame.sprite.spritecollide(player, m.nonPhaseableTiles, False):
            if player.direction == 'left':
                cameraX -= 1
            else:
                cameraX += 1
            m.update()

    pygame.display.flip()
    screen.fill((100, 150, 100))