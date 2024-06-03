import pygame
import sys
import math
import torch
import random
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import os
from collections import deque

# Глобальные константы
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (51,153,255)
RED = (255, 0, 0)
GAME_SPEED = 60

PLAYER_SPRITES = [f"player/player{i}.png" for i in range(1, 6)]
AGENT_SPRITES = [f"enemy/enemy{i}.png" for i in range(1, 6)]
BULLET_SPRITES = [f"bullets/bullet{i}.png" for i in range(1, 8)]
BACKGROUND_IMAGES = [f"backgrounds/background{i}.png" for i in range(1, 5)]
MODEL_FILES = [f"models/model{i}.pth" for i in range(1, 3)]

class Actor:
    def __init__(self, x, y, width, height, image_path):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def move(self, dx, dy):
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy
        if 0 <= new_x <= SCREEN_WIDTH - self.rect.width:
            self.rect.x = new_x
        if 0 <= new_y <= SCREEN_HEIGHT - self.rect.height:
            self.rect.y = new_y

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)


class Bullet:
    def __init__(self, x, y, angle, image_path):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.angle = angle
        self.speed = 10
        self.dx = math.cos(math.radians(self.angle)) * self.speed
        self.dy = -math.sin(math.radians(self.angle)) * self.speed

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)


class DQN(nn.Module):
    def __init__(self):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(42, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, 9)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


class Agent:
    def __init__(self):
        self.model = DQN()
        self.target_model = DQN()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = 0.0  # Устанавливаем epsilon в 0, чтобы отключить случайные действия
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 32
        self.target_update_freq = 10

    def act(self, state):
        state = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            action_values = self.model(state)
        return torch.argmax(action_values).item()

    def save(self, filename):
        torch.save(self.model.state_dict(), filename)

    def load(self, filename):
        if os.path.isfile(filename):
            self.model.load_state_dict(torch.load(filename))
            self.target_model.load_state_dict(self.model.state_dict())


def calculate_firing_solution(player_pos, player_vel, agent_pos, bullet_speed):
    px, py = player_pos
    vx, vy = player_vel
    ex, ey = agent_pos

    dx = px - ex
    dy = py - ey

    a = vx**2 + vy**2 - bullet_speed**2
    b = 2 * (dx * vx + dy * vy)
    c = dx**2 + dy**2

    discriminant = b**2 - 4*a*c
    if discriminant >= 0:
        t1 = (-b + math.sqrt(discriminant)) / (2*a)
        t2 = (-b - math.sqrt(discriminant)) / (2*a)
        t = max(t1, t2)
        if t > 0:
            return (px + vx * t, py + vy * t)
    return None


def display_message(screen, message, color, size, position):
    font = pygame.font.Font(None, size)
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=position)
    screen.blit(text, text_rect)


def main_menu():
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    background = pygame.image.load("backgrounds/background5.png")
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(background, (0, 0))

    pygame.display.set_caption("Смешарики VS Marvel(Dota 3)")

    while True:
        #screen.fill("backgrounds/background2.png")
        #display_message(screen, "Смешарики VS Marvel(Dota 3)", WHITE, 100, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        display_message(screen, "Нажмите Enter чтобы начать", BLACK, 50, (350, SCREEN_HEIGHT - 150))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    character_selection()

        pygame.display.flip()


