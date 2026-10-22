import math
import pygame

SCREEN_W = 960
SCREEN_H = 540
FPS = 60
TILE = 40
WORLD_W = 3200
WORLD_H = 760

PLAYER_W = 26
PLAYER_H = 36
PLAYER_SPEED = 250.0
JUMP_SPEED = 660.0
GRAVITY = 1450.0
MAX_FALL = 900.0

BG = (17, 23, 30)
BG_LIGHT = (26, 35, 43)
STEEL = (72, 85, 94)
STEEL_LIGHT = (115, 130, 137)
MINT = (95, 230, 184)
ORANGE = (232, 157, 61)
WHITE = (232, 239, 238)
RED = (228, 76, 72)


PLATFORMS = [
    pygame.Rect(0, 480, 560, 80),
    pygame.Rect(620, 440, 240, 40),
    pygame.Rect(920, 480, 420, 80),
    pygame.Rect(1400, 420, 240, 40),
    pygame.Rect(1700, 480, 360, 80),
    pygame.Rect(2110, 440, 260, 40),
    pygame.Rect(2420, 480, 780, 80),
    pygame.Rect(220, 360, 160, 24),
    pygame.Rect(680, 300, 140, 24),
    pygame.Rect(1030, 340, 160, 24),
    pygame.Rect(1470, 270, 150, 24),
    pygame.Rect(1810, 340, 150, 24),
    pygame.Rect(2180, 290, 150, 24),
    pygame.Rect(2600, 350, 180, 24),
]
HAZARDS = [
    pygame.Rect(430, 462, 90, 18),
    pygame.Rect(1110, 462, 100, 18),
    pygame.Rect(1880, 462, 100, 18),
    pygame.Rect(2730, 462, 110, 18),
]
EXIT_RECT = pygame.Rect(3070, 390, 54, 90)
KEYCARD_POS = (1510, 225)
POWER_POS = (2280, 390)


