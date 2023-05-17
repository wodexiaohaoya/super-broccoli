需要更新的三个方向
- 为了让外星人持续随机地生成，可以在 _create_fleet() 方法中使用 random 模块来随机生成外星人的 x 坐标和行数。
- 为了让飞机实际生命为 3 条，可以在 _ship_hit() 方法中检查 self.stats.ships_left 是否大于 1 而不是大于 0，这样就不会多出一条生命。
- 另外，还可以优化一些代码，比如使用 pygame.sprite.collide_rect() 来检测碰撞，使用 pygame.display.update() 来更新屏幕，使用 pygame.time.Clock() 来控制帧率等。

更改 Alien 类：
- 首先，需要在代码开头导入 random 模块，使用 `import random` 语句。
- 然后，在 _create_alien() 方法中，不再使用 alien_number 和 row_number 来计算外星人的 x 坐标和 y 坐标，而是使用 random.randint() 函数来生成一个随机整数¹²⁴⁵。例如，可以使用 `alien.x = random.randint(0, self.settings.screen_width - alien_width)` 来生成一个在屏幕宽度范围内的随机 x 坐标，同理可以用 `alien.rect.y = random.randint(0, self.settings.screen_height // 2 - alien_height)` 来生成一个在屏幕上半部分的随机 y 坐标。
- 最后，在 _create_fleet() 方法中，不再使用 number_aliens_x 和 number_rows 来控制外星人的数量，而是使用一个循环来不断地创建外星人，直到达到一定的限制条件。例如，可以使用 `while len(self.aliens) < self.settings.alien_limit:` 来判断外星人的数量是否超过了设置的上限⁶。这样就可以实现随机源源不断地在屏幕顶方生成外星人的效果。


- 在 _create_fleet() 方法中，使用 random 模块来随机生成外星人的 x 坐标和行数。使用 random.randint() 函数来生成一个范围内的整数。例如，你可以这样修改 Alien 类的 __init__() 方法：

```python
# 随机生成外星人的 x 坐标和 y 坐标
alien_width = self.rect.width
alien_height = self.rect.height
self.x = random.randint(0, self.settings.screen_width - alien_width)
self.rect.x = self.x
self.rect.y = random.randint(0, self.settings.screen_height // 2 - alien_height)
```

- 然后，你可以在 _create_fleet() 方法中，使用一个循环来随机生成一定数量的外星人，而不是按照固定的行列数来创建。使用 len() 函数来获取当前外星人编组的长度，然后用一个条件判断来控制循环。例如，你可以这样修改 _create_fleet() 方法：

```python
def _create_fleet(self):
    """创建外星人群"""
    # 设置最大外星人数量
    max_aliens = 20
    # 创建外星人群
    while len(self.aliens) < max_aliens:
        # 创建一个外星人并将其加入当前编组
        alien = Alien(self)
        self.aliens.add(alien)
```

- 在 _ship_hit() 方法中，检查 self.stats.ships_left 是否大于 1 而不是大于 0，这样就不会多出一条生命。例如，你可以这样修改 _ship_hit() 方法：

```python
def _ship_hit(self):
    """响应飞船被外星人撞到"""
    if self.stats.ships_left > 1: # 将条件改为大于 1
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
```

外星人重叠问题
使用 pygame.sprite.spritecollide() 函数来检测外星人之间是否有碰撞，然后根据碰撞的结果来调整外星人的位置。使用一个循环来遍历外星人编组，然后使用 spritecollide() 函数来获取与当前外星人碰撞的其他外星人列表，然后根据列表的长度来判断是否需要重新生成位置。修改 _create_alien() 方法：

```python
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
        # 如果没有碰撞，跳出循环
        if len(collisions) == 0:
            overlap = False
    self.aliens.add(alien) # 将该实例添加到用于存储外星人群的编组中
```

