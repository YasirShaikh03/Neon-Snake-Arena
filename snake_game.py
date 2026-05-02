import pygame
import random
import sys
import math

# ── Constants ──────────────────────────────────────────────────────────────────
WIDTH, HEIGHT   = 700, 750
GRID_COLS       = 25
GRID_ROWS       = 25
CELL            = 24
BOARD_W         = GRID_COLS * CELL      # 600
BOARD_H         = GRID_ROWS * CELL      # 600
BOARD_X         = (WIDTH - BOARD_W) // 2
BOARD_Y         = HEIGHT - BOARD_H - 20

# Colors
BG              = (10,  12,  18)
BOARD_BG        = (14,  17,  24)
GRID_LINE       = (22,  26,  36)
SNAKE_HEAD      = (80,  220, 120)
SNAKE_BODY      = (50,  180,  90)
SNAKE_TAIL      = (30,  140,  65)
FOOD_COLOR      = (255,  80,  80)
FOOD_GLOW       = (255, 120, 100)
GOLDEN_FOOD     = (255, 210,  50)
WALL_COLOR      = (40,   45,  60)
TEXT_PRIMARY    = (220, 230, 210)
TEXT_MUTED      = (100, 110,  90)
ACCENT_GREEN    = ( 80, 220, 120)
ACCENT_RED      = (255,  80,  80)
ACCENT_GOLD     = (255, 210,  50)
PANEL_BG        = (16,  20,  28)
BTN_NORMAL      = (28,  34,  46)
BTN_HOVER       = (38,  46,  62)
BTN_ACTIVE      = (50,  100,  60)

# Directions
UP    = ( 0, -1)
DOWN  = ( 0,  1)
LEFT  = (-1,  0)
RIGHT = ( 1,  0)

OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

# Speed per level (ms per tick)
LEVEL_SPEED = {
    1: 160, 2: 140, 3: 120, 4: 100, 5: 85,
    6: 72,  7: 60,  8: 50,  9: 42, 10: 34,
}
LEVEL_LABEL = {
    1:"Baby Snake", 2:"Slow Worm", 3:"Garden Snake", 4:"Racer",    5:"Viper",
    6:"Cobra",      7:"Python",    8:"Anaconda",     9:"Sea Serpent",10:"LEVIATHAN",
}


# ── Utility ────────────────────────────────────────────────────────────────────
def lerp_color(a, b, t):
    return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))


def draw_rounded_rect(surf, color, rect, radius=8, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)


def glow_circle(surf, color, pos, radius, alpha=80):
    s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    pygame.draw.circle(s, (*color, alpha), (radius, radius), radius)
    surf.blit(s, (pos[0]-radius, pos[1]-radius))


# ── Snake ──────────────────────────────────────────────────────────────────────
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        cx, cy = GRID_COLS//2, GRID_ROWS//2
        self.body      = [(cx, cy), (cx-1, cy), (cx-2, cy)]
        self.direction = RIGHT
        self.grow_pending = 0

    def turn(self, new_dir):
        if new_dir != OPPOSITE.get(self.direction):
            self.direction = new_dir

    def move(self):
        hx, hy = self.body[0]
        dx, dy  = self.direction
        new_head = (hx+dx, hy+dy)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount=1):
        self.grow_pending += amount

    def head(self):
        return self.body[0]

    def hits_self(self):
        return self.body[0] in self.body[1:]

    def hits_wall(self):
        hx, hy = self.body[0]
        return not (0 <= hx < GRID_COLS and 0 <= hy < GRID_ROWS)


