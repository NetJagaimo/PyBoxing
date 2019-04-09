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
    
    def new(self):
        # 開始新遊戲
        self.all_sprites = pg.sprite.Group()
        self.boxer_red = Boxer(self, 'red')
        self.boxer_blue = Boxer(self, 'blue')
        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        # Game Loop - Update，遊戲的動作
        self.all_sprites.update()

        #碰撞判定

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
        self.all_sprites.draw(self.screen)
        self.draw_blood()
        pg.display.flip()
        
    def draw_blood(self):
        # 繪製當前血量
        pass

    def intro(self):
        # Game Intro，遊戲開始畫面
        pass
    
    def gameover(self):
        # Game Over，遊戲結束畫面
        pass
    
    def wait_for_key(self):
        # 按下任何按鍵後才會繼續執行
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for events in pg.event.get():
                if events.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if events.type == pg.KEYUP:
                    waiting = False

    
    def draw_text(self, text, size, color, x, y):
        # 顯示文字
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text.rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

game = Game()
game.intro()
while game.running:
    game.new()
    game.gameover

pg.quit()
quit()
