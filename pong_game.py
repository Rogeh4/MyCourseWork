import pygame
import sys
import random
from collections import namedtuple

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Настройки игры
WIDTH, HEIGHT = 600, 400
BALL_RADIUS = 15  # Еще меньше мяч
PAD_WIDTH, PAD_HEIGHT = 8, 60  # Еще короче ракетка
PAD_DISTANCE = 0
HALF_PAD_WIDTH = PAD_WIDTH // 2
HALF_PAD_HEIGHT = PAD_HEIGHT // 2


class PongGame:
    def __init__(self):
        pygame.init()
        self.fps = pygame.time.Clock()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Pong RL made not by me')

        # Сложности
        self.difficulty_levels = {
            "easy": {"ball_speed": (4, 5), "paddle_speed": 5, "acceleration": 1.05},
            "medium": {"ball_speed": (3, 4), "paddle_speed": 7, "acceleration": 1.1},
            "hard": {"ball_speed": (4, 5), "paddle_speed": 9, "acceleration": 1.2}
        }
        self.current_difficulty = "hard"
        self.difficulty = self.difficulty_levels[self.current_difficulty]
        self.stepRes = StepResult = namedtuple('StepResult', ['state', 'reward', 'done', "ball_speed"])

        self.reset()

    def reset(self):
        self.paddle1_pos = [HALF_PAD_WIDTH + PAD_DISTANCE, HEIGHT // 2]  # Всегда стартуем из центра
        self.paddle2_pos = [WIDTH - HALF_PAD_WIDTH - PAD_DISTANCE, HEIGHT // 2]
        self.ball_pos = [WIDTH // 2, HEIGHT // 2]
        self.ball_vel = [0, 0]
        self.l_score = 0
        self.r_score = 0
        self.ball_init(random.choice([True, False]))
        self.hit_paddle1 = False
        self.scored = False
        self.last_ball_pos = self.ball_pos.copy()

    def ball_init(self, right):
        horz = random.randint(*self.difficulty["ball_speed"])
        vert = random.randint(1, self.difficulty["ball_speed"][1])
        self.ball_vel = [horz if right else -horz, -vert]

    def update_difficulty(self):
        if max(self.l_score, self.r_score) >= 10:
            self.current_difficulty = "hard"
        elif max(self.l_score, self.r_score) >= 5:
            self.current_difficulty = "medium"
        else:
            self.current_difficulty = "easy"
        self.difficulty = self.difficulty_levels[self.current_difficulty]

    def get_state(self):
        return [
            self.ball_pos[0],
            self.ball_pos[1],
            self.ball_vel[0],
            self.ball_vel[1],
            self.paddle1_pos[1]
        ]

    def step(self, action):
        self.update_difficulty()

        # Динамическая скорость ракетки
        base_speed = self.difficulty["paddle_speed"]
        speed = base_speed * (0.5 if self.hit_paddle1 else 1.0)

        # Плавное управление с инерцией
        if action == 1:  # Вверх
            self.paddle1_vel = -speed
        elif action == 2:  # Вниз
            self.paddle1_vel = speed
        else:
            self.paddle1_vel = 0  # Торможение

        # Применение скорости с ограничением
        new_pos = self.paddle1_pos[1] + self.paddle1_vel
        new_pos = max(HALF_PAD_HEIGHT, min(HEIGHT - HALF_PAD_HEIGHT, new_pos))
        self.paddle1_pos[1] = new_pos

        # Движение мяча
        self.ball_pos[0] += self.ball_vel[0]
        self.ball_pos[1] += self.ball_vel[1]

        # Коллизии мяча по y
        if  self.ball_pos[1] >= HEIGHT - BALL_RADIUS:
            self.ball_vel[1] *= -0.9
            self.ball_pos[1] = HEIGHT - BALL_RADIUS
        # редакция коллизий по y
        if self.ball_pos[1] <= BALL_RADIUS:
            self.ball_vel[1] *= -0.9
            self.ball_pos[1] = BALL_RADIUS

        # Проверка отбития левой ракеткой
        if (self.ball_pos[0] <= PAD_WIDTH + BALL_RADIUS and
                self.paddle1_pos[1] - HALF_PAD_HEIGHT <= self.ball_pos[1] <= self.paddle1_pos[1] + HALF_PAD_HEIGHT):
            self.ball_vel[0] *= -self.difficulty["acceleration"]
            self.ball_vel[1] = self.paddle1_vel
            self.hit_paddle1 = True
        elif self.ball_pos[0] <= 0:
            self.r_score += 1
            self.ball_init(True)
            self.scored = True

        # Проверка правой ракетки
        if (self.ball_pos[0] >= WIDTH - PAD_WIDTH - BALL_RADIUS and
                self.paddle2_pos[1] - HALF_PAD_HEIGHT <= self.ball_pos[1] <= self.paddle2_pos[1] + HALF_PAD_HEIGHT):
            self.ball_vel[0] *= -self.difficulty["acceleration"]
            self.ball_vel[1] = self.paddle2_vel
        elif self.ball_pos[0] >= WIDTH:
            self.l_score += 1
            self.ball_init(False)
            self.scored = True

        # Обработка действий игрока
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.paddle2_vel = -self.difficulty["paddle_speed"]
                elif event.key == pygame.K_DOWN:
                    self.paddle2_vel = self.difficulty["paddle_speed"]
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    self.paddle2_vel = 0

        # Обновление позиции правой ракетки
        if hasattr(self, 'paddle2_vel'):
            new_paddle2_y = self.paddle2_pos[1] + self.paddle2_vel
            self.paddle2_pos[1] = max(HALF_PAD_HEIGHT, min(HEIGHT - HALF_PAD_HEIGHT, new_paddle2_y))

        # Отрисовка
        self.window.fill(BLACK)
        pygame.draw.line(self.window, WHITE, [WIDTH // 2, 0], [WIDTH // 2, HEIGHT], 1)
        pygame.draw.circle(self.window, WHITE, [WIDTH // 2, HEIGHT // 2], 70, 1)

        pygame.draw.rect(self.window, GREEN,
                         (self.paddle1_pos[0] - HALF_PAD_WIDTH, self.paddle1_pos[1] - HALF_PAD_HEIGHT, PAD_WIDTH,
                          PAD_HEIGHT))
        pygame.draw.rect(self.window, GREEN,
                         (self.paddle2_pos[0] - HALF_PAD_WIDTH, self.paddle2_pos[1] - HALF_PAD_HEIGHT, PAD_WIDTH,
                          PAD_HEIGHT))
        pygame.draw.circle(self.window, [100, 0, 100], (int(self.ball_pos[0]), int(self.ball_pos[1])), BALL_RADIUS)

        font = pygame.font.SysFont("Comic Sans MS", 20)
        self.window.blit(font.render(f"Score {self.l_score}", True, (255, 255, 0)), (50, 20))
        self.window.blit(font.render(f"Score {self.r_score}", True, (255, 255, 0)), (470, 20))
        self.window.blit(font.render(f"Difficulty: {self.current_difficulty.capitalize()}", True, WHITE), (200, 20))

        pygame.display.update()
        self.fps.tick(60)

        # Система наград
        reward = 0

        # Награда за отбитие мяча
        if self.hit_paddle1:
            reward += 20
            self.hit_paddle1 = False

        # Штраф/награда за гол
        if self.scored:
            if self.r_score > self.l_score:
                reward -= 100
            else:
                reward += 100
            self.scored = False

        # Прогрессивный штраф за близость к краям
        # edge_distance = min(self.paddle1_pos[1] - HALF_PAD_HEIGHT,
        #                     HEIGHT - HALF_PAD_HEIGHT - self.paddle1_pos[1])
        # if edge_distance < 10:
        #     reward -= 10
        # elif edge_distance < 20:
        #     reward -= 5
        # elif edge_distance < 30:
        #     reward -= 2

        # Награда за движение к мячу
        paddle_center = self.paddle1_pos[1]
        ball_y = self.ball_pos[1]
        prev_ball_y = self.last_ball_pos[1]
        distance = abs(paddle_center - ball_y)
        prev_distance = abs(paddle_center - prev_ball_y)

        if distance < prev_distance:
            reward += 3
        else:
            reward -= 1

        # Награда за центральную позицию
        if HEIGHT // 2 - 30 <= paddle_center <= HEIGHT // 2 + 30:
            reward += 5
        elif HEIGHT // 2 - 60 <= paddle_center <= HEIGHT // 2 + 60:
            reward += 2

        # Сохраняем позицию мяча для следующего шага
        self.last_ball_pos = self.ball_pos.copy()

        # Проверка завершения эпизода со счетом
        if self.l_score >= 5:
            done = 'Left'
        elif self.r_score >= 5:
            done = 'Right'
        else:
            done = 0

        ball_speed = abs(self.ball_vel[0])+abs(self.ball_vel[1])
        return self.stepRes(state=self.get_state(), reward=reward, done=done, ball_speed=ball_speed)

    def discretize_state(self, state, bins=(12, 12, 10, 10, 30)):
        bounds = [
            (0, WIDTH),
            (0, HEIGHT),
            (-5, 5),
            (-5, 5),
            (0, HEIGHT)
        ]
        digitized = []
        for i in range(len(bins)):
            scale = (bounds[i][1] - bounds[i][0]) / bins[i]
            value = int(min(bins[i] - 1, max(0, (state[i] - bounds[i][0]) // scale)))
            digitized.append(value)
        return tuple(digitized)
