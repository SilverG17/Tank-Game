import pygame


class InputHandler:
    def __init__(self):
        self.keys = {}
        self.mouse_buttons = {}
        self.mouse_pos = (0, 0)
        self.quit_requested = False

    # ==========================================
    # UPDATE (call once per frame)
    # ==========================================
    def update(self):
        self.keys = pygame.key.get_pressed()
        self.mouse_buttons = pygame.mouse.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()
        self.quit_requested = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_requested = True

    # ==========================================
    # KEY CHECKS
    # ==========================================
    def is_key_down(self, key):
        return self.keys[key]

    # ==========================================
    # COMMON GAME CONTROLS
    # ==========================================
    def move_vector(self):
        """
        Returns normalized movement vector (x, y)
        """
        x = 0
        y = 0
        if self.keys[pygame.K_w] or self.keys[pygame.K_UP]:
            y -= 1
        if self.keys[pygame.K_s] or self.keys[pygame.K_DOWN]:
            y += 1
        if self.keys[pygame.K_a] or self.keys[pygame.K_LEFT]:
            x -= 1
        if self.keys[pygame.K_d] or self.keys[pygame.K_RIGHT]:
            x += 1
        vec = pygame.Vector2(x, y)
        if vec.length() > 0:
            vec = vec.normalize()
        return vec

    def is_shoot_pressed(self):
        return self.keys[pygame.K_SPACE]

    def is_restart_pressed(self):
        return self.keys[pygame.K_r]