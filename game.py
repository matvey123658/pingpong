import pygame
import sys
import time
import random

pygame.init()

screen = pygame.display.set_mode((800, 600))  # Создание экрана игры размером 800x600
pygame.display.set_caption("Ping Pong")  # Название окна игры
clock = pygame.time.Clock()  # Создание объекта для управления временем

# Объекты игры
player_1 = pygame.Rect(10, 200, 10, 100)  # Ракетка игрока
computer = pygame.Rect(780, 200, 10, 100)  # Ракетка компьютера
ball = pygame.Rect(390, 290, 10, 10)  # Мяч

# Скорости движения
PADDLE_SPEED = 5  # Скорость ракетки игрока
BALL_SPEED_X = 5  # Скорость мяча по оси X
BALL_SPEED_Y = 5  # Скорость мяча по оси Y
AI_SPEED = 4  # Скорость ИИ

# Настройки сложности ИИ
PREDICTION_ACCURACY = 0.75  # Точность предсказания позиции мяча (0.75 — не идеальная)
REACTION_DELAY = 15  # Задержка реакции ИИ (чем больше, тем меньше шанс на мгновенную реакцию)
MISTAKE_CHANCE = 0.15  # Шанс ошибки ИИ (чем больше, тем чаще ИИ ошибается)

# Инициализация мяча
ball_dx = BALL_SPEED_X  # Направление мяча по оси X
ball_dy = BALL_SPEED_Y  # Направление мяча по оси Y

# Счёт
player_score = 0  # Счёт игрока
computer_score = 0  # Счёт компьютера
font = pygame.font.Font(None, 36)  # Шрифт для отображения счёта

# Переменные для ИИ
ai_target_y = 300  # Целевая позиция Y для ракетки ИИ
frames_since_direction_change = 0  # Количество кадров с момента изменения направления мяча
last_ball_direction = 1  # Направление последнего движения мяча
ai_movement_threshold = 2  # Порог, ниже которого ИИ не двигает свою ракетку

# Функция для предсказания положения мяча
def predict_ball_position():
    global frames_since_direction_change, last_ball_direction
    
    # Обновляем предсказание, если мяч движется к ИИ
    if ball_dx > 0:
        if last_ball_direction <= 0:  # Если мяч изменил направление
            frames_since_direction_change = 0
        last_ball_direction = ball_dx
        
        if frames_since_direction_change < REACTION_DELAY:  # Задержка реакции
            frames_since_direction_change += 1
            return computer.centery
        
        # Расчёт времени, за которое мяч дойдёт до ракетки ИИ
        time_to_paddle = (computer.x - ball.x) / ball_dx
        
        # Предсказание Y позиции мяча в момент его достижения ракетки
        predicted_y = ball.y + (ball_dy * time_to_paddle)
        
        # Внесение случайности в предсказание на основе сложности
        if random.random() < MISTAKE_CHANCE:
            predicted_y += random.randint(-50, 50)
        
        # Учёт отскоков мяча от верхней и нижней границы
        while predicted_y < 0 or predicted_y > 600:
            if predicted_y < 0:
                predicted_y = -predicted_y
            if predicted_y > 600:
                predicted_y = 1200 - predicted_y
        
        # Внесение погрешности в предсказание
        predicted_y = (predicted_y * PREDICTION_ACCURACY + 
                      computer.centery * (1 - PREDICTION_ACCURACY))
        
        return predicted_y
    
    # Если мяч уходит от ИИ, возвращаем случайное значение
    return 300 + random.randint(-50, 50)

# Функция для перезапуска мяча
def restart_ball():
    global ball_dx, ball_dy
    ball.center = (400, 300)  # Центр экрана
    ball_dx = BALL_SPEED_X * (-1 if ball_dx > 0 else 1)  # Разворот мяча по оси X
    ball_dy = BALL_SPEED_Y * (-1 if ball_dy > 0 else 1)  # Разворот мяча по оси Y
    return ball_dx, ball_dy

# Флаг для отслеживания перезапуска мяча
ball_resetting = False
reset_timer = 0

while True:
    clock.tick(60)  # Ограничение FPS до 60 кадров в секунду
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()  # Закрытие игры
            sys.exit()

    # Управление игроком
    keys = pygame.key.get_pressed()  # Получаем нажатые клавиши
    if keys[pygame.K_UP] and player_1.top > 0:  # Двигаем ракетку вверх
        player_1.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and player_1.bottom < 600:  # Двигаем ракетку вниз
        player_1.y += PADDLE_SPEED

    # Движение мяча
    if not ball_resetting:
        ball.x += ball_dx
        ball.y += ball_dy

        # Отскок мяча от верхней и нижней границы экрана
        if ball.top <= 0 or ball.bottom >= 600:
            ball_dy = -ball_dy

        # Действия ИИ
        target_y = predict_ball_position()  # Получаем предсказанную позицию мяча
        distance_to_target = abs(computer.centery - target_y)  # Расстояние до цели
        
        # Двигаем ракетку ИИ, если она не близка к цели
        if distance_to_target > ai_movement_threshold:
            move_speed = min(AI_SPEED, distance_to_target * 0.5)
            
            if computer.centery < target_y and computer.bottom < 600:
                computer.y += move_speed
            elif computer.centery > target_y and computer.top > 0:
                computer.y -= move_speed

        # Отскок мяча от ракеток
        if ball.colliderect(player_1) or ball.colliderect(computer):
            ball_dx = -ball_dx  # Разворачиваем мяч по оси X
            ball_dy += random.uniform(-1, 1)  # Добавляем случайность в траекторию мяча
            if abs(ball_dy) > BALL_SPEED_Y * 1.5:  # Контроль за скоростью мяча
                ball_dy = BALL_SPEED_Y * 1.5 * (1 if ball_dy > 0 else -1)

        # Гол: если мяч выходит за пределы экрана
        if ball.left <= 0:
            computer_score += 1  # Очко для компьютера
            ball_resetting = True
            reset_timer = pygame.time.get_ticks()  # Засекаем время перезапуска
        elif ball.right >= 800:
            player_score += 1  # Очко для игрока
            ball_resetting = True
            reset_timer = pygame.time.get_ticks()  # Засекаем время перезапуска
    else:
        # Двигаем мяч в том же направлении после перезапуска
        ball.x += ball_dx
        ball.y += ball_dy
        
        # Проверка времени перезапуска
        if pygame.time.get_ticks() - reset_timer > 1000:
            ball_dx, ball_dy = restart_ball()  # Перезапускаем мяч
            ball_resetting = False

    # Отрисовка
    screen.fill((0, 0, 0))  # Заливка фона чёрным
    pygame.draw.rect(screen, (255, 255, 255), player_1)  # Ракетка игрока
    pygame.draw.rect(screen, (255, 255, 255), computer)  # Ракетка компьютера
    pygame.draw.aaline(screen, (255, 255, 255), (400, 0), (400, 600))  # Центровая линия
    pygame.draw.ellipse(screen, (255, 255, 255), ball)  # Мяч

    # Отображение счёта
    score_text = font.render(f"{player_score} - {computer_score}", True, (255, 255, 255))
    screen.blit(score_text, (350, 20))  # Размещение счёта в верхней части экрана

    pygame.display.flip()  # Обновление экрана

pygame.quit()
sys.exit()
