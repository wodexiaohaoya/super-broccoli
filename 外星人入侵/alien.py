import pygame
from pygame.sprite import Sprite
import random  # 导入 random 模块


class Alien(Sprite):
    """表示单个外星人的类"""

    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        # 加载外星人图像并设置其 rect 属性
        self.image = pygame.image.load('images/alien.png')
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect()
        # 随机生成外星人的 x 坐标和 y 坐标
        alien_width = self.rect.width
        alien_height = self.rect.height
        self.x = random.randint(0, self.settings.screen_width - alien_width)
        self.rect.x = self.x
        self.rect.y = random.randint(0, self.settings.screen_height // 2 - alien_height)
        # 存储外星人的精确水平位置
        self.x = float(self.rect.x)

    def check_edges(self):
        """如果外星人位于屏幕边缘，就返回 True"""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True

    def update(self):
        """向左或向右移动外星人"""
        self.x += (self.settings.alien_speed * self.settings.fleet_direction)
        self.rect.x = self.x
