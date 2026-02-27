import pygame
import sys
import os
import math
import random

# --- KHỞI TẠO CƠ BẢN ---
pygame.init()
TILE_SIZE = 64
WIDTH, HEIGHT = 18 * TILE_SIZE, 12 * TILE_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Battle - Physics & Bouncing Edition")
clock = pygame.time.Clock()

# Fonts
font_title = pygame.font.SysFont("Impact", 100)
font_big = pygame.font.SysFont("Impact", 60)
font_hud = pygame.font.SysFont("Arial", 20, bold=True)
font_score = pygame.font.SysFont("Consolas", 30, bold=True)
font_guide = pygame.font.SysFont("Arial", 16, bold=True)

# Game Config
SCORE_LIMIT = 400 
game_state = "START" 
winner_text = ""
p1_sens, p2_sens = 200, 200

# --- TẢI ASSETS ---
def load_t(name, scale=TILE_SIZE):
    # Tạo đường dẫn đầy đủ: image/tên_file.png
    path = os.path.join("image", name) 
    
    if os.path.exists(path):
        return pygame.transform.scale(pygame.image.load(path).convert_alpha(), (scale, scale))
    
    # Nếu không tìm thấy, tạo ô màu tím lỗi
    print(f"Lỗi: Không tìm thấy file {path}")
    surf = pygame.Surface((scale, scale))
    surf.fill((255, 0, 255)) 
    return surf

# --- TẢI ÂM THANH (Dành cho MP3) ---
pygame.mixer.pre_init(44100, -16, 2, 512) # Tối ưu hóa để giảm độ trễ MP3
pygame.mixer.init()

def load_sfx(name):
    path = os.path.join("sound", name)
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return None
    print(f"Warning: Sound file {path} not found")
    return None

# Nạp các hiệu ứng từ file MP3
SFX = {
    'fire':   load_sfx("fire.mp3"),
    'hit':    load_sfx("hit.mp3"),
    'coin':   load_sfx("coin.mp3"),
    'bounce': load_sfx("bounce.mp3"),
    'over': load_sfx("nop.mp3")
}

# Chỉnh âm lượng riêng cho từng loại nếu cần (0.0 đến 1.0)
if SFX['fire']: SFX['fire'].set_volume(0.6)
if SFX['bounce']: SFX['bounce'].set_volume(0.4)

# Nhạc nền MP3 (Background Music)
bg_music_path = os.path.join("sound", "bg_music.mp3")
if os.path.exists(bg_music_path):
    pygame.mixer.music.load(bg_music_path)
    pygame.mixer.music.set_volume(0.2) # Nhạc nền nhỏ thôi để nghe tiếng súng
    pygame.mixer.music.play(-1) # -1 là lặp lại vô tận

TILES = {
    'e': load_t("tileGrass_roadEast.png"), 'n': load_t("tileGrass_roadNorth.png"),
    'X': load_t("tileGrass_roadCrossing.png"), 'R': load_t("tileGrass_roadCornerLL.png"),
    'L': load_t("tileGrass_roadCornerLR.png"), 'r': load_t("tileGrass_roadCornerUL.png"),
    'l': load_t("tileGrass_roadCornerUR.png"), 'S': load_t("tileGrass_roadSplitS.png"),
    'E': load_t("tileGrass_roadSplitE.png"), 'N': load_t("tileGrass_roadSplitN.png"),
    'W': load_t("tileGrass_roadSplitW.png"), 'g': load_t("tileGrass2.png"),
    'B': load_t("tileRock_large.png"), 'T': load_t("tree.png"),
}

LEVEL_MAP = [
    "LeeeeeeeeeeeeeeeeR",
    "ngggggggTggggggggn",
    "nggTggggBggggTgggn",
    "nggggTggggggggTggn",
    "nggBgggggggBggBggn",
    "ngggggggBggTgggggn",
    "ngggBgTgggggggTggn",
    "nggTggggTggggTgggn",
    "nBggggggBgggggBggn",
    "ngggggBgggggBggggn",
    "nggggggggBgggggggn",
    "leeeeeeeeeeeeeeeer",
]

