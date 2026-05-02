import pygame, sys, random, time, json, os
from pygame.locals import *

# ─────────────────────────────────────────────
# Initialize Pygame and its audio mixer
# ─────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

# Target frame rate and clock to enforce it
FPS = 60
FramePerSec = pygame.time.Clock()

# ─────────────────────────────────────────────
# Game window dimensions and display surface
# ─────────────────────────────────────────────
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer Game")

# ─────────────────────────────────────────────
# Color constants (RGB tuples)
# ─────────────────────────────────────────────
WHITE = (255, 255, 255)
BLACK = (0,   0,   0)
RED = (255, 0,   0)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)
GREEN = (0,   200, 0)
BLUE = (50,  150, 255)
GREY = (180, 180, 180)
DARK = (30,  30,  30)
GOLD = (255, 200, 50)

# ─────────────────────────────────────────────
# Font sizes used across all screens and HUD
# ─────────────────────────────────────────────
font_big = pygame.font.SysFont("Verdana", 46)
font_mid = pygame.font.SysFont("Verdana", 26)
font_small = pygame.font.SysFont("Verdana", 17)
font_tiny = pygame.font.SysFont("Verdana", 13)

# ─────────────────────────────────────────────
# Global speed shared by all falling sprites.
# Modified by coin milestones, power-ups and oil spills.
# ─────────────────────────────────────────────
SPEED = 5

# Registry of all active sprite rects, rebuilt every frame.
# Used by find_clear_spawn to avoid placing new sprites on top of existing ones.
occupied_rects = []

# ─────────────────────────────────────────────
# Loads an image file and optionally scales it.
# path  — filename of the image (e.g. "assets/Player.png")
# size  — optional (width, height) tuple to scale to
# ─────────────────────────────────────────────
def load_img(path, size=None):
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

# ─────────────────────────────────────────────
# Load all game images at startup.
# Images are loaded once and reused every frame.
# ─────────────────────────────────────────────
background = load_img("assets/AnimatedStreet.png")
player_img = load_img("assets/Player.png",      (50, 80))
enemy1_img = load_img("assets/Enemy.png",       (50, 80))
enemy2_img = load_img("assets/enemy_2.png",     (85, 200))
obstacle_img = load_img("assets/obstacle.png",    (80, 55))
oil_img_large = load_img("assets/oil_spill.png",  (140, 75))
oil_img_small = load_img("assets/oil_spill.png",  (75,  48))
coin_small_img = load_img("assets/small_coin_icon.png", (16, 16))
coin_large_img = load_img("assets/large_coin_icon.png", (54, 48))
heart_img = load_img("assets/heart_icon.png",  (20, 20))
nitro_img = load_img("assets/nitro_icon.png",  (36, 36))
shield_img = load_img("assets/shield_icon.png", (36, 36))
repair_img = load_img("assets/repair_icon.png", (36, 36))

# Button and UI images — all buttons share the same width/height
BTN_W, BTN_H = 200, 62
btn_play = load_img("assets/Play_icon.png",        (BTN_W, BTN_H))
btn_quit = load_img("assets/Quit_icon.png",        (BTN_W, BTN_H))
btn_leaderboard = load_img("assets/Leaderboard_icon.png", (BTN_W, BTN_H))
btn_retry = load_img("assets/Retry_icon.png",       (BTN_W, BTN_H))
btn_main_menu = load_img("assets/Main_menu_icon.png",   (BTN_W, BTN_H))
img_racer_title = load_img("assets/Racer_icon.png",       (260, 80))
img_podium = load_img("assets/top_three_players.png",(300, 120))
btn_settings = load_img("assets/Settings_icon.png",    (52, 52))

# ─────────────────────────────────────────────
# Load sound effects and background music.
# Music loops indefinitely (-1). If audio fails,
# the game continues silently.
# ─────────────────────────────────────────────
crash_sound = pygame.mixer.Sound("assets/crash.wav")
try:
    pygame.mixer.music.load("assets/background.wav")
    pygame.mixer.music.play(-1)
except:
    pass

# ─────────────────────────────────────────────
# JSON file names for persistent storage
# ─────────────────────────────────────────────
LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE = "settings.json"
PLAYERS_FILE = "players.json"

