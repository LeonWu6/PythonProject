# -*- coding: utf-8 -*-

from PIL import Image
import argparse


parser = argparse.ArgumentParser()  # 实例化对象
parser.add_argument('ImageFile')    # 定义第一个位置参数，当图片文件名作为第一个位置参数传入时，会存到实体中这个变量里
parser.add_argument('-o', '--output')   # 定义可选参数'-o'，当使用'-o'时，后同需要跟一个作为输出文件的文件名，解析后，会存放到output这个变量里
parser.add_argument('--width', type=int, default=80)    # 定义默认参数width，默认值为80，解析命令行合，存于width这个变量中
parser.add_argument('--height', type=int, default=80)   # 定义默认参数height，默认值为80
args = parser.parse_args()  # 开始解析命令行

ascii_char = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")
ascii_char_len = len(ascii_char)


def get_char(r, g, b, alpha=256):
    if alpha == 0:  # 如果alpha(透明度)值为零，说明是没有图片的位置，返回空字符
        rChar = " "
    gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)    # 将R,G,B值转化为灰度值的公式
    unit = (256.0+1)/ascii_char_len     # 0~256个值，一共是257个
    rChar = ascii_char[int(gray/unit)]
    return rChar


if __name__ == '__main__':
    im = Image.open(args.ImageFile)
    im = im.resize((args.width, args.height), Image.NEAREST)    # 参数含义：Image.NEAREST 低质量

    txt = ""
    for i in range(args.height):
        for j in range(args.width):
            txt += get_char(*im.getpixel((j, i)))   # getpixel()返回一个元素，包含R,G,B和alpha值，用*把序列中的每个元素，当作位置参数传进函数
        txt += '\n'
    print(txt)

    # 字符画输出到文件
    if args.output:
        with open(args.output, 'w') as f:
            f.write(txt)
    else:
        with open("output.txt", 'w') as f:
            f.write(txt)