import pygame
import os
import time
import random

from pygame.constants import K_DOWN
pygame.font.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1550,780 
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Invaders")
# Load Images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png"))

# Player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets","pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets","pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets","pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets","background-black.png")), (WIDTH,HEIGHT))
LASER_SOUND = pygame.mixer.Sound("assets\laser_sound.wav")
HIT_SOUND = pygame.mixer.Sound("assets\hit_sound.wav")

MUSIC = pygame.mixer.music.load("assets\music_kahoot.mp3")      #Music
pygame.mixer.music.play(-1)

# HighScores
HIGHSCORES = []
with open("assets\HighScores.txt","r") as file:
    for rivi in file:
        HIGHSCORES.append(int(rivi))
highScore = HIGHSCORES[0]
current_score = 0

class Laser:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    def draw(self,window):
        window.blit(self.img, (self.x,self.y))
    def move(self, vel):
        self.y+=vel
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)
    def collision(self,obj):
        return collide(obj,self)
        

class Ship:
    COOLDOWN = 10                                                                  # Player firerate, ehkä joku perkki systeemi?
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
    
    def draw(self, window):
        window.blit(self.ship_img, (self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)
    
    def move_lasers(self,vel,obj):
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
            laser = Laser(self.x,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self,vel,objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:   
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            return True
    def draw(self,window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self,window):
        pygame.draw.rect(window, (255,0,0),(self.x,self.y + self.ship_img.get_height() + 10,self.ship_img.get_width(),10))
        pygame.draw.rect(window, (0,255,0),(self.x,self.y + self.ship_img.get_height() + 10,self.ship_img.get_width()*(self.health/self.max_health),10))

class Enemy(Ship):
    COLOR_MAP = {
        "red":(RED_SPACE_SHIP,RED_LASER),
        "green":(GREEN_SPACE_SHIP,GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP,BLUE_LASER)
        }
    
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-17,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x-obj1.x
    offset_y = obj2.y-obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None
def main():
    run = True
    FPS = 80                               #Frames per second, mutable
    level = 0                                   #Starting Level
    lives = 3                                   #Lives    
    score = 0
    current_score = 0
    highScore = int(HIGHSCORES[0])
    main_font = pygame.font.SysFont("8-Bit-Madness", 35, True)
    lost_font = pygame.font.SysFont("8-Bit-Madness", 100, True)
    enemies = []
    wave_length = 5
    enemy_vel = 1                               #Enemy velocity
    player_vel = 10                              #Player velocity
    laser_vel = 4                               #Laser velocity
    player = Player(300,630)
    clock = pygame.time.Clock()
    lost = False
    lost_count = 0
    hscore_clr = 255
    def redraw_window():
        WIN.blit(BG, (0,0))
        lives_clr = lives*player.health*0.85
        lives_label = main_font.render(f"Lives: {lives}",1,(255,lives_clr,lives_clr))
        level_label = main_font.render(f"Level: {level}",1,(255,255,255))
        score_label = main_font.render(f"Score: {score} | Highscore: {highScore}",1,(hscore_clr,255,hscore_clr))
    


        WIN.blit(lives_label, (10,10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10,10))
        WIN.blit(score_label, (WIDTH/2 -score_label.get_width()/2,10))
        for enemy in enemies:
            enemy.draw(WIN)
        player.draw(WIN)
        if lost:
            lost_label = lost_font.render("Game Over",1, (255,0,0))
            WIN.blit(lost_label, (WIDTH/2 -lost_label.get_width()/2,350))
        pygame.display.update()
    while run:
        clock.tick(FPS)
        redraw_window()
        if score > highScore:
            highScore = score
            hscore_clr = 0
        if player.health <= 0:
            lives-=1
            player.health = 100
        if lives <= 0:
            lost = True
            lost_count += 1
        if lost:
            if lost_count > FPS*2:
                run = False
            else:
                continue
        if len(enemies) == 0:
            level +=1
            score+=100*(level-1)
            wave_length += 5                                                                #DIFFICULTY> more enemies per wave
            for i in range(wave_length):
                enemy = Enemy(random.randrange(100,WIDTH-100),random.randrange(-1500,-100),random.choice(["red","blue","green"]))
                enemies.append(enemy)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > -50:                             #left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width()-50 < WIDTH:  #right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:                                 #up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height()+10 < HEIGHT: #down
            player.y += player_vel
        if keys[pygame.K_SPACE]:                                                            #shoot
            player.shoot()
            # LASER_SOUND.play()
        if keys[pygame.K_ESCAPE]:
            end_menu(score)

        

        for enemy in enemies:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0,160) ==1:                                                 #DIFFICULTY: change the firing rate of enemies
                enemy.shoot()
            
            if collide(enemy, player):
                player.health -= 10
                # HIT_SOUND.play()
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        if player.move_lasers(-laser_vel, enemies):
            score += 10*level
    for i in range(len(HIGHSCORES)):
        if score>HIGHSCORES[i]:
            HIGHSCORES.pop
            for j in range(9,i,-1):
                HIGHSCORES[j]=HIGHSCORES[j-1]
            HIGHSCORES[i] = score
            break
    with open("assets\HighScores.txt","w") as file:
        for rivi in HIGHSCORES:
            file.write(str(rivi)+"\n")
    end_menu(score)  
                
def end_menu(current_score):
    title_font = pygame.font.SysFont("8-Bit-Madness",50,True)
    list_font = pygame.font.SysFont("8-Bit-Madness",40)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("HighScores: ",1,(255,255,255))
        s = 1
        y = 100

        WIN.blit(title_label,(WIDTH/2 - title_label.get_width()/2, 50))
        for i in range(0,10):
            list_label = list_font.render((str(s)+"."),1,(150,150,150))
            WIN.blit(list_label,(0.38*WIDTH,y ))
            list_label = list_font.render((str(HIGHSCORES[i]).strip()),1,(100,255,150))
            WIN.blit(list_label,(0.6*WIDTH,y ))
            s += 1
            y+=30
        list_label = list_font.render(("Your Score: "+str(current_score)),1,(100,150,255))
        WIN.blit(list_label,(0.45*WIDTH,430 ))
        title_label = title_font.render("Any key to PlayAgain",1,(255,255,255))
        WIN.blit(title_label,(WIDTH/2 - title_label.get_width()/2, 700))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quit()
            if event.type == pygame.KEYDOWN:
                run = False
def main_menu():
    title_font = pygame.font.SysFont("8-Bit-Madness",70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press any key to begin...",1,(255,255,255))
        WIN.blit(title_label,(WIDTH/2 - title_label.get_width()/2, 350))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                main()
main_menu()