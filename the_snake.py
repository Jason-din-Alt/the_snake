from random import choice

import pygame as pg

# Константы для размеров поля и сетки
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Словарь обратных направлений
OPPOSITE_DIRECTIONS = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT
}

# Словарь для обработки ввода с клавиатуры
KEY_DIRECTION = {
    pg.K_UP: UP,
    pg.K_DOWN: DOWN,
    pg.K_LEFT: LEFT,
    pg.K_RIGHT: RIGHT,
    pg.K_w: UP,
    pg.K_s: DOWN,
    pg.K_a: LEFT,
    pg.K_d: RIGHT,
}
# Цвета
BOARD_BACKGROUND_COLOR = (220, 220, 220)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки
SPEED = 10

# Настройка игрового окна
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка (Для выхода нажмите Esc)')
clock = pg.time.Clock()

CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

ALL_CELLS = set(
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
)


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color=None) -> None:
        self.body_color = body_color
        self.position = None

    def draw(self):
        """Метод отрисовки, должен быть переопределен в дочерних классах."""
        raise NotImplementedError(
            f'Метод draw() не реализован в классе {type(self).__name__}'
        )

    def draw_cell(self, position, color=None, border_color=BORDER_COLOR):
        """Отрисовывает одну ячейку (сегмент) на поверхности."""
        draw_color = color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, draw_color, rect)
        if border_color is not None:
            pg.draw.rect(screen, border_color, rect, 1)

    def clear_cell(self, position):
        """Стираем одну ячейку (сегмент)."""
        self.draw_cell(
            position,
            color=BOARD_BACKGROUND_COLOR,
            border_color=None
        )


class Apple(GameObject):
    """Класс, яблоко."""

    def __init__(self, color=APPLE_COLOR, occupied_positions=None):
        super().__init__(body_color=color)
        positions_to_avoid = occupied_positions or []
        self.randomize_position(positions_to_avoid)

    def randomize_position(self, occupied_positions):
        """Размещает яблоко в случайной позиции на поле."""
        self.position = choice(tuple(ALL_CELLS - set(occupied_positions)))

    def draw(self):
        """Отрисовывает яблоко на экране."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс, представляющий змейку."""

    def __init__(self, color=SNAKE_COLOR):
        super().__init__(body_color=color)
        self.reset()

    def update_direction(self, new_direction):
        """Обновляет направление движения змейки."""
        if new_direction != OPPOSITE_DIRECTIONS[self.direction]:
            self.direction = new_direction

    def move(self):
        """Перемещает змейку на одну позицию."""
        head_x, head_y = self.positions[0]
        dx, dy = self.direction

        # Обработка выхода за границы (проход через стены)
        self.positions.insert(0, (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        ))
        # Удаляем последний сегмент и запоминаем его позицию в self.last
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает змейку на поверхности."""
        # Стираем старую позицию хвоста, если она есть
        if self.last:
            self.clear_cell(self.last)
            self.last = None

        # Отрисовываем только голову (она всегда новая)
        self.draw_cell(self.get_head_position())

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [CENTER_POSITION]
        self.direction = RIGHT
        self.last = None


def handle_keys(snake):
    """Обрабатывает события клавиатуры для управления змейкой."""
    for event in pg.event.get():
        if (event.type == pg.QUIT
                or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE)):
            pg.quit()
            raise SystemExit

        if event.type == pg.KEYDOWN:
            # Использование словаря для получения нового направления
            new_direction = KEY_DIRECTION.get(event.key)
            if new_direction:
                snake.update_direction(new_direction)


def main():
    """Основной игровой цикл."""
    pg.init()
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)

    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.move()

        head_pos = snake.get_head_position()

        # Проверка столкновения с яблоком
        if head_pos == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        # Проверка самостолкновения (пропускаем первые 4 сегмента - шею)
        elif head_pos in snake.positions[4:]:
            # Отрисовка объектов
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
            apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()

        pg.display.update()


if __name__ == '__main__':
    main()
