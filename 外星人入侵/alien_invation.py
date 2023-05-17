import sys  # 玩家退出时，使用sys模块工具退出
from time import sleep
import pygame  # 模块pygame包含开发游戏所需的功能
from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
import random # 导入 random 模块


class AlienInvasion:
    """管理游戏资源和行为的类"""

    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()  # 初始化背景设置
        self.settings = Settings()
        # 全屏模式下运行游戏
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height

        pygame.display.set_caption("Alien Invasion")  # 设置屏幕标题

        # 创建存储游戏统计信息的实例
        # 并创建记分牌
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)  # 在创建屏幕后创建一个Ship实例，并将当前的AlienInvasion实例作为参数
        self.bullets = pygame.sprite.Group()  # 创建一个编组，用于存储所有有效的子弹
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # 创建 Play 按钮
        self.play_button = Button(self, "Play")
        # 创建一个时钟对象
        self.clock = pygame.time.Clock()
        # 创建一个变量来存储上一次下降的时间
        self.last_drop_time = 0


    def run_game(self):
        """开始游戏的主循环"""
        while True:
            # 设置游戏的帧率为 240 帧/秒
            self.clock.tick(240)
            # 获取当前的时间毫秒数
            current_time = pygame.time.get_ticks()
            # 如果当前时间和上一次下降的时间之差大于一定的值，就让飞船下降并改变方向
            if current_time - self.last_drop_time > 1000:
                self._change_fleet_direction()
                # 更新上一次下降的时间为当前时间
                self.last_drop_time = current_time
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()

    def _check_events(self):
        # 监视键盘和鼠标事件
        for event in pygame.event.get():  # 事件循环，pygame.event.get()返回一个列表，包含它上一次被调用后发生的所有事件
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:  # 检测KEYDOWN事件
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """在玩家单击Play按钮时开始新游戏"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # 重置游戏设置
            self.settings.initialize_dynamic_settings()
            # 重置游戏统计信息
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            # 清空余下的外星人和子弹
            self.aliens.empty()
            self.bullets.empty()

            # 创建一群新的外星人并让飞船居中
            self._create_fleet()
            self.ship.center_ship()

            # 隐藏鼠标光标
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """响应按键"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:  # 按q键退出游戏
            self.running = False
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()


    def _check_keyup_events(self, event):
        """相应松开"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """创建一颗子弹，并将其加入编组bullet中"""
        if len(self.bullets) < self.settings.bullets_allowed:  # 如果子弹个数小于3，将创建一颗新子弹，如果有3颗未消失的子弹
            new_bullet = Bullet(self)  # 则玩家按按空格键时，什么都不会发生
            self.bullets.add(new_bullet)

    def _create_fleet(self):
        """创建外星人群"""
        # 设置最大外星人数量
        max_aliens = 10
        # 创建外星人群
        while len(self.aliens) < max_aliens:
            # 创建一个外星人并将其加入当前编组
            alien = Alien(self)
            self.aliens.add(alien)

    def _create_alien(self):
        # 创建一个外星人并设置其随机的 x 坐标和 y 坐标
        alien = Alien(self)
        alien_width = alien.rect.width
        alien_height = alien.rect.height
        # 用一个循环来避免重叠
        overlap = True
        while overlap:
            # 随机生成位置
            self.x = random.randint(0, self.settings.screen_width - alien_width)
            alien.rect.x = self.x
            alien.rect.y = random.randint(0, self.settings.screen_height // 2 - alien_height)
            # 检测碰撞
            collisions = pygame.sprite.spritecollide(alien, self.aliens, False)
            # collisions = pygame.sprite.spritecollide(alien, self.aliens, False, pygame.sprite.collide_mask)
            # 如果没有碰撞，跳出循环
            if len(collisions) == 0:
                overlap = False
        self.aliens.add(alien)  # 将该实例添加到用于存储外星人群的编组中


    def _check_fleet_edges(self):
        """外星人到达边缘时采取相应的措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """将整群外星人下移，并改变他们的方向"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_aliens(self):
        """检查是否有外星人位于屏幕边缘，并更新整群外星人的位置"""
        self._check_fleet_edges()
        # 更新外星人群中所有外星人的位置
        self.aliens.update()

        # 检测外星人和飞船之间的碰撞
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # 检查是否有外星人到达了屏幕底端
        self._check_aliens_bottom()

    def _update_screen(self):
        """更新屏幕是的图像，并切换到新屏幕"""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        # 显示得分
        self.sb.show_score()

        # 如果游戏处于非活动状态，就绘制Play按钮
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()

    def _update_bullets(self):
        """更新子弹的位置并删除消失的子弹"""
        # 更新子弹的位置
        self.bullets.update()
        # 删除消失的子弹
        for bullet in self.bullets.copy():  # 遍历Pygame编组
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()
        # 检查是否有子弹击中了外星人
        # 如果是，就删除相应的子弹和外星人

        if not self.aliens:
            # 删除现有的子弹并新建一群外星人
            self.bullets.empty()
            self._create_fleet()
        # self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """响应子弹和外星人碰撞"""
        # 删除彼此碰撞的子弹和外星人
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:  # 检查编组是否为空
            # 删除现有的子弹并新建一群外星人
            # for aliens in collisions.values():
            # self.stats.score += self.settings.alien_points * len(aliens)
            # if not self.aliens:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                self.sb.prep_score()
                self.sb.check_high_score()
                self.bullets.empty()
                # self._create_fleet()
                self.settings.increase_speed()

            # 提高等级
            self.stats.level += 1
            self.sb.prep_level()

    def _ship_hit(self):
        """响应飞船被外星人撞到"""
        if self.stats.ships_left > 1:  # 将条件改为大于 1
            # 将 ships_left 减 1,并更新记分牌
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            # 清空余下的外星人和子弹
            self.aliens.empty()
            self.bullets.empty()
            # 创建一群新的的外星人，并将飞船放到屏幕底端的中央
            self._create_fleet()
            self.ship.center_ship()
            # 暂停
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """检查是否有外星人到达了屏幕底端"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # 像飞船被撞到一样处理
                self._ship_hit()
                break



if __name__ == '__main__':
    # 创建游戏实例并运行游戏
    ai = AlienInvasion()
    ai.run_game()
pygame.quit()