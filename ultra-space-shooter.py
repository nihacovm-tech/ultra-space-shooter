import pygame
import random
import math
import sys

pygame.init()

WIDTH, HEIGHT = 480, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ULTRA Space Shooter")

clock = pygame.time.Clock()

WHITE=(255,255,255)
RED=(255,70,70)
BLUE=(70,150,255)
CYAN=(0,255,255)
YELLOW=(255,220,0)
GREEN=(0,200,120)
GRAY=(120,120,120)
BLACK=(5,5,20)
ORANGE=(255,140,0)
PURPLE=(170,0,170)

font_big=pygame.font.SysFont("Arial",40)
font=pygame.font.SysFont("Arial",22)

# ---------- НАСТРОЙКИ ----------
settings = {
    "button_size": 70,
    "auto_fire": False
}

# ---------- САМОЛЁТЫ ----------
planes = [
    {"name": "Standard", "speed": 0, "damage": 0, "fire": 0},
    {"name": "Falcon", "speed": 2, "damage": 0, "fire": 1},
    {"name": "Destroyer", "speed": 0, "damage": 2, "fire": 0},
    {"name": "Rapid X", "speed": 0, "damage": 0, "fire": 3},
    {"name": "Legend", "speed": 3, "damage": 2, "fire": 2}
]

# ---------- ДАННЫЕ ИГРОКА ----------
player_data = {
    "money": 0,
    "speed_level": 1,
    "damage_level": 1,
    "fire_rate_level": 1,
    "current_plane": 0
}

# ---------- ФОН ----------
stars=[[random.randint(0,WIDTH),random.randint(0,HEIGHT),random.randint(1,3)] for _ in range(80)]

def draw_background(offset):
    screen.fill(BLACK)
    for s in stars:
        pygame.draw.circle(screen,(200,200,200),(s[0]+offset,s[1]),s[2])
        s[1]+=s[2]
        if s[1]>HEIGHT:
            s[1]=0
            s[0]=random.randint(0,WIDTH)

# ---------- КЛАССЫ ----------

class Particle:
    def __init__(self,x,y,color):
        self.x=x; self.y=y
        self.dx=random.uniform(-3,3)
        self.dy=random.uniform(-3,3)
        self.life=40
        self.color=color

    def update(self):
        self.x+=self.dx
        self.y+=self.dy
        self.life-=1

    def draw(self,offset):
        if self.life>0:
            pygame.draw.circle(screen,self.color,
                               (int(self.x+offset),int(self.y)),3)

