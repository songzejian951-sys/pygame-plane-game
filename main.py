import pygame as pg
import random
import sys
import os


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

SIZE=(800,600)
pg.init()

def get_chinese_font(size):
    paths=["C:/Windows/Fonts/msyh.ttc","C:/Windows/Fonts/msyhbd.ttc","C:/Windows/Fonts/simhei.ttf","C:/Windows/Fonts/simsun.ttc"]
    for path in paths:
        try:
            return pg.font.Font(path,size)
        except:
            pass
    return pg.font.SysFont("microsoftyahei",size)


class Button:
    def __init__(self,text,x,y,width,height,font,normal_color=(40,50,80),hover_color=(70,100,160)):
        self.text=text
        self.rect=pg.Rect(x,y,width,height)
        self.font=font
        self.normal_color=normal_color
        self.hover_color=hover_color
        self.hovered=False

    def update(self):
        self.hovered=self.rect.collidepoint(pg.mouse.get_pos())

    def draw(self,window):
        self.update()
        color=self.hover_color if self.hovered else self.normal_color
        pg.draw.rect(window,color,self.rect,border_radius=12)
        pg.draw.rect(window,(150,180,220),self.rect,2,border_radius=12)
        text=self.font.render(self.text,True,(255,255,255))
        window.blit(text,text.get_rect(center=self.rect.center))

    def is_clicked(self,event):
        return event.type==pg.MOUSEBUTTONDOWN and event.button==1 and self.rect.collidepoint(event.pos)

class BaseSprite(pg.sprite.Sprite):
    def __init__(self,image_path):
        super().__init__()
        self.image=pg.image.load(image_path).convert_alpha()
        self.rect=self.image.get_rect()