# Reads a JSON file from disk. Returns default if the file doesn't exist yet.
def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

# Writes a Python object to a JSON file on disk.
def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Load saved data at startup — falls back to defaults on first run
settings = load_json(SETTINGS_FILE,    {"sound": True, "difficulty": "easy"})
leaderboard = load_json(LEADERBOARD_FILE, [])
players_db = load_json(PLAYERS_FILE,     {})

# Saves the player's score after a game ends.
# Keeps only the best distance per player.
# Rebuilds and saves the sorted top-10 leaderboard.
def save_score(username, distance):
    prev = players_db.get(username, {}).get("distance", 0)
    if distance > prev:
        players_db[username] = {"distance": distance}
        save_json(PLAYERS_FILE, players_db)
    leaderboard.clear()
    for name, data in players_db.items():
        # Support old entries that used "score" key instead of "distance"
        dist = data.get("distance", data.get("score", 0))
        leaderboard.append({"name": name, "distance": dist})
    leaderboard.sort(key=lambda e: e["distance"], reverse=True)
    del leaderboard[10:]
    save_json(LEADERBOARD_FILE, leaderboard)

# ─────────────────────────────────────────────
# Difficulty configuration.
# easy — 1 red enemy, slower speed scaling, fewer obstacles
# hard — 2 enemies (red + truck), faster scaling, more obstacles
# ─────────────────────────────────────────────
DIFFICULTY_SETTINGS = {
    "easy": {
        "speed": 4, "coins_per_speedup": 8, "speed_inc": 0.5,
        "enemy_count": 1, "obstacle_interval": 12, "obstacle_interval_min": 8,
    },
    "hard": {
        "speed": 6, "coins_per_speedup": 5, "speed_inc": 1.0,
        "enemy_count": 2, "obstacle_interval": 6,  "obstacle_interval_min": 4,
    },
}

# Returns the difficulty config dictionary based on current settings.
def get_diff():
    return DIFFICULTY_SETTINGS.get(
        settings.get("difficulty", "easy"),
        DIFFICULTY_SETTINGS["easy"]
    )

# Finds a clear spawn position above the screen that doesn't overlap
# any currently active sprite. Tries up to max_tries random positions.
# w, h     — dimensions of the sprite to place
# y_range  — vertical range above the screen to search within
# max_tries — how many attempts before using the fallback position
def find_clear_spawn(w, h, y_range=None, max_tries=30):
    if y_range is None:
        y_range = (-700, -(h + 10))
    y0 = min(y_range[0], y_range[1])
    y1 = max(y_range[0], y_range[1])
    for _ in range(max_tries):
        x = random.randint(40, max(41, SCREEN_WIDTH - 40 - w))
        y = random.randint(y0, y1)
        r = pygame.Rect(x, y, w, h)
        if not any(r.colliderect(o) for o in occupied_rects):
            occupied_rects.append(r)
            return r
    # Fallback — place far above screen if no clear spot found
    r = pygame.Rect(random.randint(40, max(41, SCREEN_WIDTH - 40 - w)), -900, w, h)
    occupied_rects.append(r)
    return r

# ═══════════════════════════════════════════════
# Sprite classes
# ═══════════════════════════════════════════════

