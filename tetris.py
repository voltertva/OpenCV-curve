import curses
import random
import time

BOARD_WIDTH = 10
BOARD_HEIGHT = 20
TICK_RATE = 0.5

SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
]


def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]


def new_piece():
    shape = random.choice(SHAPES)
    x = BOARD_WIDTH // 2 - len(shape[0]) // 2
    y = 0
    return shape, x, y


def valid_position(board, shape, x, y):
    for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
            if cell:
                board_x = x + col_idx
                board_y = y + row_idx
                if board_x < 0 or board_x >= BOARD_WIDTH:
                    return False
                if board_y < 0 or board_y >= BOARD_HEIGHT:
                    return False
                if board[board_y][board_x]:
                    return False
    return True


def lock_piece(board, shape, x, y):
    for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
            if cell:
                board[y + row_idx][x + col_idx] = 1


def clear_lines(board):
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    cleared = BOARD_HEIGHT - len(new_board)
    for _ in range(cleared):
        new_board.insert(0, [0] * BOARD_WIDTH)
    return new_board, cleared


def draw(stdscr, board, shape, x, y, score):
    stdscr.clear()
    stdscr.addstr(0, 0, "Tetris (arrows to move/rotate, q to quit)")
    stdscr.addstr(1, 0, f"Score: {score}")

    for row_idx in range(BOARD_HEIGHT):
        stdscr.addstr(row_idx + 3, 0, "|")
        for col_idx in range(BOARD_WIDTH):
            cell = board[row_idx][col_idx]
            char = "#" if cell else " "
            if y <= row_idx < y + len(shape) and x <= col_idx < x + len(shape[0]):
                if shape[row_idx - y][col_idx - x]:
                    char = "@"
            stdscr.addstr(row_idx + 3, col_idx + 1, char)
        stdscr.addstr(row_idx + 3, BOARD_WIDTH + 1, "|")

    stdscr.addstr(BOARD_HEIGHT + 3, 0, "+" + "-" * BOARD_WIDTH + "+")
    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
    shape, x, y = new_piece()
    score = 0
    last_tick = time.time()

    while True:
        draw(stdscr, board, shape, x, y, score)
        key = stdscr.getch()

        if key in (ord("q"), ord("Q")):
            break
        if key == curses.KEY_LEFT and valid_position(board, shape, x - 1, y):
            x -= 1
        elif key == curses.KEY_RIGHT and valid_position(board, shape, x + 1, y):
            x += 1
        elif key == curses.KEY_DOWN and valid_position(board, shape, x, y + 1):
            y += 1
        elif key == curses.KEY_UP:
            rotated = rotate(shape)
            if valid_position(board, rotated, x, y):
                shape = rotated

        if time.time() - last_tick > TICK_RATE:
            if valid_position(board, shape, x, y + 1):
                y += 1
            else:
                lock_piece(board, shape, x, y)
                board, cleared = clear_lines(board)
                score += cleared * 100
                shape, x, y = new_piece()
                if not valid_position(board, shape, x, y):
                    stdscr.addstr(BOARD_HEIGHT // 2, 2, "Game Over")
                    stdscr.nodelay(False)
                    stdscr.getch()
                    break
            last_tick = time.time()


if __name__ == "__main__":
    curses.wrapper(main)