# ── Food ───────────────────────────────────────────────────────────────────────
class Food:
    def __init__(self, snake_body, walls):
        self.golden      = False
        self.golden_timer= 0
        self.pulse       = 0
        self.spawn(snake_body, walls)

    def spawn(self, snake_body, walls):
        occupied = set(snake_body) | set(walls)
        free = [(x, y) for x in range(GRID_COLS) for y in range(GRID_ROWS)
                if (x, y) not in occupied]
        if free:
            self.pos = random.choice(free)
        self.golden = random.random() < 0.12
        self.golden_timer = 150 if self.golden else 0

    def update(self):
        self.pulse = (self.pulse + 0.12) % (2 * math.pi)
        if self.golden:
            self.golden_timer -= 1
            if self.golden_timer <= 0:
                self.golden = False

    def draw(self, surf, tick):
        px = BOARD_X + self.pos[0]*CELL + CELL//2
        py = BOARD_Y + self.pos[1]*CELL + CELL//2
        r  = CELL//2 - 2
        pulse_r = int(r + 3*math.sin(self.pulse))
        if self.golden:
            glow_circle(surf, GOLDEN_FOOD, (px, py), pulse_r+10, 60)
            pygame.draw.circle(surf, GOLDEN_FOOD, (px, py), pulse_r)
            pygame.draw.circle(surf, (255,240,180), (px-2, py-2), pulse_r//3)
        else:
            glow_circle(surf, FOOD_GLOW, (px, py), pulse_r+8, 55)
            pygame.draw.circle(surf, FOOD_COLOR, (px, py), pulse_r)
            pygame.draw.circle(surf, (255,180,160), (px-2, py-2), pulse_r//3)


# ── Particle ──────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color):
        self.x = x; self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-4, 0)
        self.life = random.randint(20, 40)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(2, 5)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.18
        self.life -= 1

    def draw(self, surf):
        alpha = int(255 * self.life / self.max_life)
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        surf.blit(s, (int(self.x)-self.size, int(self.y)-self.size))


# ── Game ───────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, level=1, walls_on=False):
        self.level     = level
        self.walls_on  = walls_on
        self.walls     = self._make_walls() if walls_on else []
        self.snake     = Snake()
        self.food      = Food(self.snake.body, self.walls)
        self.score     = 0
        self.high_score= 0
        self.tick_ms   = LEVEL_SPEED[level]
        self.last_tick = pygame.time.get_ticks()
        self.particles = []
        self.game_over = False
        self.paused    = False
        self.flash     = 0
        self.score_pop = []   # (value, x, y, timer)
        self.combo     = 0
        self.combo_timer=0

    def _make_walls(self):
        walls = []
        # Border pillars
        for i in range(0, GRID_COLS, 4):
            walls += [(i, 0), (i, GRID_ROWS-1)]
        for j in range(0, GRID_ROWS, 4):
            walls += [(0, j), (GRID_COLS-1, j)]
        # Inner obstacles (avoid center)
        centers = [(6,6),(18,6),(6,18),(18,18)]
        for cx,cy in centers:
            for dx in range(-1,2):
                for dy in range(-1,2):
                    nx,ny=cx+dx,cy+dy
                    if 0<nx<GRID_COLS-1 and 0<ny<GRID_ROWS-1:
                        walls.append((nx,ny))
        # Remove duplicates and center region
        snake_safe = {(GRID_COLS//2+i, GRID_ROWS//2) for i in range(-3,4)}
        return list(set(walls)-snake_safe)

    def handle_key(self, key):
        if key == pygame.K_UP    or key == pygame.K_w: self.snake.turn(UP)
        if key == pygame.K_DOWN  or key == pygame.K_s: self.snake.turn(DOWN)
        if key == pygame.K_LEFT  or key == pygame.K_a: self.snake.turn(LEFT)
        if key == pygame.K_RIGHT or key == pygame.K_d: self.snake.turn(RIGHT)
        if key == pygame.K_p or key == pygame.K_ESCAPE:
            self.paused = not self.paused

    def update(self):
        if self.game_over or self.paused: return
        now = pygame.time.get_ticks()
        if now - self.last_tick < self.tick_ms: return
        self.last_tick = now

        self.food.update()
        self.snake.move()

        # Collision checks
        if self.snake.hits_wall() or self.snake.hits_self() or \
           self.snake.head() in self.walls:
            self.game_over = True
            self.flash = 12
            # Burst particles
            hx = BOARD_X + self.snake.head()[0]*CELL + CELL//2
            hy = BOARD_Y + self.snake.head()[1]*CELL + CELL//2
            for _ in range(30):
                self.particles.append(Particle(hx, hy, ACCENT_RED))
            return

        # Eat food
        if self.snake.head() == self.food.pos:
            pts = 30 if self.food.golden else 10
            self.combo_timer = 60
            self.combo += 1
            bonus = pts * min(self.combo, 5)
            self.score += bonus + self.level * 2
            self.high_score = max(self.high_score, self.score)
            grow = 3 if self.food.golden else 1
            self.snake.grow(grow)
            fx = BOARD_X + self.food.pos[0]*CELL + CELL//2
            fy = BOARD_Y + self.food.pos[1]*CELL + CELL//2
            col = GOLDEN_FOOD if self.food.golden else FOOD_COLOR
            for _ in range(16):
                self.particles.append(Particle(fx, fy, col))
            self.score_pop.append([f"+{bonus}", fx, fy, 40, col])
            self.food.spawn(self.snake.body, self.walls)

        # Combo decay
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

        # Update particles
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles: p.update()
        self.score_pop = [s for s in self.score_pop if s[3] > 0]
        for s in self.score_pop: s[2] -= 1; s[3] -= 1
        if self.flash > 0: self.flash -= 1

    def draw(self, surf, fonts):
        mfont, tfont, bfont, smfont = fonts

        # Flash overlay on death
        if self.flash > 0:
            alpha = int(180 * self.flash / 12)
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((220, 40, 40, alpha))
            surf.blit(ov, (0, 0))

        # Board background
        pygame.draw.rect(surf, BOARD_BG, (BOARD_X, BOARD_Y, BOARD_W, BOARD_H))

        # Grid lines
        for x in range(GRID_COLS+1):
            pygame.draw.line(surf, GRID_LINE,
                (BOARD_X+x*CELL, BOARD_Y), (BOARD_X+x*CELL, BOARD_Y+BOARD_H))
        for y in range(GRID_ROWS+1):
            pygame.draw.line(surf, GRID_LINE,
                (BOARD_X, BOARD_Y+y*CELL), (BOARD_X+BOARD_W, BOARD_Y+y*CELL))

        # Walls
        for wx, wy in self.walls:
            pygame.draw.rect(surf, WALL_COLOR,
                (BOARD_X+wx*CELL+1, BOARD_Y+wy*CELL+1, CELL-2, CELL-2), border_radius=3)

        # Board border
        pygame.draw.rect(surf, (40,50,40), (BOARD_X-2,BOARD_Y-2,BOARD_W+4,BOARD_H+4), 2, border_radius=4)

        # Snake
        n = len(self.snake.body)
        for i, (bx, by) in enumerate(self.snake.body):
            px = BOARD_X + bx*CELL + 1
            py = BOARD_Y + by*CELL + 1
            sz = CELL - 2
            t  = i / max(n-1, 1)
            if i == 0:
                col = SNAKE_HEAD
                # glow
                glow_circle(surf, SNAKE_HEAD,
                    (px+sz//2, py+sz//2), sz//2+6, 40)
            else:
                col = lerp_color(SNAKE_BODY, SNAKE_TAIL, t)
            draw_rounded_rect(surf, col, (px, py, sz, sz),
                              radius=5 if i==0 else 3)
            # Eyes on head
            if i == 0:
                dx, dy = self.snake.direction
                ex = px + sz//2 + dx*(sz//3)
                ey = py + sz//2 + dy*(sz//3)
                # perpendicular eye offset
                ox, oy = -dy, dx
                for side in (-1, 1):
                    eox = ex + side*ox*(sz//5)
                    eoy = ey + side*oy*(sz//5)
                    pygame.draw.circle(surf, (10,10,10), (int(eox),int(eoy)), 3)
                    pygame.draw.circle(surf, (255,255,255), (int(eox)-1,int(eoy)-1), 1)

        # Food
        self.food.draw(surf, 0)

        # Particles
        for p in self.particles: p.draw(surf)

        # Score popups
        for txt, fx, fy, timer, col in self.score_pop:
            alpha = min(255, timer*8)
            s = smfont.render(txt, True, col)
            sv = pygame.Surface(s.get_size(), pygame.SRCALPHA)
            sv.blit(s, (0,0)); sv.set_alpha(alpha)
            surf.blit(sv, (fx - s.get_width()//2, int(fy - (40-timer)*0.8)))

        # ── HUD (top panel)
        pygame.draw.rect(surf, PANEL_BG, (0, 0, WIDTH, BOARD_Y-4))

        # Score
        sc_lbl = smfont.render("SCORE", True, TEXT_MUTED)
        sc_val = mfont.render(str(self.score), True, ACCENT_GREEN)
        surf.blit(sc_lbl, (BOARD_X, 10))
        surf.blit(sc_val, (BOARD_X, 24))

        # High score
        hs_lbl = smfont.render("BEST", True, TEXT_MUTED)
        hs_val = mfont.render(str(self.high_score), True, ACCENT_GOLD)
        surf.blit(hs_lbl, (WIDTH//2 - hs_val.get_width()//2, 10))
        surf.blit(hs_val, (WIDTH//2 - hs_val.get_width()//2, 24))

        # Level
        lv_lbl = smfont.render("LEVEL", True, TEXT_MUTED)
        lv_val = mfont.render(str(self.level), True, TEXT_PRIMARY)
        surf.blit(lv_lbl, (BOARD_X+BOARD_W - lv_val.get_width(), 10))
        surf.blit(lv_val, (BOARD_X+BOARD_W - lv_val.get_width(), 24))

        # Length
        ln_lbl = smfont.render(f"Length: {len(self.snake.body)}", True, TEXT_MUTED)
        surf.blit(ln_lbl, (BOARD_X, 52))

        # Combo
        if self.combo >= 2:
            ct = mfont.render(f"x{self.combo} COMBO!", True, ACCENT_GOLD)
            surf.blit(ct, (WIDTH//2 - ct.get_width()//2, 48))

        # Pause overlay
        if self.paused:
            ov = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
            ov.fill((0,0,0,140)); surf.blit(ov,(0,0))
            pt = bfont.render("PAUSED", True, TEXT_PRIMARY)
            surf.blit(pt,(WIDTH//2-pt.get_width()//2, HEIGHT//2-pt.get_height()//2))
            ps = smfont.render("Press P to resume", True, TEXT_MUTED)
            surf.blit(ps,(WIDTH//2-ps.get_width()//2, HEIGHT//2+40))


# ── Screens ────────────────────────────────────────────────────────────────────
def menu_screen(surf, fonts, high_score=0):
    mfont, tfont, bfont, smfont = fonts
    clock = pygame.time.Clock()
    level = 1
    walls = False
    tick  = 0

    bar_x = WIDTH//2 - 160
    bar_w = 320

    btn_play = pygame.Rect(WIDTH//2-100, 520, 200, 48)

    while True:
        tick += 1
        surf.fill(BG)
        mx, my = pygame.mouse.get_pos()

        # Animated background dots
        for i in range(20):
            x = (i*137 + tick//2) % WIDTH
            y = (i*97  + tick//3) % HEIGHT
            r = 1 + i%3
            pygame.draw.circle(surf, (25,35,25), (x,y), r)

        # Title
        t = bfont.render("🐍 SNAKE", True, ACCENT_GREEN)
        surf.blit(t,(WIDTH//2-t.get_width()//2, 60))
        if high_score > 0:
            hs = smfont.render(f"Best Score: {high_score}", True, ACCENT_GOLD)
            surf.blit(hs,(WIDTH//2-hs.get_width()//2, 130))

        # Level slider
        dl = tfont.render("Speed / Difficulty", True, TEXT_MUTED)
        surf.blit(dl,(WIDTH//2-dl.get_width()//2, 170))

        bar_y = 200; bar_h = 8
        pygame.draw.rect(surf,(40,40,40),(bar_x,bar_y,bar_w,bar_h),border_radius=4)
        fill_w = int(bar_w*(level-1)/9)
        pygame.draw.rect(surf,ACCENT_GREEN,(bar_x,bar_y,fill_w,bar_h),border_radius=4)
        kx = bar_x+fill_w
        pygame.draw.circle(surf,ACCENT_GREEN,(kx,bar_y+bar_h//2),10)
        pygame.draw.circle(surf,(10,10,10),(kx,bar_y+bar_h//2),5)

        # Level numbers
        step = bar_w/9
        for i in range(1,11):
            nx=int(bar_x+(i-1)*step)
            col2=ACCENT_GREEN if i==level else (60,60,60)
            n=smfont.render(str(i),True,col2)
            surf.blit(n,(nx-n.get_width()//2, bar_y+bar_h+10))

        ll = tfont.render(f"Level {level} — {LEVEL_LABEL[level]}", True, ACCENT_GREEN)
        surf.blit(ll,(WIDTH//2-ll.get_width()//2, bar_y+bar_h+34))

        # Walls toggle
        wlbl = tfont.render("Obstacles:", True, TEXT_MUTED)
        surf.blit(wlbl,(WIDTH//2-120, 310))
        for label, val, ox in [("OFF", False, 30), ("ON", True, 100)]:
            r = pygame.Rect(WIDTH//2+ox, 306, 52, 26)
            active = walls==val
            draw_rounded_rect(surf, BTN_ACTIVE if active else BTN_NORMAL, r, 6,
                              1, ACCENT_GREEN if active else (50,55,50))
            lt = smfont.render(label, True, ACCENT_GREEN if active else TEXT_MUTED)
            surf.blit(lt,(r.centerx-lt.get_width()//2, r.centery-lt.get_height()//2))

        # Controls hint
        ctrl = [
            "Arrow Keys / WASD — Move",
            "P / ESC — Pause",
            "Golden food = +30 pts & grow x3",
            "Combos multiply your score!",
        ]
        for i,c in enumerate(ctrl):
            ct = smfont.render(c, True, TEXT_MUTED)
            surf.blit(ct,(WIDTH//2-ct.get_width()//2, 360+i*22))

        # Play button
        hov = btn_play.collidepoint(mx,my)
        draw_rounded_rect(surf, BTN_HOVER if hov else BTN_NORMAL, btn_play, 10,
                          2, ACCENT_GREEN)
        pt = mfont.render("▶  PLAY", True, ACCENT_GREEN)
        surf.blit(pt,(btn_play.centerx-pt.get_width()//2,
                      btn_play.centery-pt.get_height()//2))

        pygame.display.flip()
        clock.tick(60)

        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit();sys.exit()
            if ev.type==pygame.MOUSEBUTTONDOWN:
                if btn_play.collidepoint(ev.pos): return level, walls
                # Walls toggle
                r_off=pygame.Rect(WIDTH//2+30,306,52,26)
                r_on =pygame.Rect(WIDTH//2+100,306,52,26)
                if r_off.collidepoint(ev.pos): walls=False
                if r_on.collidepoint(ev.pos):  walls=True
                # Slider
                if bar_x<=ev.pos[0]<=bar_x+bar_w and bar_y-14<=ev.pos[1]<=bar_y+30:
                    frac=max(0.0,min(1.0,(ev.pos[0]-bar_x)/bar_w))
                    level=max(1,min(10,round(frac*9)+1))
            if ev.type==pygame.MOUSEMOTION and ev.buttons[0]:
                if bar_x-10<=ev.pos[0]<=bar_x+bar_w+10 and bar_y-20<=ev.pos[1]<=bar_y+40:
                    frac=max(0.0,min(1.0,(ev.pos[0]-bar_x)/bar_w))
                    level=max(1,min(10,round(frac*9)+1))
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_RETURN:
                return level, walls


def game_over_screen(surf, fonts, score, high_score, level):
    mfont, tfont, bfont, smfont = fonts
    clock = pygame.time.Clock()

    btn_retry = pygame.Rect(WIDTH//2-110, 420, 100, 44)
    btn_menu  = pygame.Rect(WIDTH//2+10,  420, 100, 44)

    while True:
        mx,my = pygame.mouse.get_pos()
        surf.fill(BG)

        ov = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        ov.fill((200,20,20,18)); surf.blit(ov,(0,0))

        t = bfont.render("GAME OVER", True, ACCENT_RED)
        surf.blit(t,(WIDTH//2-t.get_width()//2, 140))

        sc = mfont.render(f"Score: {score}", True, TEXT_PRIMARY)
        surf.blit(sc,(WIDTH//2-sc.get_width()//2, 230))

        if score >= high_score:
            hs = mfont.render("🏆 New High Score!", True, ACCENT_GOLD)
            surf.blit(hs,(WIDTH//2-hs.get_width()//2, 270))
        else:
            hs = tfont.render(f"Best: {high_score}", True, ACCENT_GOLD)
            surf.blit(hs,(WIDTH//2-hs.get_width()//2, 270))

        ll = tfont.render(f"Level {level} — {LEVEL_LABEL[level]}", True, TEXT_MUTED)
        surf.blit(ll,(WIDTH//2-ll.get_width()//2, 320))

        for btn,label in [(btn_retry,"↺ Retry"),(btn_menu,"⌂ Menu")]:
            hov=btn.collidepoint(mx,my)
            draw_rounded_rect(surf,BTN_HOVER if hov else BTN_NORMAL,btn,8,1,ACCENT_GREEN)
            lt=smfont.render(label,True,TEXT_PRIMARY)
            surf.blit(lt,(btn.centerx-lt.get_width()//2,btn.centery-lt.get_height()//2))

        pygame.display.flip()
        clock.tick(60)

        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit();sys.exit()
            if ev.type==pygame.MOUSEBUTTONDOWN:
                if btn_retry.collidepoint(ev.pos): return "retry"
                if btn_menu.collidepoint(ev.pos):  return "menu"
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_r: return "retry"
                if ev.key==pygame.K_ESCAPE: return "menu"


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")
    clock  = pygame.time.Clock()

    mfont  = pygame.font.SysFont("segoeui,dejavusans", 26, bold=True)
    tfont  = pygame.font.SysFont("segoeui,dejavusans", 16)
    bfont  = pygame.font.SysFont("segoeui,dejavusans", 42, bold=True)
    smfont = pygame.font.SysFont("segoeui,dejavusans", 13)
    fonts  = (mfont, tfont, bfont, smfont)

    high_score = 0
    state = "menu"
    game  = None
    level, walls = 1, False

    while True:
        if state == "menu":
            level, walls = menu_screen(screen, fonts, high_score)
            game  = Game(level, walls)
            state = "playing"

        elif state == "playing":
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN:
                    game.handle_key(ev.key)

            game.update()
            screen.fill(BG)
            game.draw(screen, fonts)
            pygame.display.flip()
            clock.tick(120)

            if game.game_over:
                high_score = max(high_score, game.score)
                pygame.time.wait(400)
                state = "gameover"

        elif state == "gameover":
            choice = game_over_screen(screen, fonts, game.score, high_score, level)
            if choice == "retry":
                game  = Game(level, walls)
                game.high_score = high_score
                state = "playing"
            else:
                state = "menu"

        clock.tick(60)


if __name__ == "__main__":
    main()