# Base class for all road objects that fall from top to bottom.
# Handles placement, movement and respawning automatically.
class FallingSprite(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self._place()

    # Places the sprite at a clear position above the screen.
    def _place(self):
        r = find_clear_spawn(self.rect.width, self.rect.height)
        self.rect.topleft = r.topleft
        self.mask = pygame.mask.from_surface(self.image)

    # Moves sprite downward each frame. Respawns when fully off screen.
    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self._place()

# Enemy car falling from the top.
# force_red=True locks it to the red car (used in easy mode).
# On hard mode randomly picks between red car and truck each respawn.
class Enemy(FallingSprite):
    def __init__(self, force_red=False):
        self.force_red = force_red
        img = enemy1_img if force_red else (enemy1_img if random.random() < 0.5 else enemy2_img)
        super().__init__(img)

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.image = enemy1_img if self.force_red else (enemy1_img if random.random() < 0.5 else enemy2_img)
            self._place()

# Road barrier. Hitting it costs one life.
class Obstacle(FallingSprite):
    def __init__(self):
        super().__init__(obstacle_img)

# Oil spill on the road. Randomly large or small.
# Touching it reduces SPEED by 30% for 3 seconds.
class OilSpill(FallingSprite):
    def __init__(self):
        img = oil_img_large if random.random() < 0.5 else oil_img_small
        super().__init__(img)

# Coin type configuration — point value per type
COIN_TYPES = {
    "small": {"points": 2},
    "large": {"points": 1},
}

# Collectible coin that falls down the road.
# small ($  coin, 16x16) → 2 pts — harder to collect
# large (star coin, 54x48) → 1 pt — easier to collect
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.coin_type = random.choice(["small", "large"])
        cfg = COIN_TYPES[self.coin_type]
        self.points = cfg["points"]
        self.image = coin_small_img if self.coin_type == "small" else coin_large_img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self._respawn()

    # Respawns coin at a staggered position above the screen.
    # Uses a wider y_range so 3 coins don't all arrive simultaneously.
    def _respawn(self):
        r = find_clear_spawn(self.rect.width, self.rect.height, (-600, -80))
        self.rect.topleft = r.topleft

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self._respawn()

# Power-up type configuration — image and active duration in seconds
POWERUP_TYPES = {
    "nitro":  {"img": nitro_img,  "duration": 4},
    "shield": {"img": shield_img, "duration": 5},
    "repair": {"img": repair_img, "duration": 0},
}

# Collectible power-up that falls down the road.
# Disappears after TIMEOUT seconds if not collected.
# nitro  — multiplies speed by 1.3 for 4 seconds
# shield — blocks all collisions for 5 seconds
# repair — instantly restores one life
class PowerUp(pygame.sprite.Sprite):
    TIMEOUT = 8

    def __init__(self):
        super().__init__()
        self.kind = random.choice(list(POWERUP_TYPES.keys()))
        self.image = pygame.transform.scale(POWERUP_TYPES[self.kind]["img"], (36, 36))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        r = find_clear_spawn(36, 36, (-600, -80))
        self.rect.topleft = r.topleft
        self.spawn_time = time.time()

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT or (time.time() - self.spawn_time) > self.TIMEOUT:
            self.kill()

# The player's car, controlled with left/right arrow keys.
# Tracks lives, active power-up states and slowdown timers.
class Player(pygame.sprite.Sprite):
    MAX_LIVES = 3

    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, 520)
        self.mask = pygame.mask.from_surface(self.image)
        self.lives = self.MAX_LIVES
        self.shield_active = False
        self.shield_end = 0
        self.nitro_active = False
        self.nitro_end = 0
        self.slow_end = 0
        self.oil_active = False

    # Moves player left/right based on arrow key input.
    # Movement is slower when oil slowdown is active.
    def move(self):
        keys = pygame.key.get_pressed()
        step = 3 if self.is_slowed else 5
        if self.rect.left > 0             and keys[K_LEFT]:  self.rect.move_ip(-step, 0)
        if self.rect.right < SCREEN_WIDTH and keys[K_RIGHT]: self.rect.move_ip(step, 0)

    # Activates nitro — records end timestamp for expiry check.
    def apply_nitro(self):
        self.nitro_active = True
        self.nitro_end = time.time() + POWERUP_TYPES["nitro"]["duration"]

    # Activates shield — records end timestamp for expiry check.
    def apply_shield(self):
        self.shield_active = True
        self.shield_end = time.time() + POWERUP_TYPES["shield"]["duration"]

    # Activates oil slowdown for 3 seconds.
    def apply_oil(self):
        self.slow_end = time.time() + 3
        self.oil_active = True

    # Returns True while oil slowdown is still active.
    @property
    def is_slowed(self):
        return time.time() < self.slow_end

# ─────────────────────────────────────────────
# HUD drawing functions
# ─────────────────────────────────────────────

# Draws one heart image per remaining life at the bottom of the screen.
def draw_lives(surface, lives):
    for i in range(lives):
        surface.blit(heart_img, (10 + i * 24, 568))

