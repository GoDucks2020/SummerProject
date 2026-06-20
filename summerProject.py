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

grassImage = pygame.image.load('/Users/jacobkerr/ComputerProgramingFinal test/summerProject/.venv/grass.png')
bowSpriteSheet = pygame.image.load('/Users/jacobkerr/ComputerProgramingFinal test/summerProject/.venv/bowSpriteSheet.png').convert_alpha()
arrowImage = pygame.image.load('/Users/jacobkerr/ComputerProgramingFinal test/summerProject/.venv/arrow.png').convert_alpha()

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
        self.damage = damage

    def update(self):
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


def pShoot(sped, damage):
    global pshoot
    mouse = pygame.mouse.get_pos()
    mouseX = mouse[0]
    mouseY = mouse[1]
    if pshoot:
        pshoot = False
        if mouse[0] < SCREEN_WIDTH / 2:
            projectiles.add(Projectile(cameraX, cameraY, mouseX, mouseY, sped, damage))
        else:
            projectiles.add(Projectile(cameraX, cameraY, mouseX, mouseY, sped, damage))
        sleep(1)
        pshoot = True


def checkCollisionY() -> bool:
    for tile in map.tiles:
        if tile.type == 1:
            if tile.rect.top == player.rect.bottom and player.rect.left - player.rect.width < tile.rect.x < player.rect.right:
                return True
    return False

def checkCollisionXRight() -> bool:
    for tile in map.tiles:
        if tile.rect.left == player.rect.right and tile.rect.top < player.rect.top + player.rect.height:
            return True
    return False

def checkCollisionXLeft() -> bool:
    for tile in map.tiles:
        if tile.rect.right == player.rect.left and tile.rect.top < player.rect.top + player.rect.height:
            return True
    return False


player = Player(SCREEN_WIDTH / 2 - 15, SCREEN_HEIGHT / 2 - 15)
map = Map()

players = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemyHealth = pygame.sprite.Group()
HEALTH = pygame.sprite.Group()

players.add(player)
enemies.add(Enemy(200, 580, 'red'))

map.render()

running = True
while running:
    bow_animations = getImage(bowSpriteSheet, bframe, 0, 100, 100, 1, (0, 0, 0))

    projectiles.update()
    clock.tick(FPS)
    enemies.update()
    map.tiles.update()
    enemyHealth.update()
    HEALTH.update()

    map.tiles.draw(screen)
    players.draw(screen)
    enemies.draw(screen)
    enemyHealth.draw(screen)
    HEALTH.draw(screen)

    for enemy in enemies:
        if pygame.sprite.spritecollide(enemy, projectiles, False):
            for projectile in projectiles:
                if pygame.sprite.spritecollide(projectile, enemies, False):
                    projectile.kill()
                    enemy.health -= projectile.damage
                    print('damage: ' + str(projectile.damage) + ' health: ' + str(enemy.health))

    # projectiles.draw(screen)

    for i in range(grav):
        if not checkCollisionY():
            cameraY -= 1
            map.tiles.update()
        else:
            grav = 0
    for i in range(-grav):
        cameraY += 1

    mouse = pygame.mouse.get_pos()
    mouseHeld = pygame.mouse.get_pressed()

    if mouseHeld[0] and pshoot:
        if tick < 30:
            tick += 1
        else:
            if bframe < 2:
                bframe += 1
            tick = 0
        bowRect = bow_animations.get_rect()
        abc = sin(atan2(mouse[0] - player.rect.x - player.rect.width / 2, mouse[1] - player.rect.y - player.rect.height / 2)) * 40
        cba = cos(atan2(mouse[0] - player.rect.x - player.rect.width / 2, mouse[1] - player.rect.y - player.rect.height / 2)) * 40
        if mouse[0] > player.rect.x:
            new = pygame.transform.rotate(bow_animations, (((atan2(mouse[1] - player.rect.y - player.rect.height / 2, mouse[
                0] - player.rect.x - player.rect.width / 2)) * -1) * 180 / pi))
            bowRect.x -= ((new.get_width() - 100) / 2) - abc - SCREEN_WIDTH / 2 + 50
            bowRect.y -= ((new.get_height() - 100) / 2) - cba - SCREEN_HEIGHT / 2 + 50
            screen.blit(new.convert_alpha(), bowRect)
        else:
            new2 = pygame.transform.rotate(bow_animations, (((atan2(mouse[1] - player.rect.y - player.rect.height / 2, mouse[
                0] - player.rect.x - player.rect.width / 2)) * -1) * 180 / pi))
            bowRect.x -= ((new2.get_width() - 100) / 2) - abc - SCREEN_WIDTH / 2 + 50 + 0
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
            elif event.key == pygame.K_SPACE and grav == 0:
                grav = -20
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse = pygame.mouse.get_pos()
            mouseX = mouse[0]
            mouseY = mouse[1]
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and pshoot:
                if bframe == 0:
                    th.Thread(target=pShoot, args=(12.5,1)).start()
                elif bframe == 1:
                    th.Thread(target=pShoot, args=(17.5,3)).start()
                elif bframe == 2:
                    th.Thread(target=pShoot, args=(30,5)).start()
                    bframe = 0

    keys = pygame.key.get_pressed()
    checkCollisionXRight()
    if keys[pygame.K_a] and not keys[pygame.K_d]:
        if not checkCollisionXLeft():
            cameraX += 10
    if keys[pygame.K_d] and not keys[pygame.K_a]:
        if not checkCollisionXRight():
            cameraX -= 10

    grav += 1
    pygame.display.flip()
    screen.fill((200, 200, 200))

