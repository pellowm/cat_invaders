import pygame
import os
import time
import random
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cat Invaders")

dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))
print(dirpath)

#load images
RED_SPACE_SHIP = pygame.image.load(os.path.abspath(os.path.join(dirpath, "cat_red.png")))
GREEN_SPACE_SHIP = pygame.image.load(os.path.abspath(os.path.join(dirpath, "cat_green.png")))
BLUE_SPACE_SHIP = pygame.image.load(os.path.abspath(os.path.join(dirpath, "cat_blue.png")))

#player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.abspath(os.path.join(dirpath, "dobby.png")))

#lasers
RED_LASER = pygame.image.load(os.path.abspath(os.path.join(dirpath, "pixel_laser_red.png")))
GREEN_LASER = pygame.image.load(os.path.abspath(os.path.join(dirpath, "pixel_laser_green.png")))
BLUE_LASER = pygame.image.load(os.path.abspath(os.path.join(dirpath, "pixel_laser_blue.png")))
YELLOW_LASER = pygame.image.load(os.path.abspath(os.path.join(dirpath, "bark_laser_2.png")))

#background
BG = pygame.transform.scale(pygame.image.load(os.path.abspath(os.path.join(dirpath, "background-black.png"))), (WIDTH, HEIGHT))

#sounds
bark_sound = pygame.mixer.Sound(os.path.abspath(os.path.join(dirpath, "short.wav")))
kitten_meow = pygame.mixer.Sound(os.path.abspath(os.path.join(dirpath, "kitten_meow.ogg")))
cat_death = pygame.mixer.Sound(os.path.abspath(os.path.join(dirpath, "cat_death.wav")))

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
        return collide(obj, self)

class Ship:
    COOLDOWN = 20

    def __init__(self, x, y, color, health=100):
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
            bark_sound.play()
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

#player inherits from ship
class Player(Ship):
    def __init__(self, x, y, health=100):
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
                        #angry meow here
                        if obj.ship_img == BLUE_SPACE_SHIP:
                            kitten_meow.play()
                        if obj.ship_img == GREEN_SPACE_SHIP or obj.ship_img == RED_SPACE_SHIP :
                            cat_death.play()
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health), 10))
        #pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (4 / 5), 10))

class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
    

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 3
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)


    enemies = []
    wave_length = 5
    enemy_vel = 1
    laser_vel = 4
    player_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        #draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        #drawn after enemies, so that player is shown if collision happens
        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("GAME OVER", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
        
        pygame.display.update()

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
            if level >= 6:
                victory_screen()
                run = False
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()


        for enemy in enemies:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 3*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -=1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 90)
    instructions_font = pygame.font.SysFont("comicsans", 25)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("CAT INVADERS", 1, (255, 255, 255))
        instructions_label = instructions_font.render("click to begin", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 300))
        WIN.blit(instructions_label, (WIDTH/2 - instructions_label.get_width()/2, 550))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                instructions_screen()
    pygame.quit()
            
def victory_screen():
    victory_font = pygame.font.SysFont("comicsans", 50)
    victory_font_2 = pygame.font.SysFont("comicsans", 25)


    run = True
    while run:
        WIN.blit(BG, (0,0))
        victory_label_1 = victory_font.render("You win! Those darned cats are gone.", 1, (255, 255, 255))
        victory_label_2 = victory_font.render("You can now rest easy in your castle.", 1, (255, 255, 255))
        SLEEPY = pygame.image.load(os.path.abspath(os.path.join(dirpath, "sleepy.png")))
        sleepy_small = pygame.transform.scale(SLEEPY, (400, 250))
        victory_label_3 = victory_font_2.render("Click to play again", 1, (255, 255, 255))
        
        WIN.blit(victory_label_1, (WIDTH/2 - victory_label_1.get_width()/2, 150))
        WIN.blit(sleepy_small, (WIDTH/2 - sleepy_small.get_width()/2, 200))
        WIN.blit(victory_label_2, (WIDTH/2 - victory_label_2.get_width()/2, 475))
        WIN.blit(victory_label_3, (WIDTH/2 - victory_label_3.get_width()/2, 600))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main_menu()
    pygame.quit()

def instructions_screen():
    instructions_font = pygame.font.SysFont("comicsans", 35)
    instructions_font_2 = pygame.font.SysFont("comicsans", 25)

    run = True
    while run:
        WIN.blit(BG, (0,0))
        instructions_label_1 = instructions_font.render("Help Dobby scare away the cat invaders ", 1, (255, 255, 255))
        instructions_label_2 = instructions_font.render("by barking with the space bar. ", 1, (255, 255, 255))
        instructions_label_3 = instructions_font.render("Dodge their lasers with the arrow keys. ", 1, (255, 255, 255))
        instructions_label_4 = instructions_font.render("Try to hold down the fort for 5 rounds!", 1, (255, 255, 255))
        instructions_label_5 = instructions_font_2.render("Click to start your defense.", 1, (255, 255, 255))
        WIN.blit(instructions_label_1, (WIDTH/2 - instructions_label_1.get_width()/2, 250))
        WIN.blit(instructions_label_2, (WIDTH/2 - instructions_label_2.get_width()/2, 300))
        WIN.blit(instructions_label_3, (WIDTH/2 - instructions_label_3.get_width()/2, 350))
        WIN.blit(instructions_label_4, (WIDTH/2 - instructions_label_4.get_width()/2, 400))
        WIN.blit(instructions_label_5, (WIDTH/2 - instructions_label_5.get_width()/2, 550))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

main_menu()
