import pygame as pg
from settings import *
from os import path
vec = pg.math.Vector2

class Boxer(pg.sprite.Sprite):
    def __init__(self, game, side):
        if side == 'red':
            self.groups = game.all_sprites, game.red_team
        else:
            self.groups = game.all_sprites, game.blue_team
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.side = side
        self.actions = ['Blocking', 'Dizzy', 'Hurt', 'Idle', 'KO', 'Punch', 'PunchUp', 'Walk', 'WalkBack']

        # 角色動畫相關初始化
        self.walking = False
        self.punching = True
        self.punching_up = False
        self.hurting = False
        self.dizzying = False
        self.KOing = False
        self.charging = False
        self.sprinting = False
        self.sprinting_punching_count = 0
        self.charge_point = -1
        self.charge_point_last_update = 0
        self.current_frame = 0
        self.last_update = 0
        self.stop_time = 0
        self.unstoppable_count = 0

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

        # 角色數值初始化
        self.blood = 100
        self.dizzy_num = 0
        
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
        friction = BOXER_FRICTION
        # Charge
        if self.charging:
            now = pg.time.get_ticks()
            if now - self.charge_point_last_update > 50:
                self.charge_point_last_update = now
                self.charge_point += 1
                if self.charge_point >= 35:
                    self.sprinting = True
                    self.charge_point = -1
                    self.charging = False
                elif self.charge_point >= 25:
                    friction = CHARGING_FRICTION_2
                elif self.charge_point >= 10:
                    friction = CHARGING_FRICTION_1
        self.acc = vec(0, BOXER_GRAV)
        if not self.hurting and not self.dizzying and not self.KOing:
            self.events()
        # 受傷動作
        if self.hurting:
            if self.side == 'blue':
                self.vel.x = PUNCH_REPEL_X
            else:
                self.vel.x = -PUNCH_REPEL_X
        # 衝刺動作
        if self.sprinting:
            if self.side == 'red':
                self.vel.x = SPRINT_SPEED
            else:
                self.vel.x = -SPRINT_SPEED
        # 暈眩值判定及動作
        if self.dizzy_num >= 9:
            friction = BOXER_FRICTION_DIZZY_2
        elif self.dizzy_num >= 5:
            friction = BOXER_FRICTION_DIZZY_1
        # 摩擦力
        self.acc.x += self.vel.x * friction
        # Equation of motion
        self.vel += self.acc
        # 防止x軸速度永遠不為零
        if abs(self.vel.x) < 0.6:
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
    
    def events(self):
        # Key events
        keys = pg.key.get_pressed()
        if self.side == 'red':
            if keys[pg.K_h] and not self.sprinting:
                self.charging = True
            else:
                self.charging = False
                self.charge_point = 0
            if keys[pg.K_a]:
                self.acc.x = -1 * BOXER_ACC
            if keys[pg.K_d]:
                self.acc.x = BOXER_ACC
            if keys[pg.K_f]:
                self.punching = True
            else:
                self.punching = False
            if keys[pg.K_g]:
                self.punching_up = True
            else:
                self.punching_up = False
        elif self.side == 'blue':
            if keys[pg.K_SLASH] and not self.sprinting:
                self.charging = True
            else:
                self.charging = False
                self.charge_point = 0
            if keys[pg.K_LEFT]:
                self.acc.x = -1 * BOXER_ACC
            if keys[pg.K_RIGHT]:
                self.acc.x = BOXER_ACC
            if keys[pg.K_COMMA]:
                self.punching = True
            else:
                self.punching = False
            if keys[pg.K_PERIOD]:
                self.punching_up = True
            else:
                self.punching_up = False

    def animate(self):
        # 角色所有動畫
        now = pg.time.get_ticks()

        # 走路判斷
        if self.vel.x != 0 and not self.sprinting:
            self.walking = True
        else:
            self.walking = False

        # Sprint animation
        if self.sprinting:
            self.action_unstoppable('Punch', 20)
        # KO animation
        elif self.KOing:
            self.action_unstoppable('KO', 50)    
        # Hurt animation
        elif self.hurting:
            self.action_unstoppable('Hurt', 50)
        # Dizzy animation
        elif self.dizzying:
            self.action_unstoppable('Dizzy', 150)
        # Walking animation
        elif self.walking:
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
        
        self.mask = pg.mask.from_surface(self.image)

    def action(self, kind, rate):
        now = pg.time.get_ticks()
        if now - self.last_update > rate:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.action_frames[kind])
            bottom = self.rect.bottom
            self.image = self.action_frames[kind][self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom
    
    def action_unstoppable(self, kind, rate):
        now = pg.time.get_ticks()
        if now - self.last_update > rate:
            if self.unstoppable_count >= len(self.action_frames[kind]):
                if kind == 'Hurt':
                    self.hurting = False
                elif kind == 'Dizzy':
                    self.dizzying = False
                elif kind == 'KO':
                    self.KOing = False
                    self.game.playing = False
                elif kind == 'Punch':
                    self.sprinting_punching_count += 1
                    if self.sprinting_punching_count == 2:
                        self.sprinting = False
                        self.sprinting_punching_count = 0
                self.unstoppable_count = 0
                return
            self.last_update = now
            bottom = self.rect.bottom
            self.image = self.action_frames[kind][self.unstoppable_count]
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom
            self.unstoppable_count += 1