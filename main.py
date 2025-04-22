
import pygame
import os
import time
import random
from pygame import mixer

pygame.mixer.init()
pygame.font.init()
WIDTH, HEIGHT = 1000, 1000
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("World of Spaceship")
game_pause=True
gameIcon = pygame.image.load(os.path.join("assets", "WOS.png"))
pygame.display.set_icon(gameIcon)

#Load Images
arr = os.listdir("assets")
print(arr)
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "boss.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "creep1.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "creep2.png"))
BOSS_SPACE_SHIP = pygame.image.load(os.path.join("assets", "Fboss.png"))
#Player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "player.png"))

#Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "boss_beam.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "grn_beam.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "cyan_beam.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "yel_beam.png"))
BOSS_LASER = pygame.image.load(os.path.join("assets", "Boss_ki.png"))


#Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "vutru.jpg")), (WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=200):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        obj.health -= 75
                        if obj.health <= 0:
                            objs.remove(obj)
                        explosion_Sound=mixer.Sound('explosion.wav')
                        explosion_Sound.play()
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER),
                "boss": (BOSS_SPACE_SHIP, BOSS_LASER)
                }
    
    maxhealth = {
                "red": 125,
                "green": 50,
                "blue": 100,
                "boss" : 180
                }

    def __init__(self, x, y, color, health=100):
        health = self.maxhealth[color]
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move(self, vel):
        self.x += vel[0]
        self.y += vel[1]


    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)
    i=0
    enemies = []
    wave_length = 5
    enemy_vel = [1, 1]

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0
    
    
    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("Game Over!!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()
    def text_objects(text,font):
        textsurface=font.render(text,True,"black")
        return textsurface,textsurface.get_rect()

    def button(msg,x,y,w,h,ic,ac,action=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        print(click)
        if x+w > mouse[0] > x and y+h > mouse[1] > y:
            pygame.draw.rect(gameDisplay, ac,(x,y,w,h))
            if click[0] == 1 and action != None:
                action()         
        else:
            pygame.draw.rect(gameDisplay, ic,(x,y,w,h))
        smallText = pygame.font.SysFont("comicsansms",20)
        textSurf, textRect = text_objects(msg, smallText)
        textRect.center = ( (x+(w/2)), (y+(h/2)) )
        gameDisplay.blit(textSurf, textRect)
    
    def gamepause():
          global game_pause
          while game_pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()          
            largeText = pygame.font.SysFont("comicsansms",115)
            TextSurf, TextRect = text_objects("Paused", largeText)
            TextRect.center = ((WIDTH/2),(HEIGHT/2))
            gameDisplay.blit(TextSurf, TextRect)
            button("Continue",150,450,100,50,"green","green",unpause)
            button("Quit",550,450,100,50,"red","red",quitgame)
            pygame.display.update()
           

    def quitgame():
        pygame.quit()
    def unpause():
        global game_pause
        game_pause=False
    
    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green", "boss"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
            bullet_sound=mixer.Sound('laser.wav')
            bullet_sound.play()
            
        if keys[pygame.K_ESCAPE]:
            global game_pause
            game_pause=True
            gamepause()
        if keys[pygame.K_m]:
            mixer.music.pause()
        if keys[pygame.K_n]:
            mixer.music.unpause()   
           
        for enemy in enemies[:]:
            if not (0 <= enemy.x + enemy_vel[0] <= WIDTH):
                enemy_vel[0] *= -1
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True

    # Phát nhạc intro khi vào menu
    mixer.music.load("intro.mp3")
    mixer.music.play(-1)  # Lặp lại vô hạn

    while run:
        WIN.blit(BG, (0,0))
        title_label = pygame.image.load(os.path.join("assets", "WOS.png"))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 200))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Khi bắt đầu chơi thì dừng nhạc intro
                mixer.music.stop()

                # Chạy game và phát nhạc game
                mixer.music.load("musicback.mp3")
                mixer.music.play(-1)
                main()
    pygame.quit()



main_menu()