def draw_level(surface, camera_x, time_s, keycard_collected, power_on):
    surface.fill(BG)
    for x in range(-((camera_x // 2) % 180), surface.get_width(), 180):
        pygame.draw.rect(surface, BG_LIGHT, (x, 90, 18, 360))
        pygame.draw.rect(surface, (34, 45, 52), (x + 25, 160, 95, 290))
        pygame.draw.rect(surface, (39, 51, 58), (x + 35, 185, 75, 10))
    for wx in range(80, WORLD_W, 320):
        sx = wx - camera_x
        if -50 < sx < surface.get_width() + 50:
            pygame.draw.rect(surface, (50, 63, 70), (sx, 35, 70, 12))
            glow = 100 + int(20 * (1 + math.sin(time_s * 3 + wx)))
            pygame.draw.rect(surface, (glow, glow, max(0, glow - 20)), (sx + 25, 47, 20, 4))
    for r in PLATFORMS:
        sr = r.move(-camera_x, 0)
        if sr.right < 0 or sr.left > surface.get_width():
            continue
        pygame.draw.rect(surface, STEEL, sr)
        pygame.draw.rect(surface, STEEL_LIGHT, (sr.x, sr.y, sr.width, 5))
        for bx in range(sr.x + 10, sr.right - 5, 30):
            pygame.draw.line(surface, (56, 67, 75), (bx, sr.y + 8), (bx + 12, sr.bottom - 4), 2)
        pygame.draw.rect(surface, ORANGE, (sr.x, sr.y, sr.width, 4))
    for r in HAZARDS:
        sr = r.move(-camera_x, 0)
        if -120 < sr.x < surface.get_width() + 120:
            pygame.draw.rect(surface, (38, 39, 37), sr)
            for x in range(sr.x, sr.right, 18):
                pygame.draw.polygon(surface, ORANGE, [(x, sr.y), (x + 8, sr.y), (x, sr.bottom)])
    if not keycard_collected:
        x, y = KEYCARD_POS
        sx = x - camera_x
        pygame.draw.rect(surface, MINT, (sx, y, 24, 16), border_radius=3)
        pygame.draw.rect(surface, (20, 50, 45), (sx + 5, y + 4, 5, 8))
        pygame.draw.circle(surface, WHITE, (sx + 18, y + 8), 2)
    sx, sy = POWER_POS[0] - camera_x, POWER_POS[1]
    pygame.draw.rect(surface, (48, 60, 66), (sx, sy, 30, 48), border_radius=3)
    pygame.draw.circle(surface, MINT if power_on else ORANGE, (sx + 15, sy + 14), 7)
    pygame.draw.rect(surface, (120, 135, 140), (sx + 8, sy + 29, 14, 4))
    er = EXIT_RECT.move(-camera_x, 0)
    pygame.draw.rect(surface, (31, 48, 48) if power_on and keycard_collected else (45, 43, 38), er)
    pygame.draw.rect(surface, MINT if power_on and keycard_collected else ORANGE, er, 3)
    for y in range(er.y + 10, er.bottom - 5, 14):
        pygame.draw.line(surface, (72, 100, 92) if power_on else (103, 78, 43),
                         (er.x + 8, y), (er.right - 8, y), 2)
    pygame.draw.line(surface, (48, 61, 68), (0, 560), (surface.get_width(), 560), 2)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_W, PLAYER_H)
        self.x, self.y = float(x), float(y)
        self.vx = self.vy = 0.0
        self.on_ground = False
        self.facing = 1
        self.hp = 5
        self.ammo = 36
        self.invuln = 0.0
        self.shot_cooldown = 0.0
        self.keycard = False
        self.power_on = False
        self.score = 0

    def jump(self):
        if self.on_ground:
            self.vy = -JUMP_SPEED
            self.on_ground = False

    def update(self, dt, platforms):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]:
            self.jump()

        direction = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        self.vx = direction * PLAYER_SPEED
        if direction:
            self.facing = direction
        self.x += self.vx * dt
        self.rect.x = round(self.x)
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vx > 0:
                    self.rect.right = p.left
                elif self.vx < 0:
                    self.rect.left = p.right
                self.x = float(self.rect.x)
        self.vy = min(self.vy + GRAVITY * dt, MAX_FALL)
        self.y += self.vy * dt
        self.rect.y = round(self.y)
        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vy > 0:
                    self.rect.bottom = p.top
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = p.bottom
                self.y = float(self.rect.y)
                self.vy = 0.0
        self.invuln = max(0.0, self.invuln - dt)
        self.shot_cooldown = max(0.0, self.shot_cooldown - dt)

    def hurt(self, amount=1):
        if self.invuln <= 0:
            self.hp -= amount
            self.invuln = 1.0
            self.vy = -250
            return True
        return False

    def draw(self, surface, camera_x):
        r = self.rect.move(-camera_x, 0)
        if self.invuln > 0 and int(self.invuln * 12) % 2 == 0:
            return
        pygame.draw.rect(surface, (35, 51, 55), (r.x + 3, r.y + 4, r.width - 6, r.height - 4))
        pygame.draw.rect(surface, MINT, (r.x + 4, r.y + 10, r.width - 8, 18))
        pygame.draw.rect(surface, (52, 69, 76), (r.x + 2, r.y + 2, r.width - 4, 10))
        visor_x = r.x + (14 if self.facing > 0 else 4)
        pygame.draw.rect(surface, WHITE, (visor_x, r.y + 5, 8, 4))
        pygame.draw.rect(surface, ORANGE, (r.x + 5, r.bottom - 5, 6, 5))
        pygame.draw.rect(surface, ORANGE, (r.right - 11, r.bottom - 5, 6, 5))


class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, 12, 5)
        self.vx = direction * 620
        self.life = 1.3

    def update(self, dt):
        self.rect.x += int(self.vx * dt)
        self.life -= dt

    def draw(self, surface, camera_x):
        r = self.rect.move(-camera_x, 0)
        pygame.draw.rect(surface, (255, 219, 124), r)
        pygame.draw.rect(surface, (255, 247, 207), (r.x, r.y, 5, r.height))


class Drone:
    def __init__(self, x, floor_y, left, right):
        self.rect = pygame.Rect(x, floor_y - 30, 34, 30)
        self.left, self.right = left, right
        self.vx = 75
        self.hp = 3
        self.alive = True
        self.phase = 0.0

    def update(self, dt):
        self.phase += dt
        self.rect.x += int(self.vx * dt)
        if self.rect.left < self.left or self.rect.right > self.right:
            self.vx *= -1
            self.rect.x += int(self.vx * dt * 2)

    def draw(self, surface, camera_x):
        r = self.rect.move(-camera_x, 0)
        pygame.draw.rect(surface, (104, 73, 61), r, border_radius=4)
        pygame.draw.rect(surface, RED, (r.x + 7, r.y + 8, 20, 6))
        pygame.draw.rect(surface, (180, 190, 190), (r.x + 4, r.y + 2, 26, 4))
        pygame.draw.line(surface, ORANGE, (r.centerx, r.bottom), (r.centerx, r.bottom + 5), 2)


