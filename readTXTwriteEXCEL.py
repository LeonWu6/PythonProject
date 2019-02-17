# -*- coding:utf-8 -*-


# import xlrd
import xlwt


# 创建工作簿
workbook = xlwt.Workbook(encoding='utf-8')
# 创建sheet
data_sheet = workbook.add_sheet('demo', cell_overwrite_ok=True)
mfile = open("input.txt", "r")

for line in mfile:
	char_c = line.split(" ")[0]
	char_r = line.split(" ")[1]
	cinput = line.split(" ")[2]
	cinput.replace("\n", "")
	int_c = int(char_c)-1
	int_r = int(char_r)-1
	data_sheet.write(int_r, int_c, cinput)
	workbook.save('demo.xls')
	
	