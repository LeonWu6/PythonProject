# -*- coding:utf-8 -*-

import curses
from random import randrange, choice
from collections import defaultdict


letter_codes = [ord(c) for c in 'WASDRQwasdrq']
actions = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
actions_dict = dict(zip(letter_codes, actions * 2))


# 采用阻塞方式，等待有效按键的输入
def get_user_action(keyboard):
    ch = ''
    while ch not in actions_dict:
        ch = keyboard.getch()
    return actions_dict[ch]


# 矩阵的转置
def transpose(field):
    return [list(row) for row in zip(*field)]


# 矩阵的反转
def invert(field):
    return [row[::-1] for row in field]


class GameField:
    def __init__(self, width=4, height=4, win=2048):
        self.width = width
        self.height = height
        self.win_value = win
        self.score = 0
        self.highscore = 0
        self.reset()

    def reset(self):
        if self.highscore < self.score:
            self.highscore = self.score
        self.score = 0
        self.field = [[0 for i in range(self.width)] for j in range(self.height)]
        self.spawn()
        self.spawn()

    def spawn(self):    # 随机生成一个4或者2
        new_element = 4 if randrange(100) > 89 else 2
        (i,j) = choice([(i,j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
        self.field[i][j] = new_element

    def move(self, direction):
        def move_row_left(row):  # 用来对整行进行左移
            def tighten(row):   # 用于将每一行中非零的元素聚集在左边，右边用0填充
                new_row = [i for i in row if i != 0]
                new_row += [0 for i in range(len(row) - len(new_row))]
                return new_row

            def merge(row):  # 对邻近元素进行合并
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        new_row.append(2 * row[i])
                        self.score += 2 * row[i]
                        pair = False
                    else:
                        if i+1 < len(row) and row[i] == row[i + 1]:
                            pair = True
                            new_row.append(0)
                        else:
                            new_row.append(row[i])
                assert len(new_row) == len(row)
                return new_row
            return tighten(merge(tighten(row)))

        moves = { }
        moves['Left'] = lambda field: [move_row_left(row) for row in field]     # 每行左移
        moves['Right'] = lambda field: invert(moves['Left'](invert(field)))     # 倒序后向左移，再倒序回去
        moves['Up'] = lambda field: transpose(moves['Left'](transpose(field)))  # 转置之后左移，再转回来
        moves['Down'] = lambda field: transpose(moves['Right'](transpose(field)))   # 转置之后右移，再转回来
        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False

    def move_is_possible(self, direction):
        def row_is_left_movable(row):   # 判断单行能不能左移
            def change(i):
                if row[i] == 0 and row[i+1] != 0:
                    return True
                if row[i] != 0 and row[i+1] == row[i]:
                    return True
                return False
            return any(change(i) for i in range(len(row) - 1))

        check = {}
        check['Left'] = lambda field: any(row_is_left_movable(row) for row in field)
        check['Right'] = lambda field: check['Left'](invert(field))
        check['Up'] = lambda field: check['Left'](transpose(field))
        check['Down'] = lambda field: check['Right'](transpose(field))

        if direction in check:
            return check[direction](self.field)
        else:
            return False

    def is_win(self):
        return any(any(i >= self.win_value for i in row) for row in self.field)

    def is_gameover(self):
        return not any(self.move_is_possible(move) for move in actions)

    def draw(self, screen):
        help_string1 = '(W)Up (S)Down (A)Left (D)Right'
        help_string2 = '     (R)Restart (Q)Exit'
        gameover_string = '           GAME OVER'
        win_string = '          YOU WIN!'

        def cast(string):
            screen.addstr(string + '\n')

        def draw_hor_separator():
            line = '+-----' * 4 + '+'
            cast(line)

        def draw_row(row):
            cast(''.join('|{: ^5}'.format(num) if num > 0 else '|     ' for num in row) + '|')

        screen.clear()
        cast('SCORE: ' + str(self.score))  # 打印出分数 SCORE: 0
        if 0 != self.highscore:	 # 打印最高分 HIGHSCORE: 124
            cast('HIGHSCORE: ' + str(self.highscore))
        for row in self.field:
            draw_hor_separator()
            draw_row(row)
        draw_hor_separator()
        if self.is_win():  # 如果是赢了，画出赢字符串 ： YOU WIN!
            cast(win_string)
        else:				# 如果没赢
            if self.is_gameover():	    # 是不是gameover状态，画出gameover状态
                cast(gameover_string)
            else:					# 如果不是，画出 (W)Up (S)Down (A)Left (D)Right
                cast(help_string1)
        cast(help_string2)			# (R)Restart (Q)Exit


def main(stdscr):
    def init():     # 重置游戏
        game_field.reset()
        return 'Game'

    def not_game(state):    # state为Restart 和 Exit
        game_field.draw(stdscr)
        action = get_user_action(stdscr)
        responses = defaultdict(lambda: state)
        responses['Restart'], responses['Exit'] = 'Init', 'Exit'
        return responses[action]

    def game():
        game_field.draw(stdscr)
        action = get_user_action(stdscr)

        if action == 'Restart':
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        if game_field.move(action):     # 如果不是上面两种输入
            if game_field.is_win():     # 判断是不是赢了
                return 'Win'
            if game_field.is_gameover():
                return 'Gameover'
        return 'Game'

    state_actions = {
        'Init': init,
        'Win': lambda: not_game('Win'),
        'Gameover': lambda: not_game('Gameover'),
        'Game': game
    }

    # 设置终结状态最大数值为 32
    game_field = GameField(win=64)

    state = 'Init'

    while state != 'Exit':
        state = state_actions[state]()


curses.wrapper(main)
# 从源码可知，curses.wrapper()作了以下操作：
# initscr()--> noecho()--> cbreak()--> stdscr.keypad(1)--> start_color()--> return func(stdscr, *args, **kwds)
# 初始化--> 关闭自动回显--> 打开对按键立即反应--> enable return special key value--> 设置使用颜色--> 调用函数





