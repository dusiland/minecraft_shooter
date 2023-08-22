from random import randint
import pygame
import time
pygame.init()

win_width, win_height = 700, 500

window = pygame.display.set_mode((win_width, win_height))

back = pygame.image.load('pict/чит.png')
back = pygame.transform.scale(back, (win_width, win_height))

FPS = 60
clock = pygame.time.Clock()

pygame.mixer_music.load('space.ogg')
pygame.mixer_music.play(1)

fire_snd = pygame.mixer.Sound('fire.ogg')
game_over_snd = pygame.mixer.Sound("gameover.ogg") 

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, image, speed):
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)
        self.image = pygame.transform.scale(image, (w, h))
        self.speed = speed
    
    def update(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

enemys_group = pygame.sprite.Group()
bot_pic = pygame.image.load('pict/village.png')
bot_list = []
lost = 0

class Bot(GameSprite):
    def __init__(self, x, y, w, h, image, speed):
        super().__init__( x, y, w, h, image, speed) 
        bot_list.append(self)
        enemys_group.add(self)
        self.x_speed = randint(-4, 4)
        self.x_turn = randint(30, 180)

    def update(self):
        global lost
        self.rect.y += self.speed
        self.rect.x += self.x_speed
        if self.x_turn <= 0 or self.rect.x <= 0 or self.rect.x >= int(700 - self.rect.w):
            self.x_speed *= -1
            self.x_turn = randint(30, 180)
        else:
            self.x_turn -= 1
        if self.rect.y >= 500:
            lost += 1
            bot_list.remove(self)
            enemys_group.remove(self)

class Player(GameSprite):
    def __init__(self, x, y, w, h, image, speed, bullets_max):
        super().__init__(x, y, w, h, image, speed)
        self.bullets_max = bullets_max
        self.have_bullets = bullets_max
        self.need_reload = False

    def move(self, left, right):
        k = pygame.key.get_pressed()
        if k[left] and self.rect.x >= 0:
            self.rect.x -= 5
        if k[right] and (win_width - self.rect.x) >= self.rect.w:
            self.rect.x += 5

    def fire(self):
        if not self.need_reload:
            bullet = Bullet(self.rect.x + int(self.rect.w * 0.3), self.rect.y, 20,30, bullet_pic, 7)
            bullet_group.add(bullet)
            fire_snd.play()
            self.have_bullets -= 1
            if self.have_bullets == 0:
                self.need_reload = True

    # def colide(self, item):
    #     if self.rect.colliderect(item.rect):
    #         return True
    #     else:
    #         return False

# bullet_list = []
bullet_group = pygame.sprite.Group()

class Bullet(GameSprite):
    def __init__(self, x, y, w, h, image, speed):
        super().__init__( x, y, w, h, image, speed) 
        # bot_list.append(self)
        bullet_group.add(self)

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y <= 0:
            self.kill()

bullet_pic = pygame.image.load('pict/fireball.png')

player_pic = pygame.image.load('pict/gast.png')
player1 = Player(375, 420, 50, 60, player_pic, 4, 10)

font = pygame.font.SysFont('Mistral', 40)
font2 = pygame.font.SysFont('Mistral', 80)

score = 0

while True:
    try:
        with open('record.txt', 'r+') as file:
            max_score = 0
            try:
                data = file.read()
                max_score = int(data)
            except:
                print('Щось пішло не так')
        break
    except FileNotFoundError:
        file = open('record.txt', 'x')
        file.close()

spawn_bot = 0

game = True
screen = 'menu'

while game:
    if screen == 'menu':

        window.blit(back,(0,0))
        new_lb =font.render ("Натисніть ENTER щоб почати знову", True, (255,255,255)) 
        window.blit(new_lb,(105,240)) 

        max_scr_lb = font.render('Рекорд:' + str(max_score), True, (255,255,255))
        window.blit(max_scr_lb,( 270 ,290))

        enemys_group.empty()
        bullet_group.empty()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                screen = 'game'

    if screen == 'game':

        spawn_bot += 1

        window.blit(back,(0,0))

        lost_lb = font.render('Lost : ' + str(lost), True, (255,255,255))
        window.blit(lost_lb, (0,0))

        player1.update()
        player1.move(pygame.K_a, pygame.K_d)

        bullet_group.draw(window)
        bullet_group.update()

        reload_lb = font.render('Кількість куль:'+ str(player1.have_bullets), True, (255,255,255))
        window.blit(reload_lb,(0,50))

        if spawn_bot == 110:
            bot = Bot(randint(50, 625), -50, 70, 50, bot_pic, randint(1, 6))
            spawn_bot = 0

        if score > max_score:
            time_scr_lb = font.render('Новий рекорд', True, (255,255,255))
            window.blit(time_scr_lb,(0,100))

        if player1.need_reload:
            R_lb = font2.render('Press R to reloading', True, (255,255,255))
            window.blit(R_lb,(100,210))

        # for bot in bot_list:
        #     bot.update()
        #     bot.move()

        enemys_group.draw(window)
        enemys_group.update()

        if pygame.sprite.groupcollide(enemys_group, bullet_group, True, True):
            score += 1
        if pygame.sprite.spritecollide(player1, enemys_group, True, False) or lost == 3:
            if score > max_score:
                with open('record.txt', 'w') as file:
                    file.write(str(score))
            screen = 'gameover'

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player1.fire()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and player1.need_reload:
                player1.have_bullets = player1.bullets_max
                player1.need_reload = False
            if event.type == pygame.QUIT:
                game = False

    if screen == 'gameover':
        window.blit(back,(0,0))
        game_over_snd.play()
        game_over = font.render("Game Over", True, (255,255,255)) 
        window.blit(game_over,(250,150)) 
        new_lb =font.render ("Натисніть ENTER щоб почати знову", True, (255,255,255)) 
        window.blit(new_lb,(105,225))
        score_lb = font.render('Знищенно: ' + str(score), True, (255,255,255))
        window.blit(score_lb, (250,300))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                score = 0
                lost = 0
                screen = 'menu'

    pygame.display.update()
    clock.tick(FPS)