# --- CLASSES ---
class Bullet:
    def __init__(self, pos, angle, owner):
        self.pos = pygame.Vector2(pos)
        # Physics: Góc Pygame 0 độ là hướng lên, math 0 độ là hướng phải
        rad = math.radians(angle - 90)
        self.speed = 450
        self.vel = pygame.Vector2(math.cos(rad) * self.speed, math.sin(rad) * self.speed)
        self.owner = owner
        self.active = True
        self.bounces = 0
        self.max_bounces = 3 

    def update(self, dt):
        next_pos = self.pos + self.vel * dt
        
        # Logic Đạn nảy (Bouncing)
        gx, gy = int(next_pos.x // TILE_SIZE), int(next_pos.y // TILE_SIZE)
        if 0 <= gy < len(LEVEL_MAP) and 0 <= gx < len(LEVEL_MAP[0]):
            if LEVEL_MAP[gy][gx] == 'B':
                # Tính toán Reflection dựa trên vị trí tương đối trong Tile
                rel_x = next_pos.x % TILE_SIZE
                rel_y = next_pos.y % TILE_SIZE
                
                # Nếu đập vào cạnh dọc (trái/phải)
                if rel_x < 10 or rel_x > TILE_SIZE - 10:
                    self.vel.x *= -1
                    if SFX['bounce']: SFX['bounce'].play()
                # Nếu đập vào cạnh ngang (trên/dưới)
                else:
                    self.vel.y *= -1
                    if SFX['bounce']: SFX['bounce'].play()
                
                self.bounces += 1
                if self.bounces > self.max_bounces: self.active = False
                return

        self.pos = next_pos
        if not screen.get_rect().collidepoint(self.pos):
            self.active = False

    def draw(self, surf):
        pygame.draw.circle(surf, (255, 215, 0), (int(self.pos.x), int(self.pos.y)), 4)

class Coin:
    def __init__(self):
        self.image = load_t("coin.png", 35)
        self.spawn()

    def spawn(self):
        # 1. Tạo danh sách tất cả các vị trí (gx, gy) có thể đặt Coin
        valid_positions = []
        for gy in range(len(LEVEL_MAP)):
            for gx in range(len(LEVEL_MAP[0])):
                # Chỉ thêm vào danh sách nếu ô đó KHÔNG phải vật cản
                if LEVEL_MAP[gy][gx] not in ['B', 'T', '.']:
                    valid_positions.append((gx, gy))

        # 2. Nếu tìm thấy vị trí hợp lệ, chọn ngẫu nhiên một ô
        if valid_positions:
            gx, gy = random.choice(valid_positions)
            
            # Tính toán tọa độ pixel dựa trên TILE_SIZE
            self.pos = pygame.Vector2(gx * TILE_SIZE + TILE_SIZE // 2, 
                                     gy * TILE_SIZE + TILE_SIZE // 2)
            self.rect = self.image.get_rect(center=self.pos)
        else:
            # Trường hợp bản đồ không còn chỗ trống nào
            print("Warning: Không còn vị trí nào để spawn Coin!")

    def draw(self, surf):
        surf.blit(self.image, self.rect)

class Tank:
    def __init__(self, x, y, controls, color, name):
        self.pos = pygame.Vector2(x, y)
        self.controls = controls
        self.name = name
        # --- THÊM MỚI ---
        # Trong Tank.__init__
        self.speed_boost = 1.0
        self.has_shield = False
        self.triple_shot_timer = 0
        self.powerup_timers = {'SPEED': 0, 'SHIELD': 0, 'TRIPLE': 0}
        self.max_bullets = 5        # Giới hạn 5 viên đạn trên màn hình
        self.cooldown_time = 120    # 500ms (0.5 giây) giữa mỗi lần bắn
        self.last_shot_time = 0

        self.angle = 0
        self.health = 100
        self.score = 0
        self.flash_timer = 0
        self.hull_orig = load_t("Hull_01.png", 50)
        self.gun_orig = load_t("Gun_01.png", 50)
        self.hull = self.hull_orig.copy()
        self.hull.fill(color, special_flags=pygame.BLEND_MULT)
        self.rect = self.hull.get_rect(center=self.pos)

    def check_collision(self, next_pos):
        if not (0 <= next_pos.x < WIDTH and 0 <= next_pos.y < HEIGHT):
            return False
        
        # THAY ĐỔI QUAN TRỌNG: inflate(-20, -20)
        # Lệnh này tạo ra một khung va chạm ảo nhỏ hơn hình ảnh thật 20 pixel mỗi chiều
        # Giúp bạn có thể "quẹt" nhẹ vào cạnh đá mà không bị đứng khựng lại
        tank_physics_rect = self.hull.get_rect(center=next_pos).inflate(-20, -20)
        
        # Kiểm tra va chạm với Đá 'B'
        start_x = max(0, int((next_pos.x - TILE_SIZE) // TILE_SIZE))
        end_x = min(len(LEVEL_MAP[0]), int((next_pos.x + TILE_SIZE) // TILE_SIZE) + 1)
        start_y = max(0, int((next_pos.y - TILE_SIZE) // TILE_SIZE))
        end_y = min(len(LEVEL_MAP), int((next_pos.y + TILE_SIZE) // TILE_SIZE) + 1)

        for gy in range(start_y, end_y):
            for gx in range(start_x, end_x):
                if LEVEL_MAP[gy][gx] == 'B':
                    block_rect = pygame.Rect(gx * TILE_SIZE, gy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if tank_physics_rect.colliderect(block_rect):
                        return False
        
        # Kiểm tra va chạm với Cây (Cũng dùng hitbox thu nhỏ)
        for t in trees:
            # Thu nhỏ hitbox của cây đi 15 pixel mỗi chiều khi tính toán va chạm
            tree_physics_rect = t.rect.inflate(-15, -15) 
            if tank_physics_rect.colliderect(tree_physics_rect):
                return False
                
        return True

    def update(self, dt, keys, sensitivity):
        if self.flash_timer > 0: self.flash_timer -= dt
        
        # Xoay Tank
        if keys[self.controls['left']]: self.angle -= sensitivity * dt
        if keys[self.controls['right']]: self.angle += sensitivity * dt
        
        # Vector Movement: Forward/Backward
        rad = math.radians(self.angle - 90)
        move_vec = pygame.Vector2(0, 0)
        
        if keys[self.controls['up']]:
            move_vec = pygame.Vector2(math.cos(rad), math.sin(rad))
        elif keys[self.controls['down']]:
            move_vec = pygame.Vector2(-math.cos(rad), -math.sin(rad))
            
        if move_vec.length() > 0:
            new_pos = self.pos + move_vec * (160 * self.speed_boost) * dt
            if self.check_collision(new_pos):
                self.pos = new_pos
                self.rect.center = self.pos
        # Trong Tank.update
        for key in self.powerup_timers:
            if self.powerup_timers[key] > 0:
                self.powerup_timers[key] -= dt
            else:
                # Reset lại chỉ số khi hết thời gian
                if key == 'SPEED': self.speed_boost = 1.0
                if key == 'SHIELD': self.has_shield = False

    def draw(self, surf):
        if self.flash_timer > 0 and int(self.flash_timer * 15) % 2 == 0: return
        
        # Vẽ vòng tròn bảo vệ nếu có SHIELD
        if self.has_shield:
            pygame.draw.circle(surf, (0, 255, 255), (int(self.pos.x), int(self.pos.y)), 35, 2)
            
        # Vẽ vệt sáng nếu có SPEED
        if self.speed_boost > 1.0:
            pygame.draw.circle(surf, (255, 255, 0), (int(self.pos.x), int(self.pos.y)), 30, 1)
        # Rotate body dựa trên self.angle
        h_rot = pygame.transform.rotate(self.hull, -self.angle)
        g_rot = pygame.transform.rotate(self.gun_orig, -self.angle)
        surf.blit(h_rot, h_rot.get_rect(center=self.pos))
        surf.blit(g_rot, g_rot.get_rect(center=self.pos))

class PowerUp:
    def __init__(self):
        self.types = ['SPEED', 'SHIELD', 'TRIPLE']
        self.type = random.choice(self.types)
        
        # 1. Xác định kích thước trước (Ví dụ: 60 cho to rõ)
        self.size = 60  
        self.duration = 5.0
        
        # 2. Nạp ảnh với đúng kích thước self.size đã chọn
        if self.type == 'SPEED':
            self.image = load_t("speed.png", self.size)
        elif self.type == 'SHIELD':
            self.image = load_t("shield.png", self.size)
        else:
            self.image = load_t("triple.png", self.size)
            
        # 3. Cuối cùng mới spawn để tính toán vị trí và rect
        self.spawn()

    def spawn(self):
        valid_pos = []
        for gy, row in enumerate(LEVEL_MAP):
            for gx, char in enumerate(row):
                if char == 'g' or char in "enXRLrlSENW":
                    valid_pos.append((gx * TILE_SIZE + TILE_SIZE//2, gy * TILE_SIZE + TILE_SIZE//2))
        
        self.pos = pygame.Vector2(random.choice(valid_pos))
        # Tạo rect khớp với ảnh đã scale
        self.rect = self.image.get_rect(center=self.pos)

    def draw(self, surf):
        surf.blit(self.image, self.rect)

class Tree:
    def __init__(self, gx, gy):
        self.image = TILES['T']
        self.gx = gx
        self.gy = gy
        self.pos = pygame.Vector2(gx * TILE_SIZE, gy * TILE_SIZE)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, TILE_SIZE, TILE_SIZE)
        self.health = 4 # 4 lần trúng đạn

    def draw(self, surf):
        # Bạn có thể vẽ cây mờ dần khi máu giảm để tạo hiệu ứng
        alpha = (self.health / 4) * 255
        self.image.set_alpha(alpha)
        surf.blit(self.image, self.pos)
# --- FUNCTIONS ---
def draw_hud():
    # Máu & Điểm
    pygame.draw.rect(screen, (50, 50, 50), (20, 20, 150, 15))
    pygame.draw.rect(screen, (0, 255, 0), (20, 20, p1.health * 1.5, 15))
    p1_s = font_hud.render(f"P1: {p1.score}", True, (255, 255, 255))
    screen.blit(p1_s, (20, 40))

    pygame.draw.rect(screen, (50, 50, 50), (WIDTH-170, 20, 150, 15))
    pygame.draw.rect(screen, (0, 255, 0), (WIDTH-170, 20, p2.health * 1.5, 15))
    p2_s = font_hud.render(f"P2: {p2.score}", True, (255, 255, 255))
    screen.blit(p2_s, (WIDTH-170, 40))

    goal_txt = font_hud.render(f"GOAL: {SCORE_LIMIT}", True, (255, 255, 0))
    screen.blit(goal_txt, (WIDTH//2 - goal_txt.get_width()//2, 20))
    # Hướng dẫn
    def draw_t_s(text, x, y):
        s = font_guide.render(text, True, (0, 0, 0))
        t = font_guide.render(text, True, (255, 255, 255))
        screen.blit(s, (x+1, y+1)); screen.blit(t, (x, y))

    draw_t_s("P1: WASD + SPACE/F", 50, HEIGHT - 35)
    draw_t_s("P2: ARROWS + ENTER/M", WIDTH - 200, HEIGHT - 35)
    screen.blit(GEAR_IMG, gear_rect)

def show_settings():
    global p1_sens, p2_sens
    waiting = True
    while waiting:
        screen.fill((20, 20, 20))
        title = font_score.render("SETTINGS", True, (255, 215, 0))
        p1_t = font_hud.render(f"P1 Sensitivity: {p1_sens} (W/S)", True, (100, 200, 255))
        p2_t = font_hud.render(f"P2 Sensitivity: {p2_sens} (UP/DOWN)", True, (255, 100, 100))
        hint = font_hud.render("Press ENTER to Save", True, (150, 150, 150))
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        screen.blit(p1_t, (WIDTH//2 - p1_t.get_width()//2, 250))
        screen.blit(p2_t, (WIDTH//2 - p2_t.get_width()//2, 300))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 400))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w: p1_sens += 10
                if event.key == pygame.K_s: p1_sens -= 10
                if event.key == pygame.K_UP: p2_sens += 10
                if event.key == pygame.K_DOWN: p2_sens -= 10
                if event.key == pygame.K_RETURN: waiting = False
        pygame.display.flip()

# --- INITIALIZE OBJECTS ---
GEAR_IMG = load_t("settings_icon.png", 40)
gear_rect = GEAR_IMG.get_rect(center=(WIDTH // 2, HEIGHT - 30))

p1_ctrl = {
    'up': pygame.K_w, 
    'down': pygame.K_s, 
    'left': pygame.K_a, 
    'right': pygame.K_d, 
    'fire': [pygame.K_SPACE, pygame.K_f] # Danh sách phím bắn cho P1
}
p2_ctrl = {
    'up': pygame.K_UP, 
    'down': pygame.K_DOWN, 
    'left': pygame.K_LEFT, 
    'right': pygame.K_RIGHT, 
    'fire': [pygame.K_RETURN, pygame.K_m] # Danh sách phím bắn cho P2
}

p1 = Tank(TILE_SIZE*1.5, TILE_SIZE*1.5, p1_ctrl, (100, 200, 255), "Player 1")
p2 = Tank(WIDTH - TILE_SIZE*1.5, HEIGHT - TILE_SIZE*3, p2_ctrl, (255, 100, 100), "Player 2")
coins = [Coin() for _ in range(5)] # Tạo ra 5 đồng xu ngẫu nhiên
bullets = []

# Tìm tất cả cây trong LEVEL_MAP và tạo object
trees = []
for gy, row in enumerate(LEVEL_MAP):
    for gx, char in enumerate(row):
        if char == 'T':
            trees.append(Tree(gx, gy))

# Chuyển LEVEL_MAP thành danh sách có thể thay đổi (list of lists)
# Để khi cây mất, ta biến ô đó thành cỏ 'g'
WORKING_MAP = [list(row) for row in LEVEL_MAP]
for gy in range(len(WORKING_MAP)):
    for gx in range(len(WORKING_MAP[0])):
        if WORKING_MAP[gy][gx] == 'T':
            WORKING_MAP[gy][gx] = 'g' # Xóa cây tĩnh, chỉ để lại cỏ

# Sau đó, cập nhật LEVEL_MAP để không vẽ cây tĩnh đè lên cây động
# Bạn có thể thay đổi 'T' thành 'g' (cỏ) trong LEVEL_MAP sau khi đã nạp vào danh sách trees
MODIFIED_MAP = [list(row) for row in LEVEL_MAP]

def init_trees():
    global trees
    trees = []
    for gy, row in enumerate(LEVEL_MAP):
        for gx, char in enumerate(row):
            if char == 'T':
                new_tree = Tree(gx, gy)
                # Đảm bảo cây mới luôn hiển thị rõ nét 100%
                new_tree.image.set_alpha(255) 
                trees.append(new_tree)

# Gọi lần đầu để khởi tạo cây khi mở game
init_trees()

# Thêm vào trước Main Loop
POWERUP_SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(POWERUP_SPAWN_EVENT, 10000) # 10 giây xuất hiện 1 cái
powerups = []

# --- MAIN LOOP ---
while True:
    dt = clock.tick(60) / 1000.0
    events = pygame.event.get()
    current_time = pygame.time.get_ticks()
    
    for event in events:
        if event.type == pygame.QUIT: 
            pygame.quit(); sys.exit()

        # --- SPAWN POWER-UPS ---
        if game_state == "PLAYING" and event.type == POWERUP_SPAWN_EVENT:
            if len(powerups) < 3: # Tối đa 3 vật phẩm trên map
                powerups.append(PowerUp())

        if game_state == "START":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_state = "PLAYING"
        
        elif game_state == "PLAYING":
            if event.type == pygame.KEYDOWN:
                # Xử lý bắn đạn (P1 & P2)
                for p in [p1, p2]:
                    if event.key in p.controls['fire']:
                        p_bullets = [b for b in bullets if b.owner == p]
                        if len(p_bullets) < p.max_bullets and current_time - p.last_shot_time > p.cooldown_time:
                            # LOGIC TRIPLE SHOT
                            if p.powerup_timers['TRIPLE'] > 0:
                                for off in [-15, 0, 15]:
                                    bullets.append(Bullet(p.pos, p.angle + off, p))
                            else:
                                bullets.append(Bullet(p.pos, p.angle, p))
                            
                            if SFX['fire']: SFX['fire'].play()
                            p.last_shot_time = current_time
        
        elif game_state == "GAMEOVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # 1. Reset thông số người chơi
                for p in [p1, p2]:
                    p.health, p.score = 100, 0
                
                # 2. Reset vị trí
                p1.pos = pygame.Vector2(TILE_SIZE*1.5, TILE_SIZE*1.5)
                p2.pos = pygame.Vector2(WIDTH - TILE_SIZE*1.5, HEIGHT - TILE_SIZE*3)
                p1.angle, p2.angle = 0, 0
                
                # 3. Reset thực thể game
                bullets.clear()
                for c in coins: c.spawn()
                
                # --- QUAN TRỌNG: NẠP LẠI CÂY TỪ LEVEL_MAP ---
                init_trees() 
                
                if SFX['over']: SFX['over'].play()
                powerups.clear()
                game_state = "PLAYING"

    # --- RENDER LOGIC ---
    if game_state == "START":
        screen.fill((30, 50, 30))
        t_s = font_title.render("TANK BATTLE", True, (255, 215, 0))
        h_s = font_big.render("PRESS SPACE TO START", True, (255, 255, 255))
        screen.blit(t_s, (WIDTH//2 - t_s.get_width()//2, HEIGHT//3))
        screen.blit(h_s, (WIDTH//2 - h_s.get_width()//2, HEIGHT//2))

    elif game_state == "PLAYING":
        # Update
        keys = pygame.key.get_pressed()
        p1.update(dt, keys, p1_sens)
        p2.update(dt, keys, p2_sens)

        # Coin Collection
        for c in coins:
            for p in [p1, p2]:
                if p.rect.colliderect(c.rect):
                    p.score += 20
                    c.spawn()
                    if SFX['coin']: SFX['coin'].play()
                    if p.score >= SCORE_LIMIT:
                        winner_text = f"{p.name.upper()} REACHED {SCORE_LIMIT} PTS!"
                        game_state = "GAMEOVER"
        
        # --- Power-up Collection --- (CHÈN VÀO ĐÂY)
        for pw in powerups[:]:
            for p in [p1, p2]:
                if p.rect.colliderect(pw.rect):
                    if pw.type == 'SPEED':
                        p.speed_boost = 1.8
                    elif pw.type == 'SHIELD':
                        p.has_shield = True
                    # Triple shot được xử lý ở phần bắn đạn
                    
                    p.powerup_timers[pw.type] = pw.duration
                    powerups.remove(pw)
                    if SFX['coin']: SFX['coin'].play()

        # Bullet Physics & Combat
    # --- TRONG VÒNG LẶP PLAYING ---
# --- TRONG VÒNG LẶP PLAYING ---
        for b in bullets[:]:
            b.update(dt)
            
            bullet_hit_something = False
            
            # 1. Kiểm tra va chạm với cây
            for t in trees[:]:
                if t.rect.collidepoint(b.pos):
                    t.health -= 1
                    b.active = False
                    bullet_hit_something = True
                    if SFX['hit']: SFX['hit'].play()
                    if t.health <= 0:
                        trees.remove(t)
                    break 
            
            # 2. Nếu CHƯA chạm cây, mới kiểm tra chạm Tank
            if not bullet_hit_something:
                # ĐỊNH NGHĨA TARGET Ở ĐÂY
                target = p2 if b.owner == p1 else p1
                
                if target.rect.collidepoint(b.pos):
                    # KIỂM TRA SHIELD TRƯỚC KHI TRỪ MÁU
                    if target.has_shield:
                        target.has_shield = False
                        target.powerup_timers['SHIELD'] = 0
                        # Không trừ máu, chỉ mất khiên
                    else:
                        target.health -= 10
                        target.flash_timer = 0.5
                        b.owner.score += 15
                    
                    b.active = False
                    if SFX['hit']: SFX['hit'].play()
                    
                    # Kiểm tra điều kiện thắng
                    if target.health <= 0 or b.owner.score >= SCORE_LIMIT:
                        winner_text = f"{b.owner.name.upper()} IS THE VICTOR!"
                        game_state = "GAMEOVER"
            
            # 3. Xóa đạn
            if not b.active:
                if b in bullets:
                    bullets.remove(b)

       # Draw
        screen.fill((34, 139, 34)) 
        for r, row in enumerate(LEVEL_MAP):
            for c, char in enumerate(row):
                # Luôn vẽ cỏ làm nền
                screen.blit(TILES['g'], (c*TILE_SIZE, r*TILE_SIZE))
                
                # CHỈ vẽ các vật thể KHÔNG phải cây 'T' từ LEVEL_MAP
                if char in TILES and char != 'g' and char != 'T':
                    screen.blit(TILES[char], (c*TILE_SIZE, r*TILE_SIZE))
        
        # Vẽ các cây động (có máu và có thể bị xóa)
        for t in trees: 
            t.draw(screen)
        
        for pw in powerups:
            pw.draw(screen)

        for c in coins: c.draw(screen)
        for b in bullets: b.draw(screen)
        p1.draw(screen)
        p2.draw(screen)
        draw_hud()

    elif game_state == "GAMEOVER":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        w_s = font_big.render(winner_text, True, (255, 215, 0))
        r_s = font_hud.render("PRESS 'R' TO RESTART MISSION", True, (255, 255, 255))
        screen.blit(w_s, (WIDTH//2 - w_s.get_width()//2, HEIGHT//2 - 40))
        screen.blit(r_s, (WIDTH//2 - r_s.get_width()//2, HEIGHT//2 + 40))

    pygame.display.flip()