def character_selection():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Выбор персонажа, пуль и фона")

    selected_player = 0
    selected_agent = 0
    selected_bullet = 0
    selected_background = 0
    selected_model = 0

    while True:
        screen.fill(BLUE)
        display_message(screen, "Выберите персонажей, пули, фон и нейросеть", BLACK, 50, (SCREEN_WIDTH // 2, 50))

        # Отображаем выбранные изображения
        screen.blit(pygame.transform.scale(pygame.image.load(PLAYER_SPRITES[selected_player]), (100, 100)), (100, 100))
        screen.blit(pygame.transform.scale(pygame.image.load(AGENT_SPRITES[selected_agent]), (100, 100)), (SCREEN_WIDTH - 200, 100))
        screen.blit(pygame.transform.scale(pygame.image.load(BULLET_SPRITES[selected_bullet]), (50, 50)), (SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 150))
        screen.blit(pygame.transform.scale(pygame.image.load(BACKGROUND_IMAGES[selected_background]), (200, 100)), (SCREEN_WIDTH // 2 - 100, 100))
        display_message(screen, MODEL_FILES[selected_model], BLACK, 30, (SCREEN_WIDTH // 2, 400))

        display_message(screen, "Игрок", BLACK, 30, (150, 250))
        display_message(screen, "Противник", BLACK, 30, (SCREEN_WIDTH - 150, 250))
        display_message(screen, "Пули", BLACK, 30, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        display_message(screen, "Задний фон", BLACK, 30, (SCREEN_WIDTH // 2, 250))
        display_message(screen, "Нейросеть", BLACK, 30, (SCREEN_WIDTH // 2, 350))

        display_message(screen, "Нажмите Enter чтобы начать", BLACK, 50, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game(PLAYER_SPRITES[selected_player], AGENT_SPRITES[selected_agent], BULLET_SPRITES[selected_bullet], BACKGROUND_IMAGES[selected_background], MODEL_FILES[selected_model])
                elif event.key == pygame.K_LEFT:
                    selected_player = (selected_player - 1) % len(PLAYER_SPRITES)
                elif event.key == pygame.K_RIGHT:
                    selected_player = (selected_player + 1) % len(PLAYER_SPRITES)
                elif event.key == pygame.K_UP:
                    selected_agent = (selected_agent - 1) % len(AGENT_SPRITES)
                elif event.key == pygame.K_DOWN:
                    selected_agent = (selected_agent + 1) % len(AGENT_SPRITES)
                elif event.key == pygame.K_w:
                    selected_bullet = (selected_bullet - 1) % len(BULLET_SPRITES)
                elif event.key == pygame.K_s:
                    selected_bullet = (selected_bullet + 1) % len(BULLET_SPRITES)
                elif event.key == pygame.K_a:
                    selected_background = (selected_background - 1) % len(BACKGROUND_IMAGES)
                elif event.key == pygame.K_d:
                    selected_background = (selected_background + 1) % len(BACKGROUND_IMAGES)
                elif event.key == pygame.K_q:
                    selected_model = (selected_model - 1) % len(MODEL_FILES)
                elif event.key == pygame.K_e:
                    selected_model = (selected_model + 1) % len(MODEL_FILES)

        pygame.display.flip()


def game(player_sprite, agent_sprite, bullet_sprite, background_image, model_file):
    ticks = 0

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Смешарики VS Marvel(Dota 3)")
    background = pygame.image.load(background_image)
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    player = Actor(50, SCREEN_HEIGHT // 2, 150, 150, player_sprite)  # Увеличиваем размер игрока
    agent_actor = Actor(SCREEN_WIDTH - 200, SCREEN_HEIGHT // 2, 150, 150, agent_sprite)  # Увеличиваем размер агента
    bullets = []
    agent_bullets = []

    player_hits = 0
    enemy_hits = 0

    prev_player_pos = (player.rect.centerx, player.rect.centery)

    agent = Agent()
    
    agent.load(model_file)

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    b_x = player.rect.centerx
                    b_y = player.rect.centery
                    dx = mouse_x - b_x
                    dy = mouse_y - b_y
                    angle = math.atan2(-dy, dx)
                    b_x += math.cos(angle) * 110
                    b_y -= math.sin(angle) * 110
                    bullets.append(Bullet(b_x, b_y, math.degrees(angle), bullet_sprite))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.move(0, -5)
        if keys[pygame.K_s]:
            player.move(0, 5)
        if keys[pygame.K_a]:
            player.move(-5, 0)
        if keys[pygame.K_d]:
            player.move(5, 0)

        player_pos = (player.rect.centerx, player.rect.centery)
        fps = clock.get_fps()
        if fps == 0:
            fps = 60  # Default to GAME_SPEED if fps is zero
        player_vel = ((player_pos[0] - prev_player_pos[0]) * GAME_SPEED / fps,
                      (player_pos[1] - prev_player_pos[1]) * GAME_SPEED / fps)
        prev_player_pos = player_pos

        if random.randint(0, 5) == 1:
            firing_solution = calculate_firing_solution(player_pos, player_vel, (agent_actor.rect.centerx, agent_actor.rect.centery), 10)
            if firing_solution:
                fx, fy = firing_solution
                dx = fx - agent_actor.rect.centerx
                dy = fy - agent_actor.rect.centery
                angle = math.atan2(-dy, dx)
                agent_bullets.append(Bullet(agent_actor.rect.centerx, agent_actor.rect.centery, math.degrees(angle), bullet_sprite))

        # Собираем состояние для агента
        # Максимально учитываем 19 пуль, каждая с двумя координатами
        bullets_coords = []
        for bullet in bullets[:19]:  # Максимум 19 пуль
            bullets_coords.extend([bullet.rect.x, bullet.rect.y])
        while len(bullets_coords) < 38:  # Дополняем нулями до 38 элементов (19 * 2)
            bullets_coords.extend([0, 0])

        state = np.array([agent_actor.rect.x, agent_actor.rect.y, player.rect.x, player.rect.y] + bullets_coords)

        # Делаем действие согласно модели агента
        action = agent.act(state)

        # Маппинг действия на движение
        actions_map = [(5, 0), (0, 5), (-5, 0), (0, -5), (5, 5), (-5, -5), (5, -5), (-5, 5), (0, 0)]
        agent_dx, agent_dy = actions_map[action]
        agent_actor.move(agent_dx, agent_dy)

        screen.fill(BLACK)
        screen.blit(background, (0, 0))
        player.draw(screen)
        agent_actor.draw(screen)

        for bullet in bullets:
            bullet.move()
            bullet.draw(screen)

            if bullet.rect.colliderect(agent_actor.rect):
                enemy_hits += 1
                bullets.remove(bullet)
                if enemy_hits == 50:
                    return game_over(screen, "Вы выиграли!", player_hits, enemy_hits)
            if bullet.rect.colliderect(player.rect):
                player_hits += 1
                bullets.remove(bullet)
                if player_hits == 50:
                    return game_over(screen, "Вы проиграли!", player_hits, enemy_hits)

        for bullet in agent_bullets:
            bullet.move()
            bullet.draw(screen)

            if bullet.rect.colliderect(player.rect):
                player_hits += 1
                agent_bullets.remove(bullet)
                if player_hits == 50:
                    return game_over(screen, "Вы проиграли!", player_hits, enemy_hits)

        bullets = [bullet for bullet in bullets if screen.get_rect().colliderect(bullet.rect)]
        agent_bullets = [bullet for bullet in agent_bullets if screen.get_rect().colliderect(bullet.rect)]

        # Отображаем счетчики попаданий
        display_message(screen, f"Попадания по игроку: {player_hits}", WHITE, 30, (150, 20))
        display_message(screen, f"Попадания по врагу: {enemy_hits}", WHITE, 30, (SCREEN_WIDTH - 150, 20))

        pygame.display.flip()
        clock.tick(GAME_SPEED)

        prev_player_pos = player_pos
        ticks += 1


def game_over(screen, message, player_hits, enemy_hits):
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    background = pygame.image.load("backgrounds/finish.png")
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(background, (0, 0))

    while True:
        if (message == "Вы выиграли!"):
            display_message(screen, message, GREEN, 100, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        else:
            display_message(screen, message, RED, 100, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        display_message(screen, f"Попадания по игроку: {player_hits}", WHITE, 50, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        display_message(screen, f"Попадания по врагу: {enemy_hits}", WHITE, 50, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        display_message(screen, "Нажмите Enter, чтобы вернуться в главное меню", WHITE, 50, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
        display_message(screen, "Спасибо за игру", WHITE, 30, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        display_message(screen, "Поставьте пожалуйста зачёт", WHITE, 30, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    main_menu()

        pygame.display.flip()


if __name__ == "__main__":
    main_menu()
