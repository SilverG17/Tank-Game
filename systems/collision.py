import pygame

class CollisionSystem:
    def __init__(self):
        pass

    # ==========================================
    # BASIC AABB
    # ==========================================
    @staticmethod
    def rect_collision(rect1, rect2):
        return rect1.colliderect(rect2)

    # ==========================================
    # GENERIC RECT VS OBJECT LIST
    # ==========================================
    def rect_vs_objects(self, rect, objects):
        """
        Check collision between a rect and a list of objects
        that contain .rect
        """
        for obj in objects:
            if self.rect_collision(rect, obj.rect):
                return obj
        return None

    # ==========================================
    # BULLET VS TREES
    # ==========================================
    def bullet_vs_trees(self, bullet, trees):
        return self.rect_vs_objects(bullet.rect, trees)
    
    # ==========================================
    # BULLET VS TANK
    # ==========================================
    def bullet_vs_trees(self, bullet, trees):
        return self.rect_vs_objects(bullet.rect, trees)

    # ==========================================
    # TANK VS TREES (movement blocking)
    # ==========================================
    def tank_vs_trees(self, tank, trees):
        return self.rect_vs_objects(tank.rect, trees)
    
    # ==========================================
    # BULLET VS BULLET
    # ==========================================
    def bullet_vs_bullets(self, bullet, bullets):
        for other in bullets:
            if other is bullet:
                continue
            if self.rect_collision(bullet.rect, other.rect):
                return other
        return None