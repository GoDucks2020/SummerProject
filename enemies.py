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
bFrame = 0
pFrame = 0
rTick = 0
iFrame = 0
points = 0
pshoot = True
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


arrowSprite = getImage(arrowImage, 0, 0, 20, 5, 2, (0, 0, 0))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((20, 20))
        self.rect = self.image.get_rect()
        self.image.fill(color)
        self.x = x
        self.y = y
        self.intx = self.x
        self.inty = self.y - y
        self.bx = 0
        self.by = 0
        self.grav = 0
        self.health = 6
        self.direction = None
        self.healthBar = HealthBar(self, self.health)
        enemyHealth.add(self.healthBar)

    def update(self):
        global points
        self.grav += 1
        # self.y += self.grav
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

        while (pygame.sprite.spritecollide(self, map.nonPhaseableTiles, False) or
               pygame.sprite.spritecollide(self, map.barrierTiles, False)):
            if self.direction == 'right':
                self.x -= 1
            else:
                self.x += 1
            self.bx = self.intx + cameraX + self.x
            self.by = self.inty + cameraY + self.y
            self.rect.x = self.bx
            self.rect.y = self.by
        if self.health <= 0:
            self.kill()
            points += 1


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


class PlayerHealthBar(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((58, 12))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()

    def update(self):
        if player.health <= 0:
            self.kill()
        self.rect.x = player.rect.x - player.rect.width / 2
        self.rect.y = player.rect.y - 20


class PlayerHealth(pygame.sprite.Sprite):
    def __init__(self, healthBar):
        pygame.sprite.Sprite.__init__(self)
        self.healthBar = healthBar
        self.image = pygame.Surface((54, 8))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()

    def update(self):
        if player.health <= 0:
            self.kill()
            player.kill()
        try:
            self.image = pygame.Surface((player.health * 9, 8))
            self.image.fill((255, 0, 0))
        except:
            pass
        self.rect.x = self.healthBar.rect.x + 2
        self.rect.centery = self.healthBar.rect.centery


class Projectile(pygame.sprite.Sprite):
    def __init__(self, intx, inty, mouseX, mouseY, sped, damage):
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
        self.mouseX = mouseX
        self.mouseY = mouseY
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
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.x: int = 0
        self.y: int = 0
        self.tileSize = 30
        self.grid = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0],
                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,4,4,4,4,4,4,4,4,2,1,1,1,0],
                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,4,4,4,4,4,4,4,4,4,4,4,2,1],
                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,4,4,4,4,4,4,4,4,4,4,4,4,2],
                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,4,4,4,4,4,4,4,4,4,4,4,4,4,2],
                     [0,0,0,0,0,0,0,0,0,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,4,4,4,4,4,4,4,4,2],
                     [0,0,0,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,4,4,4,4,2],
                     [1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,2],
                     [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
                     [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]]
        self.nonPhaseableTiles = pygame.sprite.Group()
        self.barrierTiles = pygame.sprite.Group()
        self.phaseableTiles = pygame.sprite.Group()

    def render(self):
        for row in range(len(self.grid)):
            for column in range(len(self.grid[0])):
                self.x = column * self.tileSize + 5
                self.y = row * self.tileSize + 480
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
    def __init__(self, x: int, y: int) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface((30, 30))
        self.image.fill((100, 100, 255))
        self.rect = self.image.get_rect()
        self.direction = None
        self.rect.y = y
        self.rect.x = 615
        self.health = 6
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
    for tile in map.nonPhaseableTiles:
        if tile.type == 1:
            if tile.rect.top == player.rect.bottom and player.rect.left - player.rect.width < tile.rect.x < player.rect.right:
                return True
    return False

def checkCollisionYBottom() -> bool:
    for tile in map.nonPhaseableTiles:
        if tile.rect.bottom == player.rect.top and player.rect.left - player.rect.width < tile.rect.x < player.rect.right:
            return True
    return False

def jump():
    global grav, jumpable
    if jumpable:
        jumpable = False
        sleep(0.02)
        grav = -20
        jumpable = True