# Draws all HUD elements: distance, time, coins, speed, power-up, lives.
def draw_hud(surface, distance, elapsed, coins, speed, player, active_pu, pu_timer):
    surface.blit(font_small.render(f"{distance}m", True, BLACK), (10, 10))
    surface.blit(font_tiny.render(f"{elapsed}s",   True, DARK),  (10, 30))
    cs = font_small.render(f"Coins: {coins}", True, YELLOW)
    surface.blit(cs, cs.get_rect(topright=(SCREEN_WIDTH - 10, 10)))
    spd = font_tiny.render(f"SPD {speed:.1f}", True, DARK)
    surface.blit(spd, spd.get_rect(topright=(SCREEN_WIDTH - 10, 30)))
    if active_pu:
        color = BLUE if active_pu == "shield" else GREEN
        label = f"{active_pu.upper()} {pu_timer:.1f}s" if pu_timer > 0 else active_pu.upper()
        surface.blit(font_tiny.render(label, True, color), (10, 46))
    draw_lives(surface, player.lives)

# Draws a button image centered at the given position.
# Returns the rect so the caller can check mouse clicks on it.
def draw_btn(surface, img, center):
    r = img.get_rect(center=center)
    surface.blit(img, r)
    return r

# ─────────────────────────────────────────────
# Screen functions
# ─────────────────────────────────────────────

# Shows a text input field for the player to type their name.
# Saves new players to players.json immediately.
# Returns the entered username string.
def username_screen():
    name = ""
    clock = pygame.time.Clock()
    while True:
        DISPLAYSURF.fill(DARK)
        DISPLAYSURF.blit(font_mid.render("Enter your name:", True, WHITE), (80, 220))
        box = pygame.Rect(60, 268, 280, 42)
        pygame.draw.rect(DISPLAYSURF, WHITE, box, 2)
        DISPLAYSURF.blit(font_mid.render(name + "|", True, YELLOW), (box.x + 8, box.y + 7))
        DISPLAYSURF.blit(font_tiny.render("Press ENTER to start", True, GREY), (115, 330))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN and name.strip():
                    uname = name.strip()
                    if uname not in players_db:
                        players_db[uname] = {"distance": 0}
                        save_json(PLAYERS_FILE, players_db)
                    return uname
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode
        pygame.display.update()
        clock.tick(30)