class Player:
    def __init__(self):
        plane = planes[player_data["current_plane"]]
        self.rect=pygame.Rect(WIDTH//2,HEIGHT-120,50,60)
        self.speed=6 + player_data["speed_level"]*1.5 + plane["speed"]
        self.cooldown=0
        self.anim=0

    def update(self,left,right):
        self.anim+=0.3
        if left: self.rect.x-=self.speed
        if right: self.rect.x+=self.speed
        self.rect.clamp_ip(screen.get_rect())
        if self.cooldown>0: self.cooldown-=1

    def draw(self,offset):
        glow=abs(math.sin(self.anim))*6

        pygame.draw.circle(screen,CYAN,
                           (self.rect.centerx+offset,self.rect.centery),
                           int(30+glow),2)

        pygame.draw.polygon(screen,BLUE,
                            [(self.rect.centerx+offset,self.rect.top),
                             (self.rect.right+offset,self.rect.bottom),
                             (self.rect.centerx+offset,self.rect.bottom-10),
                             (self.rect.left+offset,self.rect.bottom)])

        flame=10+abs(math.sin(self.anim))*6
        pygame.draw.circle(screen,YELLOW,
                           (self.rect.centerx+offset,self.rect.bottom),
                           int(flame))

class Bullet:
    def __init__(self,x,y,laser=False):
        self.rect=pygame.Rect(x,y,6 if laser else 4,18)
        self.speed=-12
        self.laser=laser

    def update(self):
        self.rect.y+=self.speed

    def draw(self,offset):
        color=CYAN if self.laser else YELLOW
        pygame.draw.rect(screen,color,
                         (self.rect.x+offset,self.rect.y,
                          self.rect.width,self.rect.height))

class Enemy:
    def __init__(self):
        self.rect=pygame.Rect(random.randint(30,WIDTH-30),-60,40,40)
        self.speed=random.uniform(2.5,4.5)
        self.hp=2

    def update(self):
        self.rect.y+=self.speed
        self.rect.x+=math.sin(self.rect.y*0.05)*2

    def draw(self,offset):
        pygame.draw.rect(screen,RED,
                         (self.rect.x+offset,self.rect.y,
                          self.rect.width,self.rect.height),
                         border_radius=8)

# ---------- ИГРА ----------

def game():

    player=Player()
    bullets=[]
    enemies=[]
    particles=[]
    score=0
    spawn=0
    shake=0
    player_alive=True
    explosion_timer=60

    size=settings["button_size"]
    left_btn=pygame.Rect(20,HEIGHT-100,size,size)
    right_btn=pygame.Rect(120,HEIGHT-100,size,size)
    fire_btn=pygame.Rect(WIDTH-100,HEIGHT-100,size,size)

    left=False; right=False; firing=False

    running=True
    while running:
        clock.tick(60)

        offset=random.randint(-shake,shake) if shake>0 else 0
        if shake>0: shake-=1

        draw_background(offset)

        if player_alive:
            spawn+=1
            if spawn>40:
                enemies.append(Enemy())
                spawn=0

        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); sys.exit()

            if e.type==pygame.MOUSEBUTTONDOWN:
                if left_btn.collidepoint(e.pos): left=True
                if right_btn.collidepoint(e.pos): right=True
                if fire_btn.collidepoint(e.pos): firing=True

            if e.type==pygame.MOUSEBUTTONUP:
                left=False; right=False; firing=False

        if player_alive and (firing or settings["auto_fire"]) and player.cooldown==0:
            laser=random.random()<0.2
            bullets.append(Bullet(player.rect.centerx,player.rect.top,laser))
            plane = planes[player_data["current_plane"]]
            player.cooldown=max(2,8-(player_data["fire_rate_level"]+plane["fire"]))

        if player_alive:
            player.update(left,right)

        for b in bullets[:]:
            b.update()
            if b.rect.y<0: bullets.remove(b)

        for enemy in enemies[:]:
            enemy.update()

            if player_alive and enemy.rect.colliderect(player.rect):
                player_alive=False
                shake=20
                for _ in range(60):
                    particles.append(Particle(player.rect.centerx,
                                              player.rect.centery,
                                              random.choice([YELLOW,ORANGE,RED])))
                enemies.remove(enemy)

            if enemy.rect.top>HEIGHT:
                enemies.remove(enemy)

            for b in bullets[:]:
                if enemy.rect.colliderect(b.rect):
                    base_damage=2 if b.laser else 1
                    plane = planes[player_data["current_plane"]]
                    enemy.hp-=base_damage*(player_data["damage_level"]+plane["damage"])
                    if b in bullets: bullets.remove(b)
                    if enemy.hp<=0:
                        shake=8
                        score+=10
                        player_data["money"]+=5
                        for _ in range(15):
                            particles.append(Particle(enemy.rect.centerx,
                                                      enemy.rect.centery,
                                                      YELLOW))
                        enemies.remove(enemy)

        for p in particles[:]:
            p.update()
            if p.life<=0: particles.remove(p)

        if player_alive:
            player.draw(offset)

        for b in bullets: b.draw(offset)
        for enemy in enemies: enemy.draw(offset)
        for p in particles: p.draw(offset)

        pygame.draw.rect(screen,GRAY,left_btn,border_radius=20)
        pygame.draw.rect(screen,GRAY,right_btn,border_radius=20)
        pygame.draw.rect(screen,GREEN,fire_btn,border_radius=20)

        screen.blit(font.render("◀",True,WHITE),(left_btn.x+20,left_btn.y+15))
        screen.blit(font.render("▶",True,WHITE),(right_btn.x+20,right_btn.y+15))
        screen.blit(font.render("FIRE",True,WHITE),(fire_btn.x+5,fire_btn.y+20))

        screen.blit(font.render(f"Score: {score}",True,YELLOW),(10,10))
        screen.blit(font.render(f"Money: {player_data['money']}",True,GREEN),(10,40))
        screen.blit(font.render(f"Plane: {planes[player_data['current_plane']]['name']}",True,CYAN),(10,70))

        pygame.display.update()

        if not player_alive:
            explosion_timer-=1
            if explosion_timer<=0:
                running=False

    return score

# ---------- МАГАЗИН ----------

def shop_menu():
    while True:
        screen.fill((10,10,30))

        speed_btn=pygame.Rect(100,250,280,60)
        damage_btn=pygame.Rect(100,330,280,60)
        fire_btn=pygame.Rect(100,410,280,60)
        back_btn=pygame.Rect(150,520,200,60)

        screen.blit(font_big.render("SHOP",True,YELLOW),(170,150))
        screen.blit(font.render(f"Money: {player_data['money']}",True,WHITE),(170,200))

        pygame.draw.rect(screen,BLUE,speed_btn,border_radius=20)
        pygame.draw.rect(screen,RED,damage_btn,border_radius=20)
        pygame.draw.rect(screen,GREEN,fire_btn,border_radius=20)
        pygame.draw.rect(screen,GRAY,back_btn,border_radius=20)

        screen.blit(font.render(f"Speed Lv {player_data['speed_level']} (20$)",True,WHITE),(130,270))
        screen.blit(font.render(f"Damage Lv {player_data['damage_level']} (30$)",True,WHITE),(130,350))
        screen.blit(font.render(f"Fire Rate Lv {player_data['fire_rate_level']} (25$)",True,WHITE),(120,430))
        screen.blit(font.render("BACK",True,WHITE),(210,540))

        pygame.display.update()

        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                if speed_btn.collidepoint(e.pos) and player_data["money"]>=20:
                    player_data["money"]-=20
                    player_data["speed_level"]+=1
                if damage_btn.collidepoint(e.pos) and player_data["money"]>=30:
                    player_data["money"]-=30
                    player_data["damage_level"]+=1
                if fire_btn.collidepoint(e.pos) and player_data["money"]>=25:
                    player_data["money"]-=25
                    player_data["fire_rate_level"]+=1
                if back_btn.collidepoint(e.pos):
                    return

