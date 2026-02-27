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
    # BULLET VS TREES
    # ==========================================
    def bullet_vs_trees(self, bullet, trees):
        """
        Return True if bullet hits tree
        """
        for tree in trees:
            if tree.rect.colliderect(bullet.rect):
                return tree
        return None

    # ==========================================
    # BULLET VS TANK
    # ==========================================
    def bullet_vs_tank(self, bullet, tank):
        if tank.rect.colliderect(bullet.rect):
            return True
        return False

    # ==========================================
    # TANK VS TREES (movement blocking)
    # ==========================================
    def tank_vs_trees(self, tank, trees):
        for tree in trees:
            if tank.rect.colliderect(tree.rect):
                return tree
        return None

    # ==========================================
    # BULLET VS BULLET
    # ==========================================
    def bullet_vs_bullets(self, bullet, bullets):
        for other in bullets:
            if other is bullet:
                continue
            if bullet.rect.colliderect(other.rect):
                return other
        return None