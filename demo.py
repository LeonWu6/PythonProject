# -*- coding:utf-8 -*-

import curses
from random import randrange, choice  # generate and place new tile
from collections import defaultdict

letter_codes = [ord(ch) for ch in 'WASDRQwasdrq']
actions = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
actions_dict = dict(zip(letter_codes, actions * 2))


def get_user_action(keyboard):    
    char = "N"
    while char not in actions_dict:    
        char = keyboard.getch()
    return actions_dict[char]


def transpose(field):
    return [list(row) for row in zip(*field)]
    """
	zip(*field) 把field各列元素解压，组成一个元组
	zip()返回的是一个对象，如果想要打印出来，可以用for
	ff = zip(*field)
	for i in ff:
	print (i)
	"""


def invert(field):
    return [row[::-1] for row in field]
    # row[::-1],从最后一个元素到第一个元素复制一遍，即倒序


class GameField(object):
    def __init__(self, height=4, width=4, win=2048):
        self.height = height
        self.width = width
        self.win_value = win
        self.score = 0
        self.highscore = 0
        self.reset()

    def reset(self):
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        self.field = [[0 for i in range(self.width)] for j in range(self.height)]
        self.spawn()
        self.spawn()

    def spawn(self):
        new_element = 4 if randrange(100) > 89 else 2
        (i,j) = choice([(i,j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
        self.field[i][j] = new_element

    def move(self, direction):
        def move_row_left(row):
            def tighten(row): # squeese non-zero elements together
                new_row = [i for i in row if i != 0]    # 将一row中非零的元素取出放于new_row
                new_row += [0 for i in range(len(row) - len(new_row))]  # 加上新的零元素，凑行一row
                return new_row	

            def merge(row):  # 对邻近元素进行合并
                pair = False
                new_row = []
                for i in range(len(row)):  # 用len()返回row无组的长度 i : 0 1 2 3
                    if pair:
                        new_row.append(2 * row[i])  # 把两个相邻且相同的元素合并，添加进new_row中
                        self.score += 2 * row[i]    # 加分
                        pair = False
                    else:
                        if i + 1 < len(row) and row[i] == row[i + 1]:   # row有两个相同元素且相邻的元素
                            pair = True
                            new_row.append(0)   # new_row列表添加0
                        else:
                            new_row.append(row[i])  # 如果没有两个相同且相邻元素，就把row[i]搬进new_row
                assert len(new_row) == len(row)  # 断言，当这个关键字后面条件为假时，程序自动崩溃并抛出AssertionError异常
                return new_row
            return tighten(merge(tighten(row)))  # 先挤到一块再合并再挤到一块

        moves = { }
        moves['Left'] = lambda field: [move_row_left(row) for row in field]
        moves['Right'] = lambda field: invert(moves['Left'](invert(field)))     # 向右移动，则是倒序后向左移，再倒序回去
        moves['Up'] = lambda field: transpose(moves['Left'](transpose(field)))  # 向上移动，转置之后左移，再转回来
        moves['Down'] = lambda field: transpose(moves['Right'](transpose(field)))   # 向下移动，则是转置之后右移，再转回来
        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False

    def is_win(self):	    # any()如果全部为false，则返回false,如果有一个为true，则返回true
        return any(any(i >= self.win_value for i in row) for row in self.field)

    def is_gameover(self):
        return not any(self.move_is_possible(move) for move in actions)

    def move_is_possible(self, direction):
        def row_is_left_movable(row): 
            def change(i):  # true if there'll be change in i-th tile
                if row[i] == 0 and row[i + 1] != 0:  # Move
                    return True     # 如果row[i+1]和row[i]两个有一个为0，就可以移动
                if row[i] != 0 and row[i + 1] == row[i]:  # Merge
                    return True     # 如果有两个相同的值相邻，则可以移动
                return False
            return any(change(i) for i in range(len(row) - 1))	    # 如果一行中有一个位置可移动，则可以移动

        check = { }
        check['Left'] = lambda field: any(row_is_left_movable(row) for row in field)    # 判断是不是有一可以左移
        check['Right'] = lambda field: check['Left'](invert(field))     # 右移是左移的反转
        check['Up'] = lambda field: check['Left'](transpose(field))
        check['Down'] = lambda field: check['Right'](transpose(field))

        if direction in check:
            return check[direction](self.field)
        else:
            return False

    def draw(self, screen):
        help_string1 = '(W)Up (S)Down (A)Left (D)Right'
        help_string2 = '     (R)Restart (Q)Exit'
        gameover_string = '           GAME OVER'
        win_string = '          YOU WIN!'

        def cast(string):
            screen.addstr(string + '\n') # 利用addstr()打印字符串

        def draw_hor_separator():	    # 画水平分界线
            line = '+' + ('+------' * self.width + '+')[1:]	# '+------+------+------+------+'
            #  为什么不直接写成“ line = '+------' * 4 + '+' ”
            separator = defaultdict(lambda: line)
            if not hasattr(draw_hor_separator, "counter"):
                draw_hor_separator.counter = 0
            cast(separator[draw_hor_separator.counter])
            draw_hor_separator.counter += 1

        def draw_row(row):	# 画行
            cast(''.join('|{: ^5} '.format(num) if num > 0 else '|      ' for num in row) + '|')
            # ^是居中显式，<是左对齐，>是右对齐； 上面表示居中显示，长度为5，用空格填充
            #  比如：'{:0>5} '.format(8)为右对齐；5表示长度为5，用0填弃：  ’00800‘
            #  冒号后面有一个空格，意思是空格填充；

        screen.clear()  # 清屏
        cast('SCORE: ' + str(self.score))  # 打印出分数 SCORE: 0
        if 0 != self.highscore: 	# 打印最高分 HIGHSCORE: 124
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
    def init():
        # 重置游戏棋盘
        game_field.reset()
        return 'Game'

    def not_game(state):
        # 画出 GameOver 或者 Win 的界面
        game_field.draw(stdscr)
        # 读取用户输入得到action，判断是重启游戏还是结束游戏
        action = get_user_action(stdscr)
        responses = defaultdict(lambda: state)
        # 创建一个字典对象，value默认为传入的state
        responses['Restart'], responses['Exit'] = 'Init', 'Exit'
        # key为'Restart'和'Exit'赋值为'Init'和'Exit'
        return responses[action]

    def game():
        # 画出当前棋盘状态
        game_field.draw(stdscr)
        # 读取用户输入得到action
        action = get_user_action(stdscr)

        if action == 'Restart':
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        if game_field.move(action): # move successful
            if game_field.is_win():
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

    curses.use_default_colors()

    # 设置终结状态最大数值为 32
    game_field = GameField(win=32)

    state = 'Init'

    # 状态机开始循环
    while state != 'Exit':
        state = state_actions[state]()


curses.wrapper(main)