# ---------- НАСТРОЙКИ ----------

def settings_menu():
    while True:
        screen.fill((15,15,40))

        auto_btn = pygame.Rect(120,250,240,60)
        size_up = pygame.Rect(120,330,240,60)
        size_down = pygame.Rect(120,410,240,60)
        back_btn = pygame.Rect(150,520,200,60)

        screen.blit(font_big.render("SETTINGS",True,YELLOW),(130,150))

        pygame.draw.rect(screen,GREEN,auto_btn,border_radius=20)
        pygame.draw.rect(screen,BLUE,size_up,border_radius=20)
        pygame.draw.rect(screen,BLUE,size_down,border_radius=20)
        pygame.draw.rect(screen,GRAY,back_btn,border_radius=20)

        auto_text = "Auto Fire: ON" if settings["auto_fire"] else "Auto Fire: OFF"

        screen.blit(font.render(auto_text,True,WHITE),(160,270))
        screen.blit(font.render("Button Size +",True,WHITE),(170,350))
        screen.blit(font.render("Button Size -",True,WHITE),(170,430))
        screen.blit(font.render("BACK",True,WHITE),(210,540))

        pygame.display.update()

        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                if auto_btn.collidepoint(e.pos):
                    settings["auto_fire"] = not settings["auto_fire"]
                if size_up.collidepoint(e.pos):
                    settings["button_size"] += 10
                if size_down.collidepoint(e.pos) and settings["button_size"] > 40:
                    settings["button_size"] -= 10
                if back_btn.collidepoint(e.pos):
                    return

# ---------- РУЛЕТКА ----------

def roulette_menu():
    if player_data["money"] < 50:
        return

    player_data["money"] -= 50
    spin_time = 120
    selected = 0

    while spin_time > 0:
        screen.fill((10,10,30))
        selected = random.randint(0, len(planes)-1)

        screen.blit(font_big.render("ROULETTE",True,YELLOW),(130,150))
        screen.blit(font_big.render(planes[selected]["name"],True,CYAN),(120,300))

        pygame.display.update()
        pygame.time.delay(50)
        spin_time -= 5

    player_data["current_plane"] = selected

# ---------- GAME OVER ----------

def game_over(score):
    while True:
        screen.fill(BLACK)

        restart_btn=pygame.Rect(140,300,200,60)
        shop_btn=pygame.Rect(140,380,200,60)
        settings_btn=pygame.Rect(140,460,200,60)
        roulette_btn=pygame.Rect(140,540,200,60)
        exit_btn=pygame.Rect(140,620,200,60)

        screen.blit(font_big.render("GAME OVER",True,RED),(100,200))
        screen.blit(font.render(f"Score: {score}",True,WHITE),(180,250))

        pygame.draw.rect(screen,GREEN,restart_btn,border_radius=20)
        pygame.draw.rect(screen,(200,140,0),shop_btn,border_radius=20)
        pygame.draw.rect(screen,BLUE,settings_btn,border_radius=20)
        pygame.draw.rect(screen,PURPLE,roulette_btn,border_radius=20)
        pygame.draw.rect(screen,GRAY,exit_btn,border_radius=20)

        screen.blit(font.render("RESTART",True,WHITE),(170,320))
        screen.blit(font.render("SHOP",True,WHITE),(200,400))
        screen.blit(font.render("SETTINGS",True,WHITE),(170,480))
        screen.blit(font.render("ROULETTE (50$)",True,WHITE),(150,560))
        screen.blit(font.render("EXIT",True,WHITE),(200,640))

        pygame.display.update()

        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                if restart_btn.collidepoint(e.pos):
                    return
                if shop_btn.collidepoint(e.pos):
                    shop_menu()
                if settings_btn.collidepoint(e.pos):
                    settings_menu()
                if roulette_btn.collidepoint(e.pos):
                    roulette_menu()
                if exit_btn.collidepoint(e.pos):
                    pygame.quit(); sys.exit()

# ---------- ЗАПУСК ----------

while True:
    score=game()
    game_over(score)