这样就可以避免外星人重叠的问题，但是可能会影响性能，需要调整循环的次数或者使用其他的方法来优化。
但是还是有重叠的情况，不知道为什么
换了个方式pygame.sprite.spritecollide() 函数来实现的，它接受一个外星人对象和一个外星人编组作为参数，然后返回一个包含与该外星人对象碰撞的所有外星人的列表。可以参考 pygame 的官方文档。
但是我看到图片还是会重叠，可能是因为碰撞检测是基于外星人的 rect 属性来进行的，而不是基于图片的像素。rect 属性是一个矩形对象，它只包含外星人的位置和大小信息，而不包含图片的形状和透明度信息。
所以，图片有一些空白或者透明的部分，那么 rect 属性可能会比图片实际显示的部分要大一些，导致看起来像是重叠了。
需要使用 pygame.sprite.collide_mask() 函数来进行更精确的碰撞检测，它是基于外星人的 mask 属性来进行的，mask 属性是一个位图对象，它包含了图片的每个像素的信息，可以区分透明和不透明的部分。例如，你可以这样修改 spritecollide() 函数的调用：

```python
# 检测碰撞
collisions = pygame.sprite.spritecollide(alien, self.aliens, False, pygame.sprite.collide_mask)
```

这样就可以使用 mask 属性来检测碰撞，但是需要注意，这种方法也会消耗更多的资源。

感觉还是有重叠，我改回之前的检测方法，把外星人图片改成png格式了。偶尔有重叠，但是不是很明显，可以接受。
然后现在这样写它只能在第一次生成时不重叠，所以之后创建图像要在需要的地方用

**注意这里我没写哦**
```python
# 调用 _create_alien(self) 方法来创建并检测一个新的飞船
self._create_alien()
```

原本飞船下降方式是碰撞边框后下降，这样会导致一个问题，你想象一下，假如一群飞船，然后他们离边框特别近，就会很快的碰撞到边框，然后下降。
然后当飞机打到只有一个飞船时，他就下降的慢。
不过这个改不改都行，就是下降不匀速会让人觉得不适应，但是要说玩法就这样也不是不可以[捂脸]
改变飞船下降的方式，让它不是碰撞边框才下降，而是根据一定的条件来下降。根据搜索结果，使用 pygame.time.Clock() 类来创建一个时钟对象，然后使用它的 tick() 方法来控制游戏的帧率和时间流逝。使用 pygame.time.get_ticks() 函数来获取当前的时间毫秒数，然后使用一个变量来存储上一次下降的时间，然后根据两者的差值来判断是否需要下降。修改 AlienInvasion 类的 __init__() 和 run_game() 方法：

```python
class AlienInvasion:
    """管理游戏资源和行为的类"""
    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init() # 初始化背景设置
        self.settings = Settings()
        # 全屏模式下运行游戏
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion") # 设置屏幕标题
        # 创建存储游戏统计信息的实例
        # 并创建记分牌
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self) # 在创建屏幕后创建一个 Ship 实例，并将当前的 AlienInvasion 实例作为参数
        self.bullets = pygame.sprite.Group() # 创建一个编组，用于存储所有有效的子弹
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
            # 设置游戏的帧率为 60 帧/秒
            self.clock.tick(60)
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
```
这样就可以让飞船每隔一定的时间就下降并改变方向，而不是碰撞边框才下降。你可以根据你的需要修改 tick() 方法和 if 语句中的值，来调整游戏的速度和难度。

所以现在还有几个问题
1. 现在让它按照时间下降后，在游戏未开始时外星人也在下降。但实际上应该是游戏开始后才下降。不过这外星人就算这时下降到底了也不会游戏失败，还是要点击play后，外星人会重新在屏幕上方出现
2. 就是好像没看到暂停方法，设计一个暂停方法，最好加上友好性提示
3. 现在飞船还是和原来一样，是一批一批生成的，如果按照市面上的飞机大战，最好还是一边打一边生成
4. 游戏不会随着进度越来越快，可以按照需要设计一个难度递增的方法
5. 话说这游戏是全屏的，会不会有人屏幕很小，只能容得下一个飞机的宽度啊，直接按空格就行，哈哈哈哈哈