player = Player(SCREEN_WIDTH / 2 - 15, SCREEN_HEIGHT / 2 - 15)
playerHealthBar = PlayerHealthBar()
playerHealth = PlayerHealth(playerHealthBar)
map = Map()

players = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemyHealth = pygame.sprite.Group()
playerHealthBars = pygame.sprite.Group()
playerHealths = pygame.sprite.Group()
HEALTH = pygame.sprite.Group()

players.add(player)
enemies.add(Enemy(250, 580, 'red'))
playerHealthBars.add(playerHealthBar)
playerHealths.add(playerHealth)


map.render()

running = True
while running:
    rTick += 1
    if rTick % 240 == 0 and player.health > 0:
        enemies.add(Enemy(250, 580, 'red'))
    if iFrame != 0:
        iFrame -= 1
        invulnerable = True
    else:
        invulnerable = False
    if rTick % 6 == 0:
        pFrame += 1

    bow_animations = getImage(bowSpriteSheet, bFrame, 0, 100, 100, 1, (0, 0, 0))

    clock.tick(FPS)
    enemyHealth.update()
    HEALTH.update()
    playerHealthBars.update()
    playerHealths.update()

    # projectiles.draw(screen)
    map.draw(screen)
    players.draw(screen)
    enemies.draw(screen)
    enemyHealth.draw(screen)
    HEALTH.draw(screen)
    playerHealthBars.draw(screen)
    playerHealths.draw(screen)

    projectiles.update()

    if player.health <= 0:
        drawText(f"You ended with {points} points!", textFont, 'black', SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 5)

    for enemy in enemies:
        if pygame.sprite.spritecollide(enemy, projectiles, False):
            for projectile in projectiles:
                if pygame.sprite.spritecollide(projectile, enemies, False):
                    projectile.kill()
                    enemy.health -= projectile.damage
                    print('damage:' + str(projectile.damage) + 'health:' + str(enemy.health))
    for tile in map.nonPhaseableTiles:
        if pygame.sprite.spritecollide(tile, projectiles, False):
            for proj in projectiles:
                if (pygame.sprite.spritecollide(proj, map.nonPhaseableTiles, False) or
                    pygame.sprite.spritecollide(proj, map.barrierTiles, False)):
                        proj.kill()
    for tile in map.barrierTiles:
        if pygame.sprite.spritecollide(tile, projectiles, False):
            for proj in projectiles:
                if (pygame.sprite.spritecollide(proj, map.nonPhaseableTiles, False) or
                    pygame.sprite.spritecollide(proj, map.barrierTiles, False)):
                        proj.kill()
    if pygame.sprite.spritecollide(player, enemies, False) and not invulnerable:
        player.health -= 2
        iFrame = 60

    for i in range(grav):
        if not checkCollisionY():
            cameraY -= 1
            map.update()
        else:
            grav = 0
    for i in range(-grav):
        if not checkCollisionYBottom():
            cameraY += 1
            map.update()
        else:
            grav = 0

    mouse = pygame.mouse.get_pos()
    mouseHeld = pygame.mouse.get_pressed()

    if mouseHeld[0] and pshoot:
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
            if event.button == 1 and pshoot:
                if bFrame == 0:
                    th.Thread(target=pShoot, args=(12.5, 1)).start()
                elif bFrame == 1:
                    th.Thread(target=pShoot, args=(17.5, 3)).start()
                elif bFrame == 2:
                    th.Thread(target=pShoot, args=(30, 5)).start()
                bFrame = 0

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and not keys[pygame.K_d] and player.health > 0:
        cameraX += 10
        player.direction = 'left'
    if keys[pygame.K_d] and not keys[pygame.K_a] and player.health > 0:
        cameraX -= 10
        player.direction = 'right'
    if keys[pygame.K_SPACE] and checkCollisionY() and player.health > 0:
        th.Thread(target=jump).start()

    grav += 1
    enemies.update()
    map.update()

    while pygame.sprite.spritecollide(player, map.nonPhaseableTiles, False):
        if player.direction == 'left':
            cameraX -= 1
        else:
            cameraX += 1
        map.update()

    pygame.display.flip()
    screen.fill((200, 200, 200))
