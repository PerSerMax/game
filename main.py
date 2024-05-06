import pygame
import sys
import math
import random

# Определяем размеры экрана
SCREEN_WIDTH = 800 #ПИСИК У МАКСИМА В ПОПЕ
SCREEN_HEIGHT = 600
# Определяем цвета
WHITE = (255, 255, 255) #максим альтушка
BLACK = (0, 0, 0)
RED = (255, 0, 0)


class Actor:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def move(self, dx, dy):
        # Перемещаем персонажа на указанное смещение
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy
        if 0 <= new_x <= SCREEN_WIDTH - self.rect.width:
            self.rect.x = new_x
        if 0 <= new_y <= SCREEN_HEIGHT - self.rect.height:
            self.rect.y = new_y

    def draw(self, screen):
        # Рисуем персонажа на экране
        pygame.draw.rect(screen, self.color, self.rect)


class Bullet:
    def __init__(self, x, y, angle):
        self.rect = pygame.Rect(x, y, 5, 5)
        self.color = RED
        self.angle = angle
        self.speed = 10
        self.dx = math.cos(math.radians(self.angle)) * self.speed
        self.dy = -math.sin(math.radians(self.angle)) * self.speed

    def move(self):
        # Перемещаем пулю в соответствии с углом
        self.rect.x += self.dx
        self.rect.y += self.dy

    def draw(self, screen):
        # Рисуем пулю на экране
        pygame.draw.rect(screen, self.color, self.rect)

def game():
    ticks = 0

    pygame.init()

    # Создаем экран
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Управление WASD и стрельба")

    # Создаем персонажа
    player = Actor(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 50, 50, WHITE)

    # Создаем второго актера (врага)
    enemy = Actor(100, 100, 50, 50, RED)

    # Список для хранения пуль
    bullets = []

    player_hits = 0  # Переменная для подсчета попаданий по игроку
    enemy_hits = 0   # Переменная для подсчета попаданий по врагу

    clock = pygame.time.Clock()


    while True:

        if ticks % 20www

        # Обрабатываем нажатия клавиш и перемещаем персонажа
        if keys[pygame.K_w]:
            player.move(0, -5)
        if keys[pygame.K_s]:
            player.move(0, 5)
        if keys[pygame.K_a]:
            player.move(-5, 0)
        if keys[pygame.K_d]:
            player.move(5, 0)

        # Очищаем экран
        screen.fill(BLACK)

        # Рисуем персонажей
        player.draw(screen)
        enemy.draw(screen)

        # Обновляем пули и проверяем столкновения
        for bullet in bullets:
            bullet.move()
            bullet.draw(screen)

            # Проверяем столкновение с игрокомw
            if bullet.rect.colliderect(player.rect):
                enemy_hits += 1
                # Дополнительная обработка, например, уменьшение здоровья и т.д.
                bullets.remove(bullet)
                if enemy_hits == 100:
                    pygame.quit()
                    return enemy_hits - player_hits
                print(player_hits, ":", enemy_hits)

            # Проверяем столкновение с врагом
            if bullet.rect.colliderect(enemy.rect):
                player_hits += 1
                # Дополнительная обработка, например, уменьшение здоровья и т.д.
                bullets.remove(bullet)
                if player_hits == 100:
                    pygame.quit()
                    return enemy_hits - player_hits
                print(player_hits, ":", enemy_hits)

        # Удаляем пули, которые вышли за пределы экрана
        bullets = [bullet for bullet in bullets if screen.get_rect().colliderect(bullet.rect)]

        # Обновляем
        pygame.display.flip()


        clock.tick(60)
        ticks += 1



if __name__ == "__main__":
    game()