# Shows the top-10 leaderboard with the podium image for top 3.
# Back button returns to the main menu.
def leaderboard_screen():
    clock = pygame.time.Clock()
    while True:
        DISPLAYSURF.fill(DARK)
        title = font_mid.render("LEADERBOARD", True, GOLD)
        DISPLAYSURF.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 28)))
        DISPLAYSURF.blit(img_podium, img_podium.get_rect(center=(SCREEN_WIDTH // 2, 110)))
        DISPLAYSURF.blit(font_tiny.render("RANK  NAME              DIST(m)", True, GREY), (20, 182))
        pygame.draw.line(DISPLAYSURF, GREY, (20, 196), (380, 196), 1)
        for i, entry in enumerate(leaderboard[:10]):
            y = 202 + i * 34
            color = [GOLD, GREY, (205, 127, 50)][i] if i < 3 else WHITE
            name_s = entry["name"][:14]
            score_s = str(entry["distance"])
            row = font_small.render(f" {i+1}. {name_s:<16} {score_s}", True, color)
            DISPLAYSURF.blit(row, (20, y))
        back_rect = draw_btn(DISPLAYSURF, btn_main_menu, (SCREEN_WIDTH // 2, 570))
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if back_rect.collidepoint(mx, my):
                    return
            if event.type == KEYDOWN and event.key in (K_ESCAPE, K_BACKSPACE):
                return
        pygame.display.update()
        clock.tick(30)

# Shows the settings screen.
# Player can switch between Easy and Hard difficulty.
# Player can change their username without restarting.
# All changes are saved to settings.json immediately.
def settings_screen():
    global username
    clock = pygame.time.Clock()
    while True:
        DISPLAYSURF.fill(DARK)
        title = font_mid.render("SETTINGS", True, GOLD)
        DISPLAYSURF.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 55)))
        DISPLAYSURF.blit(font_small.render("Difficulty:", True, WHITE), (40, 110))
        current = settings.get("difficulty", "easy")
        easy_col = GOLD if current == "easy" else GREY
        hard_col = GOLD if current == "hard" else GREY
        easy_box = pygame.Rect(40,  148, 140, 50)
        hard_box = pygame.Rect(220, 148, 140, 50)
        pygame.draw.rect(DISPLAYSURF, easy_col, easy_box, border_radius=8)
        pygame.draw.rect(DISPLAYSURF, hard_col, hard_box, border_radius=8)
        DISPLAYSURF.blit(
            font_mid.render("EASY", True, DARK),
            font_mid.render("EASY", True, DARK).get_rect(center=easy_box.center))
        DISPLAYSURF.blit(
            font_mid.render("HARD", True, DARK),
            font_mid.render("HARD", True, DARK).get_rect(center=hard_box.center))
        desc = {"easy": "1 enemy car  |  fewer obstacles",
                "hard": "2 enemy cars  |  more obstacles"}.get(current, "")
        DISPLAYSURF.blit(font_tiny.render(desc, True, GREY), (40, 210))
        pygame.draw.line(DISPLAYSURF, GREY, (20, 240), (380, 240), 1)
        DISPLAYSURF.blit(font_small.render("Current user:", True, WHITE), (40, 258))
        DISPLAYSURF.blit(font_small.render(username, True, GOLD), (40, 282))
        change_box = pygame.Rect(40, 318, 320, 50)
        pygame.draw.rect(DISPLAYSURF, (70, 100, 160), change_box, border_radius=8)
        cu_surf = font_mid.render("Change User", True, WHITE)
        DISPLAYSURF.blit(cu_surf, cu_surf.get_rect(center=change_box.center))
        back_rect = draw_btn(DISPLAYSURF, btn_main_menu, (SCREEN_WIDTH // 2, 520))
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if easy_box.collidepoint(mx, my):
                    settings["difficulty"] = "easy"
                    save_json(SETTINGS_FILE, settings)
                if hard_box.collidepoint(mx, my):
                    settings["difficulty"] = "hard"
                    save_json(SETTINGS_FILE, settings)
                if change_box.collidepoint(mx, my):
                    username = username_screen()
                if back_rect.collidepoint(mx, my):
                    return
            if event.type == KEYDOWN and event.key in (K_ESCAPE, K_BACKSPACE):
                return
        pygame.display.update()
        clock.tick(30)

# Shows the main menu with Play, Leaderboard, Quit buttons
# and a settings gear icon in the top-left corner.
# Returns 'play' when the player starts the game.
def main_menu():
    clock = pygame.time.Clock()
    while True:
        DISPLAYSURF.blit(background, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        DISPLAYSURF.blit(overlay, (0, 0))
        DISPLAYSURF.blit(img_racer_title,
                         img_racer_title.get_rect(center=(SCREEN_WIDTH // 2, 150)))
        play_rect = draw_btn(DISPLAYSURF, btn_play,        (SCREEN_WIDTH // 2, 290))
        lb_rect = draw_btn(DISPLAYSURF, btn_leaderboard, (SCREEN_WIDTH // 2, 375))
        quit_rect = draw_btn(DISPLAYSURF, btn_quit,        (SCREEN_WIDTH // 2, 460))
        settings_bg = btn_settings.get_rect(topleft=(10, 10))
        DISPLAYSURF.blit(btn_settings, settings_bg)
        diff_label = settings.get("difficulty", "easy").upper()
        diff_col = GOLD if diff_label == "EASY" else RED
        DISPLAYSURF.blit(font_tiny.render(diff_label, True, diff_col), (66, 26))
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if play_rect.collidepoint(mx, my):   return "play"
                if lb_rect.collidepoint(mx, my):     leaderboard_screen()
                if quit_rect.collidepoint(mx, my):   pygame.quit(); sys.exit()
                if settings_bg.collidepoint(mx, my): settings_screen()
            if event.type == KEYDOWN and event.key == K_RETURN:
                return "play"
        pygame.display.update()
        clock.tick(30)

# Shows the game over screen with final distance, time and coins.
# Returns 'retry' to play again or 'menu' to go back to main menu.
def game_over_screen(distance, elapsed, username):
    clock = pygame.time.Clock()
    go_surf = font_big.render("GAME OVER", True, RED)
    sc_surf = font_small.render(f"{username}  |  {distance}m  |  {elapsed}s", True, WHITE)
    while True:
        DISPLAYSURF.fill(DARK)
        DISPLAYSURF.blit(go_surf, go_surf.get_rect(center=(SCREEN_WIDTH // 2, 190)))
        DISPLAYSURF.blit(sc_surf, sc_surf.get_rect(center=(SCREEN_WIDTH // 2, 265)))
        retry_rect = draw_btn(DISPLAYSURF, btn_retry,     (SCREEN_WIDTH // 2, 360))
        menu_rect = draw_btn(DISPLAYSURF, btn_main_menu, (SCREEN_WIDTH // 2, 450))
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if retry_rect.collidepoint(mx, my): return "retry"
                if menu_rect.collidepoint(mx, my):  return "menu"
            if event.type == KEYDOWN:
                if event.key == K_r: return "retry"
                if event.key == K_m: return "menu"
        pygame.display.update()
        clock.tick(30)

# ═══════════════════════════════════════════════
# Main game loop
# Runs one full game session for the given player.
# Returns 'menu' if ESC is pressed, or the result
# of game_over_screen ('retry' or 'menu').
# ═══════════════════════════════════════════════
def run_game(username):
    global SPEED, occupied_rects

    # Reset all game state for a fresh run
    diff = get_diff()
    SPEED = diff["speed"]
    coins_per_speedup = diff["coins_per_speedup"]
    speed_inc = diff["speed_inc"]
    speed_bumps = 0
    COINS = 0
    DISTANCE = 0.0
    elapsed = 0
    occupied_rects = []
    game_start = time.time()

    # Create sprites based on difficulty
    enemy_count = diff.get("enemy_count", 2)
    is_easy = settings.get("difficulty", "easy") == "easy"
    P1 = Player()
    enemies = pygame.sprite.Group(*[Enemy(force_red=is_easy) for _ in range(enemy_count)])
    oils = pygame.sprite.Group(OilSpill())
    coins_g = pygame.sprite.Group(Coin(), Coin(), Coin())
    powerups = pygame.sprite.Group()
    obstacles = pygame.sprite.Group(Obstacle())
    all_sprites = pygame.sprite.Group(*enemies, *obstacles, *oils, *coins_g)

    # Timers for power-up and obstacle spawning
    pu_next_spawn = time.time() + random.randint(8, 15)
    obs_interval = diff.get("obstacle_interval", 8)
    obs_interval_min = diff.get("obstacle_interval_min", 4)
    obs_next_spawn = time.time() + obs_interval
    active_pu = None
    active_pu_end = 0

    while True:
        now = time.time()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return "menu"

        # Update distance and elapsed time each frame
        DISTANCE += SPEED / (FPS * 10)
        elapsed = int(time.time() - game_start)

        # Rebuild occupied rects from all current sprite positions
        occupied_rects = [s.rect.copy() for s in all_sprites] + [P1.rect.copy()]

        # Anti-overlap system — push any two sprites that are too close apart.
        # Uses the taller sprite's height as the minimum gap so short objects
        # like coins never appear inside the tall truck body.
        all_road = list(enemies) + list(obstacles) + list(coins_g) + list(oils) + list(powerups)
        for i in range(len(all_road)):
            for j in range(i + 1, len(all_road)):
                a, b = all_road[i], all_road[j]
                gap = max(a.rect.height, b.rect.height)
                if a.rect.inflate(gap, gap).colliderect(b.rect.inflate(gap, gap)):
                    top_sprite = a if a.rect.y <= b.rect.y else b
                    ref_sprite = b if top_sprite is a else a
                    top_sprite.rect.y = ref_sprite.rect.top - top_sprite.rect.height - random.randint(100, 300)
                    top_sprite.rect.x = random.randint(40, max(41, SCREEN_WIDTH - 40 - top_sprite.rect.width))

        # Expire nitro — restore speed to earned level
        if P1.nitro_active and now >= P1.nitro_end:
            P1.nitro_active = False
            SPEED = diff["speed"] + speed_bumps * speed_inc

        # Expire nitro display
        if active_pu == "nitro" and now >= active_pu_end:
            active_pu = None

        # Expire shield — check against P1.shield_end directly
        if P1.shield_active and now >= P1.shield_end:
            P1.shield_active = False
            if active_pu == "shield":
                active_pu = None

        # Move all sprites and player
        for entity in all_sprites:
            entity.move()
        for pu in powerups:
            pu.move()
        P1.move()

        # Spawn a power-up on a random timer (only one on road at a time)
        if now >= pu_next_spawn and len(powerups) == 0:
            pu = PowerUp()
            powerups.add(pu)
            pu_next_spawn = now + random.randint(8, 15)

        # Spawn new obstacles over time — interval shrinks as distance increases
        if now >= obs_next_spawn:
            new_obs = Obstacle()
            obstacles.add(new_obs)
            all_sprites.add(new_obs)
            scale_factor = max(0.4, 1.0 - (int(DISTANCE) * 0.002))
            next_interval = max(obs_interval_min, obs_interval * scale_factor)
            obs_next_spawn = now + next_interval

        # Coin collection — award points and check speed milestone
        for coin in pygame.sprite.spritecollide(P1, coins_g, False, pygame.sprite.collide_mask):
            COINS += coin.points
            coin._respawn()
            milestones = COINS // coins_per_speedup
            if milestones > speed_bumps:
                SPEED       += (milestones - speed_bumps) * speed_inc
                speed_bumps = milestones

        # Power-up collection — apply effect immediately
        for pu in pygame.sprite.spritecollide(P1, powerups, True, pygame.sprite.collide_mask):
            if pu.kind == "nitro":
                P1.apply_nitro()
                SPEED = SPEED * 1.3
                active_pu = "nitro"
                active_pu_end = P1.nitro_end
            elif pu.kind == "shield":
                P1.apply_shield()
                active_pu = "shield"
                active_pu_end = P1.shield_end
            elif pu.kind == "repair":
                P1.lives = min(P1.lives + 1, Player.MAX_LIVES)
                active_pu = "repair"
                active_pu_end = now + 1.5

        # Oil spill — reduce speed to 70% for 3 seconds
        if pygame.sprite.spritecollideany(P1, oils, pygame.sprite.collide_mask):
            if not P1.is_slowed:
                P1.apply_oil()
                SPEED = max(2, SPEED * 0.7)

        # Restore speed once oil effect expires
        if P1.oil_active and now >= P1.slow_end:
            P1.oil_active = False
            SPEED = diff["speed"] + speed_bumps * speed_inc

        # Enemy and obstacle collision — shield blocks, otherwise lose a life
        hit = (pygame.sprite.spritecollideany(P1, enemies,   pygame.sprite.collide_mask) or
               pygame.sprite.spritecollideany(P1, obstacles, pygame.sprite.collide_mask))
        if hit:
            if P1.shield_active:
                hit._place()
            else:
                crash_sound.play()
                P1.lives -= 1
                if P1.lives <= 0:
                    save_score(username, int(DISTANCE))
                    DISPLAYSURF.fill(RED)
                    go = font_big.render("GAME OVER", True, BLACK)
                    DISPLAYSURF.blit(go, go.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
                    pygame.display.update()
                    time.sleep(1)
                    return game_over_screen(int(DISTANCE), elapsed, username)
                else:
                    # Flash red screen briefly then continue
                    flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    flash.fill(RED)
                    flash.set_alpha(120)
                    DISPLAYSURF.blit(flash, (0, 0))
                    pygame.display.update()
                    time.sleep(0.4)
                    hit._place()

        # Draw background, all sprites, then HUD on top
        DISPLAYSURF.blit(background, (0, 0))
        for entity in all_sprites:
            DISPLAYSURF.blit(entity.image, entity.rect)
        for pu in powerups:
            DISPLAYSURF.blit(pu.image, pu.rect)
        DISPLAYSURF.blit(P1.image, P1.rect)
        pu_time_left = max(0, active_pu_end - now) if active_pu in ("nitro", "shield") else 0
        draw_hud(DISPLAYSURF, int(DISTANCE), elapsed, COINS, SPEED, P1, active_pu, pu_time_left)

        pygame.display.update()
        FramePerSec.tick(FPS)

# ═══════════════════════════════════════════════
# Entry point — runs when the script is launched.
# Shows username screen first, then loops between
# main menu and game until the player quits.
# ═══════════════════════════════════════════════
username = username_screen()

while True:
    action = main_menu()
    if action == "play":
        result = run_game(username)
        while result == "retry":
            result = run_game(username)