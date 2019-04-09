import pygame as pg
from settings import *
from os import path
vec = pg.math.Vector2

class Boxer(pg.sprite.Sprite):
    def __init__(self, game, side):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.side = side
        self.actions = ['Blocking', 'Dizzy', 'Hurt', 'Idle', 'KO', 'Punch', 'PunchUp', 'Walk', 'WalkBack']

        # 角色動畫相關初始化
        self.walking = False
        self.punching = True
        self.punching_up = False
        self.current_frame = 0
        self.last_update = 0

        # 角色圖片、位置、速度、加速度初始化
        self.load_images()
        self.image = self.action_frames['Idle'][0]
        self.rect = self.image.get_rect()
        if self.side == 'red':
            self.rect.center = (100, HEIGHT - 50)
            self.pos = vec(100, HEIGHT - 50)
        elif self.side == 'blue':
            self.rect.center = (900, HEIGHT - 50)
            self.pos = vec(900, HEIGHT - 50)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        
    def load_images(self):
        # 讀取資料
        self.action_frames = {} # 用一個dictionary存取所有動作的frames
        actions_dir = path.join(self.game.img_dir, self.side)
        frame_num = {'Blocking':10, 'Dizzy':8, 'Hurt':8, 'Idle':10, 'KO':10, 'Punch':12, 'PunchUp':7, 'Walk':10, 'WalkBack':10}
        for action in self.actions:
            self.action_frames[action] = []
            action_dir = path.join(actions_dir, action)
            for i in range(frame_num[action]):
                pic_path = path.join(action_dir, '__Boxing04_{}_{:03}.png'.format(action, i))
                pic = pg.image.load(pic_path).convert_alpha()
                if self.side == 'blue':
                    pic = pg.transform.flip(pic, True, False)
                rect = pic.get_rect()
                pic = pg.transform.scale(pic, (rect.width // 3, rect.height // 3))
                self.action_frames[action].append(pic)

    def update(self):
        # 角色所有動作
        self.animate()
        self.acc = vec(0, BOXER_GRAV)

        # Key event
        keys = pg.key.get_pressed()
        if self.side == 'red':
            if keys[pg.K_a]:
                self.acc.x = -1 * BOXER_ACC
            if keys[pg.K_d]:
                self.acc.x = BOXER_ACC
            if keys[pg.K_f]:
                self.punching = True
            else:
                self.punching = False
            if keys[pg.K_h]:
                self.punching_up = True
            else:
                self.punching_up = False
        elif self.side == 'blue':
            if keys[pg.K_LEFT]:
                self.acc.x = -1 * BOXER_ACC
            if keys[pg.K_RIGHT]:
                self.acc.x = BOXER_ACC
            if keys[pg.K_COMMA]:
                self.punching = True
            else:
                self.punching = False
            if keys[pg.K_SLASH]:
                self.punching_up = True
            else:
                self.punching_up = False
        
        # 摩擦力
        self.acc.x += self.vel.x * BOXER_FRICTION
        # Equation of motion
        self.vel += self.acc
        # 防止x軸速度永遠不為零
        if abs(self.vel.x) < 0.35:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        # 畫面邊界
        if self.pos.x + (self.rect.width / 2) > WIDTH:
            self.pos.x = WIDTH - (self.rect.width / 2)
        if self.pos.x - (self.rect.width / 2) < 0:
            self.pos.x = 0 + (self.rect.width / 2)
        if self.pos.y > HEIGHT:
            self.pos.y = HEIGHT
        
        self.rect.midbottom = self.pos # 將角色的rect更新為pos向量的座標
    
    def animate(self):
        # 角色所有動畫
        now = pg.time.get_ticks()

        # 動作判斷
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False

        # Walking animation
        if self.walking:
            if self.side == 'red':
                if self.vel.x > 0:
                    self.action('Walk', 50)
                else:
                    self.action('WalkBack', 50)
            elif self.side == 'blue':
                if self.vel.x > 0:
                    self.action('WalkBack', 50)
                else:
                    self.action('Walk', 50)
        # Punch Right animation
        elif self.punching:
            self.action('Punch', 50)
        elif self.punching_up:
            self.action('PunchUp', 50)
        # Idle animation
        else:
            self.action('Idle', 100)

    def action(self, kind, rate):
        now = pg.time.get_ticks()
        if now - self.last_update > rate:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.action_frames[kind])
            bottom = self.rect.bottom
            self.image = self.action_frames[kind][self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom