import pygame as pg
import random
from os import path
from settings import *
from sprites import *

class Game:
    def __init__(self):
        # 遊戲初始化
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self):
        # 讀入資料
        self.dir = path.dirname(__file__) # 如果在當前資料夾執行檔案，這行就沒有用。但如果用絕對路徑執行，這行就有用
        self.img_dir = path.join(self.dir, 'img')

        # 讀入stage
        self.stage_img = pg.image.load(path.join(self.img_dir, 'stage.jpg')).convert_alpha()
        self.stage_img = pg.transform.scale(self.stage_img, (1000, 561))
        self.stage_img = pg.transform.flip(self.stage_img, True, False)
        self.stage_img_rect = self.stage_img.get_rect()
        self.stage_img_rect.midbottom = (WIDTH / 2, HEIGHT)

        # 讀入intrologo
        self.intrologo_img = pg.image.load(path.join(self.img_dir, 'intrologo.jpg')).convert()
        self.intrologo_img_rect = self.intrologo_img.get_rect()
        self.intrologo_img = pg.transform.scale(self.intrologo_img, 
                                               (self.intrologo_img_rect.width * 3 // 5 , self.intrologo_img_rect.height * 3 // 5))
        self.intrologo_img_rect = self.intrologo_img.get_rect()
        self.intrologo_img_rect.center = (WIDTH / 2, HEIGHT / 3)

        # 讀入音樂
        self.snd_dir = path.join(self.dir, 'snd')
        self.punch_swoosh_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Punch_Swoosh.ogg'))
        self.hurt_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Punch_Sound_Effect.ogg'))
        self.dizzy_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Dizzy_Sound_Effect.ogg'))

    def new(self):
        # 開始新遊戲
        self.all_sprites = pg.sprite.Group()
        self.red_team = pg.sprite.Group()
        self.blue_team = pg.sprite.Group()
        self.boxer_red = Boxer(self, 'red')
        self.boxer_blue = Boxer(self, 'blue')
        pg.mixer.music.load(path.join(self.snd_dir, 'playing.ogg'))
        self.run()

    def run(self):
        # Game Loop
        pg.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500)

    def update(self):
        # Game Loop - Update，遊戲的動作
        self.all_sprites.update()
        #碰撞判定
        hits = pg.sprite.spritecollide(self.boxer_red, self.blue_team, False, pg.sprite.collide_mask)
        if hits:
            # 紅方攻擊判斷
            if not self.boxer_blue.hurting and not self.boxer_blue.dizzying \
               and not self.boxer_red.walking \
               and self.boxer_red.pos.x + 55 < self.boxer_blue.pos.x:
                # 衝刺攻擊判定
                if self.boxer_red.sprinting:
                    self.hurt_sound.play()
                    self.boxer_blue.blood -= 15
                    self.boxer_blue.hurting = True
                # 正拳擊中判定
                if self.boxer_red.punching:
                    self.hurt_sound.play()
                    self.boxer_blue.blood -= 10
                    self.boxer_blue.hurting = True
                # 上鉤拳擊中判定
                if self.boxer_red.punching_up:
                    self.hurt_sound.play()
                    self.boxer_blue.blood -= 5
                    self.boxer_blue.hurting = True
                    self.boxer_blue.dizzy_num += random.randrange(1, 4)
                    if self.boxer_blue.dizzy_num >= 13:
                        self.dizzy_sound.play()
                        self.boxer_blue.dizzy_num = 0
                        self.boxer_blue.dizzying = True
            # 藍方攻擊判斷
            if not self.boxer_red.hurting and not self.boxer_red.dizzying \
               and not self.boxer_blue.walking \
               and self.boxer_blue.pos.x - 55 > self.boxer_red.pos.x:
                # 衝刺攻擊判定
                if self.boxer_blue.sprinting:
                    self.hurt_sound.play()
                    self.boxer_red.blood -= 15
                    self.boxer_red.hurting = True
                # 正拳擊中判定
                if self.boxer_blue.punching:
                    self.hurt_sound.play()
                    self.boxer_red.blood -= 10
                    self.boxer_red.hurting = True
                # 上鉤拳擊中判定
                if self.boxer_blue.punching_up:
                    self.hurt_sound.play()
                    self.boxer_red.blood -= 5
                    self.boxer_red.hurting = True
                    self.boxer_red.dizzy_num += random.randrange(1, 4)
                    if self.boxer_red.dizzy_num >= 13:
                        self.dizzy_sound.play()
                        self.boxer_red.dizzy_num = 0
                        self.boxer_red.dizzying = True

        # 遊戲結束判斷
        if self.boxer_red.blood <= 0:
            self.boxer_red.KOing = True
        elif self.boxer_blue.blood <= 0:
            self.boxer_blue.KOing = True
                
    def events(self):
        # Game Loop - events，按鍵事件
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def draw(self):
        # Game Loop - Draw，將update之後的東西繪製到遊戲主畫面上
        self.screen.fill(WHITE)
        self.screen.blit(self.stage_img, self.stage_img_rect)
        self.all_sprites.draw(self.screen)
        self.draw_blood()
        self.draw_charge_point()
        pg.display.flip()
        
    def draw_blood(self):
        # 繪製當前血量
        # 藍色血量，+1為了防止完全歸零而畫不出來
        self.blue_blood = pg.Surface((abs(self.boxer_blue.blood) * 1.5 + 1, 20))
        self.blue_blood.fill(BLUE)
        self.blue_blood_rect = self.blue_blood.get_rect()
        self.blue_blood_rect.topleft = (750, 50)
        self.screen.blit(self.blue_blood, self.blue_blood_rect)
        # 紅色血量
        self.red_blood = pg.Surface((abs(self.boxer_red.blood) * 1.5 + 1, 20))
        self.red_blood.fill(RED)
        self.red_blood_rect = self.red_blood.get_rect()
        self.red_blood_rect.topleft = (100, 50)
        self.screen.blit(self.red_blood, self.red_blood_rect)
    
    def draw_charge_point(self):
        # 繪製集氣條
        # 藍方集氣條
        if self.boxer_blue.charging and self.boxer_blue.charge_point > 0:
            self.blue_charge_point = pg.Surface((2 * self.boxer_blue.charge_point, 20))
            self.blue_charge_point.fill(GREEN)
            self.blue_charge_point_rect = self.blue_charge_point.get_rect()
            self.blue_charge_point_rect.bottomleft = (self.boxer_blue.pos.x - 60, self.boxer_blue.rect.top + 10)
            self.screen.blit(self.blue_charge_point, self.blue_charge_point_rect)
        # 紅方集氣條
        if self.boxer_red.charging and self.boxer_red.charge_point > 0:
            self.red_charge_point = pg.Surface((2 * self.boxer_red.charge_point, 20))
            self.red_charge_point.fill(GREEN)
            self.red_charge_point_rect = self.red_charge_point.get_rect()
            self.red_charge_point_rect.bottomleft = (self.boxer_red.pos.x - 30, self.boxer_red.rect.top + 10)
            self.screen.blit(self.red_charge_point, self.red_charge_point_rect)

    def intro(self):
        # Game Intro，遊戲開始畫面
        pg.mixer.music.load(path.join(self.snd_dir, 'intro_music.mp3'))
        pg.mixer.music.play(loops=-1)    
        self.screen.fill(WHITE)
        self.screen.blit(self.intrologo_img, self.intrologo_img_rect)
        self.draw_text('Py', 90, BLUE, 390, HEIGHT * 4 / 7 )
        self.draw_text('Boxing!', 90, RED, 555, HEIGHT * 4 / 7)
        self.draw_text('Press space to start', 44, GREEN, WIDTH / 2, HEIGHT * 7 / 9)
        pg.display.flip()
        self.wait_for_space()
        pg.mixer.music.fadeout(500)
    
    def gameover(self):
        # Game Over，遊戲結束畫面
        if not self.running:
            return
        pg.mixer.music.load(path.join(self.snd_dir, 'win_music.mp3'))
        pg.mixer.music.play(loops=-1)    
        self.screen.fill(WHITE)
        if self.boxer_blue.blood <= 0:
            self.draw_text('RED WIN!', 100, RED, WIDTH / 2, HEIGHT / 3)
        else:
            self.draw_text('BLUE WIN!', 100, BLUE, WIDTH / 2, HEIGHT / 3)
        self.draw_text('Press space to start', 44, GREEN, WIDTH / 2, HEIGHT * 2 / 3)
        pg.display.flip()
        self.wait_for_space()
        pg.mixer.music.fadeout(500)
    
    def wait_for_space(self):
        # 按下任何按鍵後才會繼續執行
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for events in pg.event.get():
                if events.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if events.type == pg.KEYUP:
                    if events.key == pg.K_SPACE:
                        waiting = False

    def draw_text(self, text, size, color, x, y):
        # 顯示文字
        font = pg.font.Font(path.join(self.dir, 'font', 'BoxingWizards-Regular.otf'), size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

game = Game()
game.intro()
while game.running:
    game.new()
    game.gameover()

pg.quit()
quit()
