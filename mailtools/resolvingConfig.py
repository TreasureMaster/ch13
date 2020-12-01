#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Вспомогательный пакет mailtools.
# Сценарий выбора конфигурационного файла.
"""
# ---------------------------------------------------------------------------- #
программа используется только для выбора загрузки конфигурационного файла;
True - выполняется загрузка конфигурации для сервера локальной сети,
False - выполняется загрузка конфигурации для внешнего сервера
# ---------------------------------------------------------------------------- #
"""

import sys, os
# '..' - для сценария самотестирования mailtools
# sys.path.insert(0, os.path.abspath('..'))
# '.' - для директории запуска файла
# sys.path.insert(0, os.path.abspath('.'))

# print(sys.path)

localserver = True
try:
	mailconfig = __import__('maillocal') if localserver else __import__('mailconfig')
except ModuleNotFoundError:
	print('module not founded; try found in other dirs')
	# print('spec name:', __spec__)
	# print('parent name:', __spec__.parent)
	# print('full path name:', __spec__.origin)
	# print(__spec__.__dict__)
	package = os.path.split(__spec__.origin)[0]
	if package not in sys.path:
		sys.path.insert(0, package)
	parent = os.path.split(package)[0]
	if parent not in sys.path:
		sys.path.insert(0, parent)
	mailconfig = __import__('maillocal') if localserver else __import__('mailconfig')
print('config path:', mailconfig.__file__)