class Pickup:
    def __init__(self, x, y, kind):
        self.rect = pygame.Rect(x, y, 22, 22)
        self.kind = kind
        self.t = 0.0

    def update(self, dt):
        self.t += dt

    def draw(self, surface, camera_x):
        r = self.rect.move(-camera_x, int(math.sin(self.t * 4) * 3))
        color = MINT if self.kind == "medkit" else (255, 207, 86)
        pygame.draw.rect(surface, color, r, border_radius=3)
        if self.kind == "medkit":
            pygame.draw.rect(surface, WHITE, (r.centerx - 3, r.y + 4, 6, 14))
            pygame.draw.rect(surface, WHITE, (r.x + 4, r.centery - 3, 14, 6))
        else:
            pygame.draw.rect(surface, (91, 70, 28), (r.x + 4, r.y + 4, 14, 14), 2)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("NESTIMS: INDUSTRIAL ZERO")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 25)
        self.big = pygame.font.Font(None, 58)
        self.small = pygame.font.Font(None, 20)
        self.running = True
        self.state = "menu"
        self.reset()

    def reset(self):
        self.player = Player(80, 390)
        self.bullets = []
        self.drones = [
            Drone(360, 480, 280, 510),
            Drone(1020, 480, 960, 1290),
            Drone(1760, 480, 1730, 2020),
            Drone(2500, 480, 2460, 2740),
        ]
        self.pickups = [
            Pickup(720, 260, "ammo"),
            Pickup(1260, 430, "medkit"),
            Pickup(1860, 300, "ammo"),
            Pickup(2650, 310, "medkit"),
        ]
        self.camera_x = 0
        self.time_s = 0
        self.message = "Найди ключ-карту и запусти питание"
        self.message_timer = 4.0
        self.pause_from = "playing"

    def say(self, text, seconds=2.2):
        self.message = text
        self.message_timer = seconds

    def shoot(self):
        p = self.player
        if p.ammo > 0 and p.shot_cooldown <= 0 and self.state == "playing":
            x = p.rect.right if p.facing > 0 else p.rect.left - 12
            self.bullets.append(Bullet(x, p.rect.y + 17, p.facing))
            p.ammo -= 1
            p.shot_cooldown = 0.24

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == "playing":
                    self.state = "pause"
                elif self.state == "pause":
                    self.state = "playing"
                elif self.state in ("won", "lost"):
                    self.state = "menu"
                else:
                    self.running = False
                return
            if self.state == "menu":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.reset()
                    self.state = "playing"
                elif event.key == pygame.K_q:
                    self.running = False
            elif self.state == "playing":
                if event.key in (pygame.K_j,):
                    self.shoot()
            elif self.state == "pause":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.state = "playing"
                elif event.key == pygame.K_r:
                    self.reset()
                    self.state = "playing"
                elif event.key == pygame.K_m:
                    self.state = "menu"
            elif self.state in ("won", "lost"):
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.reset()
                    self.state = "playing"
                elif event.key == pygame.K_m:
                    self.state = "menu"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == "menu":
                self.reset()
                self.state = "playing"
            elif self.state == "playing":
                self.shoot()
            elif self.state in ("won", "lost"):
                self.reset()
                self.state = "playing"

    def update(self, dt):
        self.time_s += dt
        if self.message_timer > 0:
            self.message_timer -= dt
        if self.state != "playing":
            return
        p = self.player
        p.update(dt, PLATFORMS)
        if p.rect.top > 680:
            self.state = "lost"
            return

        key_rect = pygame.Rect(KEYCARD_POS[0], KEYCARD_POS[1], 24, 16)
        if not p.keycard and p.rect.colliderect(key_rect):
            p.keycard = True
            p.score += 250
            self.say("КЛЮЧ-КАРТА ПОЛУЧЕНА", 3)
        power_rect = pygame.Rect(POWER_POS[0], POWER_POS[1], 30, 48)
        if p.rect.inflate(22, 18).colliderect(power_rect) and not p.power_on:
            p.power_on = True
            p.score += 500
            self.say("ПИТАНИЕ ВОССТАНОВЛЕНО", 3)

        for h in HAZARDS:
            if p.rect.colliderect(h):
                p.hurt()
        for pickup in self.pickups[:]:
            pickup.update(dt)
            if p.rect.colliderect(pickup.rect):
                if pickup.kind == "ammo":
                    p.ammo += 12
                    self.say("+12 ПАТРОНОВ")
                else:
                    p.hp = min(5, p.hp + 2)
                    self.say("+2 ЗДОРОВЬЯ")
                self.pickups.remove(pickup)

        for drone in self.drones:
            if drone.alive:
                drone.update(dt)
                if p.rect.colliderect(drone.rect):
                    p.hurt()

        for bullet in self.bullets[:]:
            bullet.update(dt)
            if bullet.life <= 0 or bullet.rect.left < 0 or bullet.rect.right > WORLD_W:
                self.bullets.remove(bullet)
                continue
            hit = False
            for platform in PLATFORMS:
                if bullet.rect.colliderect(platform):
                    hit = True
                    break
            if not hit:
                for drone in self.drones:
                    if drone.alive and bullet.rect.colliderect(drone.rect):
                        drone.hp -= 1
                        hit = True
                        if drone.hp <= 0:
                            drone.alive = False
                            p.score += 100
                            self.say("+100 ОЧКОВ")
                        break
            if hit and bullet in self.bullets:
                self.bullets.remove(bullet)

        if p.rect.colliderect(EXIT_RECT):
            if p.keycard and p.power_on:
                p.score += 1000
                self.state = "won"
            elif not p.keycard:
                self.say("НУЖНА КЛЮЧ-КАРТА", 1.2)
            else:
                self.say("СНАЧАЛА ВОССТАНОВИ ПИТАНИЕ", 1.2)

        if p.hp <= 0:
            self.state = "lost"

        target = p.rect.centerx - SCREEN_W // 2
        self.camera_x = max(0, min(target, WORLD_W - SCREEN_W))

    def draw_text(self, text, font, color, center, shadow=True):
        image = font.render(text, True, color)
        rect = image.get_rect(center=center)
        if shadow:
            shade = font.render(text, True, (0, 0, 0))
            self.screen.blit(shade, rect.move(2, 2))
        self.screen.blit(image, rect)

    def draw_hud(self):
        p = self.player
        pygame.draw.rect(self.screen, (8, 13, 17), (14, 12, 340, 74), border_radius=6)
        pygame.draw.rect(self.screen, (66, 82, 88), (14, 12, 340, 74), 2, border_radius=6)
        self.screen.blit(self.font.render("HEALTH", True, WHITE), (26, 20))
        for i in range(5):
            col = RED if i < p.hp else (64, 53, 54)
            pygame.draw.rect(self.screen, col, (105 + i * 23, 21, 17, 12), border_radius=2)
        self.screen.blit(self.font.render(f"AMMO  {p.ammo:02}", True, WHITE), (26, 43))
        self.screen.blit(self.font.render(f"SCORE  {p.score:05}", True, MINT), (170, 43))
        card = "YES" if p.keycard else "NO"
        power = "ON" if p.power_on else "OFF"
        self.screen.blit(self.small.render(f"CARD: {card}   POWER: {power}", True, ORANGE), (26, 64))

    def draw_overlay(self, title, subtitle, lines):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((4, 8, 12, 205))
        self.screen.blit(overlay, (0, 0))
        self.draw_text(title, self.big, MINT if title not in ("SYSTEM FAILURE",) else RED,
                       (SCREEN_W // 2, 150))
        self.draw_text(subtitle, self.font, WHITE, (SCREEN_W // 2, 205))
        for i, line in enumerate(lines):
            self.draw_text(line, self.font, ORANGE if i == 0 else WHITE,
                           (SCREEN_W // 2, 280 + i * 34), shadow=False)

    def draw(self):
        draw_level(self.screen, self.camera_x, self.time_s,
                   self.player.keycard, self.player.power_on)
        if self.state != "menu":
            for pickup in self.pickups:
                pickup.draw(self.screen, self.camera_x)
            for drone in self.drones:
                if drone.alive:
                    drone.draw(self.screen, self.camera_x)
            for bullet in self.bullets:
                bullet.draw(self.screen, self.camera_x)
            self.player.draw(self.screen, self.camera_x)
            self.draw_hud()
            if self.message_timer > 0 and self.state == "playing":
                pygame.draw.rect(self.screen, (8, 13, 17), (SCREEN_W // 2 - 230, 96, 460, 34), border_radius=5)
                self.draw_text(self.message, self.font, MINT, (SCREEN_W // 2, 113), shadow=False)

        if self.state == "menu":
            self.draw_overlay("INDUSTRIAL ZERO", "NESTIMS ORIGINAL // RETRO PLATFORMER", [
                "ENTER / CLICK – START MISSION",
                "A/D OR ARROWS – MOVE     SPACE – JUMP",
                "J / LEFT CLICK – FIRE     ESC – QUIT",
                "OBJECTIVE: FIND CARD, RESTORE POWER, REACH EXIT",
            ])
        elif self.state == "pause":
            self.draw_overlay("PAUSED", "MISSION SUSPENDED", [
                "ENTER / SPACE – RESUME",
                "R – RESTART MISSION",
                "M – MAIN MENU",
            ])
        elif self.state == "won":
            self.draw_overlay("MISSION COMPLETE", f"FINAL SCORE: {self.player.score}", [
                "THE FACILITY IS SECURED",
                "ENTER / CLICK – PLAY AGAIN",
                "M – MAIN MENU",
            ])
        elif self.state == "lost":
            self.draw_overlay("SYSTEM FAILURE", "MISSION FAILED", [
                f"FINAL SCORE: {self.player.score}",
                "ENTER / CLICK – RETRY",
                "M – MAIN MENU",
            ])
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 1 / 30)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    Game().run() 