class Update_Image_Mixin:
    def __init__(self,image_paths,size=(50,50)):
        self.size=size
        self.image_paths=image_paths
        self.images=[]
        self.contral_size()
        self.index=0

    def updateskin(self):
        self.index+=1
        if self.index>=len(self.images)*10:
            self.index=0
        self.image=self.images[self.index//10]

    def contral_size(self):
        for path in self.image_paths:
            image=pg.image.load(path).convert_alpha()
            image=pg.transform.scale(image,self.size)
            self.images.append(image)



class ExplosionSprite(pg.sprite.Sprite,Update_Image_Mixin):
    def __init__(self,x,y,size=(60,60)):
        pg.sprite.Sprite.__init__(self)
        Update_Image_Mixin.__init__(self,[resource_path('lol/enemy1_down3.png'),resource_path('lol/enemy1_down4.png')],size)
        self.image=self.images[0]
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)
        self.index=0

    def update(self):
        self.index+=1
        if self.index>=len(self.images)*5:
            self.kill()
            return
        self.image=self.images[self.index//5]



class ExplosionManager:
    def __init__(self,gm):
        self.gm=gm
        self.explosions=pg.sprite.Group()

    def add(self,x,y):
        explosion=ExplosionSprite(x,y)
        explosion.add(self.explosions)

    def draw_update(self):
        self.explosions.update()
        self.explosions.draw(self.gm.window)



class BackgroundSprite(BaseSprite):
    def __init__(self,image_path,top=0):
        super().__init__(image_path)
        self.rect.top=top
        self.height=self.rect.height

    def update(self,speed=1):
        self.rect.top+=speed
        if self.rect.top>=SIZE[1]:
            self.rect.bottom=0

class BackgroundManager:
    def __init__(self,gm):
        self.gm=gm
        self.Backgrounds=pg.sprite.Group()
        background1=BackgroundSprite(resource_path('lol/ChatGPT Image 2026年8月10日 21_19_09.png'))
        background1.add(self.Backgrounds)
        background2=BackgroundSprite(
            resource_path('lol/ChatGPT Image 2026年8月10日 21_19_09.png'),
            top=-int(background1.height)
        )
        background2.add(self.Backgrounds)

    def draw_update(self):
        self.Backgrounds.update()
        self.Backgrounds.draw(self.gm.window)

class EnemySprite(BaseSprite):
    def __init__(self,speed=4):
        super().__init__(resource_path("lol/ChatGPT Image 2026年8月11日 20_08_28.png"))
        self.speed=speed
        self.image=pg.transform.scale(self.image,(30,30))
        self.rect=self.image.get_rect()
        self.rect.x=random.randint(0,int(SIZE[0]-self.rect.width))
        self.rect.bottom=0
        self.shoot_timer=pg.time.get_ticks()
        self.shoot_interval=random.randint(1000,2500)

    def update(self):
        self.rect.y+=self.speed
        if self.rect.top>SIZE[1]:
            self.kill()

class EnemyManager:
    def __init__(self,gm):
        self.gm=gm
        self.enemies=pg.sprite.Group()

    def add(self):
        enemy=EnemySprite()
        enemy.add(self.enemies)

    def draw_update(self):
        self.enemies.update()
        current_time=pg.time.get_ticks()
        for enemy in self.enemies:
            if current_time-enemy.shoot_timer>=enemy.shoot_interval:
                self.gm.EBM.add(enemy)
                enemy.shoot_timer=current_time
                enemy.shoot_interval=random.randint(1000,2500)
        self.enemies.draw(self.gm.window)

class SuperEnemySprite(BaseSprite):
    def __init__(self,speed=5,hp=5):
        super().__init__(resource_path("lol/ChatGPT 1.png"))
        self.hp=hp
        self.max_hp=hp
        self.speed=speed
        self.image=pg.transform.scale(self.image,(80,80))
        self.rect=self.image.get_rect()
        self.rect.x=random.randint(0,int(SIZE[0]-self.rect.width))
        self.rect.bottom=0

    def update(self):
        self.rect.y+=self.speed
        if self.rect.top>SIZE[1]:
            self.kill()

    def hurt(self):
        self.hp-=1
        if self.hp<=0:
            self.kill()
            return True
        return False

    def draw_health(self,window):
        bar_width=self.rect.width
        bar_height=6
        bar_x=self.rect.x
        bar_y=self.rect.top-10
        hp_ratio=self.hp/self.max_hp
        pg.draw.rect(window,(255,0,0),(bar_x,bar_y,bar_width,bar_height))
        pg.draw.rect(window,(0,255,0),(bar_x,bar_y,int(bar_width*hp_ratio),bar_height))

class SuperEnemyManager:
    def __init__(self,gm):
        self.gm=gm
        self.superenemies=pg.sprite.Group()

    def add(self):
        superenemy=SuperEnemySprite()
        superenemy.add(self.superenemies)

    def draw_update(self):
        self.superenemies.update()
        self.superenemies.draw(self.gm.window)
        for superenemy in self.superenemies:
            superenemy.draw_health(self.gm.window)

class PlayerSpirte(BaseSprite,Update_Image_Mixin):
    def __init__(self,speed=5):
        super().__init__(resource_path('lol/ChatGPT Image 2026年8月10日 21_48_06.png'))
        Update_Image_Mixin.__init__(self,[resource_path('lol/ChatGPT Image 2026年8月10日 21_48_06.png'),resource_path('lol/ChatGPT Image 2026年8月13日 10_14_40.png')])
        self.image=self.images[0]
        self.rect=self.image.get_rect()
        self.rect.centerx=SIZE[0]//2
        self.rect.bottom=SIZE[1]-20
        self.speed=speed
        self.hp=3
        self.max_hp=3

    def hurt(self,damage=1):
        self.hp-=damage
        if self.hp<0:
            self.hp=0
        return self.hp<=0

    def update(self):
        self.updateskin()
        keys=pg.key.get_pressed()
        if keys[pg.K_UP]:
            self.rect.y-=self.speed
        if keys[pg.K_DOWN]:
            self.rect.y+=self.speed
        if keys[pg.K_LEFT]:
            self.rect.x-=self.speed
        if keys[pg.K_RIGHT]:
            self.rect.x+=self.speed
        self.rect.x=max(0,min(self.rect.x,SIZE[0]-self.rect.width))
        self.rect.y=max(0,min(self.rect.y,SIZE[1]-self.rect.height))

class PlayerManager:
    def __init__(self,gm):
        self.gm=gm
        self.players=pg.sprite.Group()
        self.player=PlayerSpirte()
        self.player.add(self.players)



    def draw_update(self):
        self.players.update()
        self.players.draw(self.gm.window)


    def draw_health(self):
        player=self.player
        bar_x=10
        bar_y=45
        bar_width=150
        bar_height=15
        hp_ratio=player.hp/player.max_hp
        pg.draw.rect(self.gm.window,(100,0,0),(bar_x,bar_y,bar_width,bar_height))
        pg.draw.rect(self.gm.window,(0,255,0),(bar_x,bar_y,int(bar_width*hp_ratio),bar_height))
        text=self.gm.small_font.render(f"生命值：{player.hp}/{player.max_hp}",True,(255,255,255))
        self.gm.window.blit(text,(10,65))



class BulletSpirte(BaseSprite):
    def __init__(self,image_path,x,y,speed=10):
        super().__init__(image_path)
        self.speed=speed
        self.image=pg.transform.scale(self.image,(10,20))
        self.rect=self.image.get_rect()
        self.rect.centerx=x
        self.rect.bottom=y

    def update(self):
        self.rect.y-=self.speed
        if self.rect.bottom<0:
            self.kill()

class PlayerBulletManage:
    def __init__(self,gm):
        self.gm=gm
        self.bullets=pg.sprite.Group()

    def add(self):
        player=self.gm.pm.player
        bullet=BulletSpirte(
            resource_path("lol/image_303592711933566.png"),
            player.rect.centerx,
            player.rect.y
        )
        bullet.add(self.bullets)

    def draw_update(self):
        self.bullets.update()
        self.bullets.draw(self.gm.window)

class EnemyBulletSprite(BaseSprite):
    def __init__(self,x,y,speed=6):
        super().__init__(resource_path("lol/image_303592711933566.png"))
        self.speed=speed
        self.image=pg.transform.scale(self.image,(10,20))
        self.image=pg.transform.rotate(self.image,180)
        self.rect=self.image.get_rect()
        self.rect.centerx=x
        self.rect.top=y

    def update(self):
        self.rect.y+=self.speed
        if self.rect.top>SIZE[1]:
            self.kill()

class EnemyBulletManager:
    def __init__(self,gm):
        self.gm=gm
        self.bullets=pg.sprite.Group()

    def add(self,enemy):
        bullet=EnemyBulletSprite(
            enemy.rect.centerx,
            enemy.rect.bottom
        )
        bullet.add(self.bullets)

    def draw_update(self):
        self.bullets.update()
        self.bullets.draw(self.gm.window)

class GameManager:
    def __init__(self):
        self.window=pg.display.set_mode(SIZE)
        pg.display.set_caption("飞机大战")
        self.clock=pg.time.Clock()
        self.title_font=get_chinese_font(64)
        self.big_font=get_chinese_font(50)
        self.font=get_chinese_font(32)
        self.small_font=get_chinese_font(22)
        self.game_state="menu"
        self.paused=False
        self.bg_manager=BackgroundManager(self)
        self.pm=PlayerManager(self)
        self.PBM=PlayerBulletManage(self)
        self.EBM=EnemyBulletManager(self)
        self.em=EnemyManager(self)
        self.sem=SuperEnemyManager(self)
        self.explosion_manager=ExplosionManager(self)
        self.enemy_timer=0
        self.score=0
        self.create_menu_buttons()
        self.create_pause_buttons()
        self.create_gameover_buttons()

    def create_menu_buttons(self):
        width=260
        height=60
        x=(SIZE[0]-width)//2
        self.start_button=Button("开始游戏",x,270,width,height,self.font)
        self.help_button=Button("游戏说明",x,350,width,height,self.font)
        self.quit_button=Button("退出游戏",x,430,width,height,self.font)

    def create_pause_buttons(self):
        width=240
        height=55
        x=(SIZE[0]-width)//2
        self.resume_button=Button("继续游戏",x,280,width,height,self.font)
        self.pause_menu_button=Button("返回主菜单",x,350,width,height,self.font)
        self.pause_quit_button=Button("退出游戏",x,420,width,height,self.font)

    def create_gameover_buttons(self):
        width=240
        height=55
        x=(SIZE[0]-width)//2
        self.restart_button=Button("重新开始",x,350,width,height,self.font)
        self.gameover_menu_button=Button("返回主菜单",x,420,width,height,self.font)
        self.gameover_quit_button=Button("退出游戏",x,490,width,height,self.font)

    def draw(self):
        self.bg_manager.draw_update()
        self.pm.draw_update()
        self.PBM.draw_update()
        self.em.draw_update()
        self.sem.draw_update()
        self.EBM.draw_update()
        self.explosion_manager.draw_update()


    def check_event(self):
        for ev in pg.event.get():
            if ev.type==pg.QUIT:
                self.quit_game()

            if self.game_state=="menu":
                if self.start_button.is_clicked(ev):
                    self.start_game()
                elif self.help_button.is_clicked(ev):
                    self.game_state="help"
                elif self.quit_button.is_clicked(ev):
                    self.quit_game()


            elif self.game_state=="help":
                if ev.type==pg.KEYDOWN and ev.key==pg.K_ESCAPE:
                    self.game_state="menu"
                if ev.type==pg.MOUSEBUTTONDOWN and ev.button==1:
                    self.game_state="menu"

            elif self.game_state=="playing":
                if ev.type==pg.KEYDOWN:
                    if ev.key==pg.K_p:
                        self.paused=not self.paused
                    elif ev.key==pg.K_SPACE and not self.paused:
                        self.PBM.add()

                if self.paused:
                    if self.resume_button.is_clicked(ev):
                        self.paused=False
                    elif self.pause_menu_button.is_clicked(ev):
                        self.game_state="menu"
                        self.paused=False
                    elif self.pause_quit_button.is_clicked(ev):
                        self.quit_game()

            elif self.game_state=="gameover":
                if self.restart_button.is_clicked(ev):
                    self.restart_game()
                elif self.gameover_menu_button.is_clicked(ev):
                    self.game_state="menu"
                elif self.gameover_quit_button.is_clicked(ev):
                    self.quit_game()
                if ev.type==pg.KEYDOWN:
                    if ev.key==pg.K_r:
                        self.restart_game()
                    elif ev.key==pg.K_ESCAPE:
                        self.game_state="menu"

    def start_game(self):
        self.game_state="playing"
        self.paused=False
        self.enemy_timer=pg.time.get_ticks()

    def restart_game(self):
        self.pm.players.empty()
        self.PBM.bullets.empty()
        self.EBM.bullets.empty()
        self.em.enemies.empty()
        self.sem.superenemies.empty()
        self.explosion_manager.explosions.empty()
        self.pm.player=PlayerSpirte()
        self.pm.player.add(self.pm.players)
        self.score=0
        self.enemy_timer=pg.time.get_ticks()
        self.paused=False
        self.game_state="playing"


    def check_collision(self):
        r1=pg.sprite.groupcollide(
            self.PBM.bullets,
            self.em.enemies,
            True,
            False
        )
        for bullet,enemies in r1.items():
            for enemy in enemies:
                self.explosion_manager.add(
                    enemy.rect.centerx,
                    enemy.rect.centery
                )
                enemy.kill()
                self.score+=1

        r2=pg.sprite.groupcollide(
            self.PBM.bullets,
            self.sem.superenemies,
            True,
            False
        )
        for bullet,superenemys in r2.items():
            for superenemy in superenemys:
                dead=superenemy.hurt()
                self.score+=1
                if dead:
                    self.explosion_manager.add(
                        superenemy.rect.centerx,
                        superenemy.rect.centery
                    )

        r3=pg.sprite.groupcollide(
            self.pm.players,
            self.em.enemies,
            False,
            True
        )
        for player,enemies in r3.items():
            dead=player.hurt()
            for enemy in enemies:
                self.explosion_manager.add(
                    enemy.rect.centerx,
                    enemy.rect.centery
                )
            if dead:
                self.player_die()

        r4=pg.sprite.groupcollide(
            self.pm.players,
            self.sem.superenemies,
            False,
            True
        )
        for player,superenemys in r4.items():
            dead=player.hurt()
            for superenemy in superenemys:
                self.explosion_manager.add(
                    superenemy.rect.centerx,
                    superenemy.rect.centery
                )
            if dead:
                self.player_die()

        r5=pg.sprite.groupcollide(
            self.pm.players,
            self.EBM.bullets,
            False,
            True
        )
        for player,bullets in r5.items():
            dead=player.hurt(len(bullets))
            if dead:
                self.player_die()

    def player_die(self):
        if self.game_state=="gameover":
            return
        player=self.pm.player
        self.explosion_manager.add(
            player.rect.centerx,
            player.rect.centery
        )
        player.kill()
        self.game_state="gameover"

    def enemy_born_time(self):
        current_time=pg.time.get_ticks()
        if current_time-self.enemy_timer>=1000:
            self.em.add()
            if random.randint(1,5)==1:
                self.sem.add()
            self.enemy_timer=current_time

    def draw_score(self):
        text=self.font.render(
            f"得分：{self.score}",
            True,
            (255,255,255)
        )
        self.window.blit(text,(10,10))

    def draw_menu(self):
        self.window.fill((5,8,30))
        random.seed(10)
        for i in range(100):
            x=random.randint(0,SIZE[0])
            y=random.randint(0,SIZE[1])
            pg.draw.circle(
                self.window,
                (100,100,130),
                (x,y),
                1
            )
        title=self.title_font.render(
            "飞机大战",
            True,
            (255,255,255)
        )
        self.window.blit(
            title,
            title.get_rect(
                center=(SIZE[0]//2,130)
            )
        )
        subtitle=self.small_font.render(
            "PLANET BATTLE",
            True,
            (120,180,255)
        )
        self.window.blit(
            subtitle,
            subtitle.get_rect(
                center=(SIZE[0]//2,200)
            )
        )
        self.start_button.draw(self.window)
        self.help_button.draw(self.window)
        self.quit_button.draw(self.window)

    def draw_help(self):
        self.window.fill((5,8,30))
        title=self.big_font.render(
            "游戏说明",
            True,
            (255,255,255)
        )
        self.window.blit(
            title,
            title.get_rect(
                center=(SIZE[0]//2,100)
            )
        )
        texts=[
            "↑ ↓ ← →    控制飞机移动",
            "空格键       发射子弹",
            "P 键         暂停游戏",
            "",
            "击败敌人可以获得分数",
            "注意躲避敌人和敌人子弹",
            "击败超级敌人可以获得更多分数",
            "",
            "点击鼠标或按 ESC 返回主菜单"
        ]
        y=180
        for text in texts:
            surface=self.small_font.render(
                text,
                True,
                (230,230,230)
            )
            self.window.blit(
                surface,
                surface.get_rect(
                    center=(SIZE[0]//2,y)
                )
            )
            y+=38

    def draw_pause(self):
        overlay=pg.Surface(SIZE,pg.SRCALPHA)
        overlay.fill((0,0,0,180))
        self.window.blit(overlay,(0,0))
        title=self.big_font.render(
            "游戏暂停",
            True,
            (255,255,255)
        )
        self.window.blit(
            title,
            title.get_rect(
                center=(SIZE[0]//2,190)
            )
        )
        self.resume_button.draw(self.window)
        self.pause_menu_button.draw(self.window)
        self.pause_quit_button.draw(self.window)

    def draw_gameover(self):
        overlay=pg.Surface(SIZE,pg.SRCALPHA)
        overlay.fill((0,0,0,200))
        self.window.blit(overlay,(0,0))
        title=self.title_font.render(
            "游戏结束",
            True,
            (255,80,80)
        )
        self.window.blit(
            title,
            title.get_rect(
                center=(SIZE[0]//2,150)
            )
        )
        score_text=self.font.render(
            f"最终得分：{self.score}",
            True,
            (255,255,255)
        )
        self.window.blit(
            score_text,
            score_text.get_rect(
                center=(SIZE[0]//2,250)
            )
        )
        self.restart_button.draw(self.window)
        self.gameover_menu_button.draw(self.window)
        self.gameover_quit_button.draw(self.window)

    def quit_game(self):
        pg.quit()
        sys.exit()

    def run(self):
        while True:
            self.check_event()

            if self.game_state=="menu":
                self.draw_menu()

            elif self.game_state=="help":
                self.draw_help()

            elif self.game_state=="playing":
                if not self.paused:
                    self.enemy_born_time()
                    self.check_collision()
                    self.draw()
                else:
                    self.draw()
                self.draw_score()
                self.pm.draw_health()
                if self.paused:
                    self.draw_pause()

            elif self.game_state=="gameover":
                self.draw_score()
                self.pm.draw_health()
                self.draw_gameover()

            pg.display.flip()
            self.clock.tick(60)

def main():
    game=GameManager()
    game.run()

if __name__=="__main__":
    main()