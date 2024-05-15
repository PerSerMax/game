import pygame
import sys
import math
import random
from typing import List, Tuple, Union

# Определяем размеры экрана
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
# Определяем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

class Actor:
    def __init__(self, x: int, y: int, image: str):
        original_image = pygame.image.load(image)
        self.image = pygame.transform.scale(original_image, (50, 50))  # Уменьшаем размер до 50x50
        self.rect = self.image.get_rect(center=(x, y))

    def move(self, dx: int, dy: int):
        # Перемещаем персонажа на указанное смещение
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy
        if 0 <= new_x <= SCREEN_WIDTH - self.rect.width:
            self.rect.x = new_x
        if 0 <= new_y <= SCREEN_HEIGHT - self.rect.height:
            self.rect.y = new_y

    def draw(self, screen: pygame.Surface):
        # Рисуем персонажа на экране
        screen.blit(self.image, self.rect.topleft)

class Bullet:
    def __init__(self, shooter: Actor, x: int, y: int, angle: float, image: str):
        # Загружаем изображение пули и уменьшаем его размер
        original_image = pygame.image.load(image)
        self.image = pygame.transform.scale(original_image, (10, 10))  # Размер пули 10x10
        self.angle = angle
        self.rotated_image = pygame.transform.rotate(self.image, 90 - self.angle)  # Устанавливаем правильный угол поворота
        self.rect = self.rotated_image.get_rect(center=(x, y))
        self.speed = 3
        self.dx = math.cos(math.radians(self.angle)) * self.speed
        self.dy = -math.sin(math.radians(self.angle)) * self.speed
        self.shooter = shooter  # Ссылка на того, кто выпустил пулю

    def move(self):
        # Перемещаем пулю в соответствии с углом
        self.rect.x += self.dx
        self.rect.y += self.dy

    def draw(self, screen: pygame.Surface):
        # Рисуем пулю на экране
        screen.blit(self.rotated_image, self.rect.topleft)

class Game:
    def __init__(self):
        self.ticks = 0
        self.player_hits = 0
        self.enemy_hits = 0
        self.bullets: List[Bullet] = []

        # Создаем персонажа
        self.player = Actor(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, "player.png")

        # Создаем второго актера (врага)
        self.enemy = Actor(100, 100, "enemy.png")

        self.clock = pygame.time.Clock()

        self.speed = 5
        self.directions: List[Tuple[int, int]] = [
            (self.speed, 0), (0, self.speed), (-self.speed, 0), (0, -self.speed),
            (self.speed, self.speed), (-self.speed, -self.speed),
            (self.speed, -self.speed), (-self.speed, self.speed)
        ]
        self.direction = random.choice(self.directions)

    def update_enemy(self):
        if self.ticks % 10 == random.randint(0, 10):
            self.direction = random.choice(self.directions)
        self.enemy.move(*self.direction)

        if random.randint(0, 30) == 1:
            self.shoot_bullet(self.enemy, self.player.rect.center, "bullet.png")

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Левая кнопка мыши
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.shoot_bullet(self.player, (mouse_x, mouse_y), "bullet.png", is_player=True)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.player.move(0, -5)
        if keys[pygame.K_s]:
            self.player.move(0, 5)
        if keys[pygame.K_a]:
            self.player.move(-5, 0)
        if keys[pygame.K_d]:
            self.player.move(5, 0)

    def shoot_bullet(self, shooter: Actor, target: Union[Actor, Tuple[int, int]], image: str, is_player: bool = False):
        if is_player:
            b_x, b_y = shooter.rect.center
        else:
            b_x = shooter.rect.centerx
            b_y = shooter.rect.centery

        if isinstance(target, Actor):
            dx = target.rect.centerx - b_x
            dy = target.rect.centery - b_y
        else:
            dx = target[0] - b_x
            dy = target[1] - b_y

        angle = math.degrees(math.atan2(-dy, dx))

        self.bullets.append(Bullet(shooter, b_x, b_y, angle, image))

    def update_bullets(self, screen: pygame.Surface):
        bullets_to_remove = []
        for bullet in self.bullets:
            bullet.move()
            bullet.draw(screen)

            if bullet.shooter != self.player and bullet.rect.colliderect(self.player.rect):
                self.enemy_hits += 1
                bullets_to_remove.append(bullet)
                if self.enemy_hits == 100:
                    self.end_game()
                    return

            if bullet.shooter != self.enemy and bullet.rect.colliderect(self.enemy.rect):
                self.player_hits += 1
                bullets_to_remove.append(bullet)
                if self.player_hits == 100:
                    self.end_game()
                    return

        self.bullets = [bullet for bullet in self.bullets if bullet not in bullets_to_remove and screen.get_rect().colliderect(bullet.rect)]

    def draw(self, screen: pygame.Surface):
        screen.fill(BLACK)
        self.player.draw(screen)
        self.enemy.draw(screen)
        self.update_bullets(screen)

        # Отображаем счетчик попаданий игрока (зеленый)
        font = pygame.font.Font(None, 36)
        player_hits_text = font.render(f"Player Hits: {self.player_hits}", True, (0, 255, 0))
        screen.blit(player_hits_text, (10, 10))

        # Отображаем счетчик попаданий врага (красный)
        enemy_hits_text = font.render(f"Enemy Hits: {self.enemy_hits}", True, (255, 0, 0))
        text_rect = enemy_hits_text.get_rect()
        text_rect.right = SCREEN_WIDTH - 10
        text_rect.top = 10
        screen.blit(enemy_hits_text, text_rect)

    def end_game(self):
        print(f"Final Score - Player: {self.player_hits}, Enemy: {self.enemy_hits}")
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    pygame.quit()
                    sys.exit()

def game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Управление WASD и стрельба")

    game_instance = Game()

    while True:
        game_instance.handle_input()
        game_instance.update_enemy()
        game_instance.draw(screen)
        pygame.display.flip()
        game_instance.clock.tick(60)
        game_instance.ticks += 1

if __name__ == "__main__":
    game()

