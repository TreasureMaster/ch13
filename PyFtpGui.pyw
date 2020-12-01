#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Передача файлов с помощью ftplib.
# Добавляем пользовательский интерфейс.
# Пример 13.9 (Лутц Т2 стр.143)
"""
# ---------------------------------------------------------------------------- #
запускает графические интерфейсы получения и отправки по FTP независимо
от каталога, в котором находиться сценарий; сценарий не обязательно
должен находиться в os.getcwd; может также жестко определить путь
в $PP4EHOME или guessLocation; можно было бы также так: [from PP4E.launchmodes
import PortableLauncher, PortableLauncher('getfilegui', '%s/getfilegui.py' %
mydir)()], но в Windows понадобилось бы всплывающее окно DOS для вывода
сообщений о состоянии, описывающих выполняемые операции;
# ---------------------------------------------------------------------------- #
"""

import os, sys

print('Running in: ', os.getcwd())

# PP3E
# from PP4E.Launcher import findFirst
# mydir = os.path.split(findFirst(os.curdir, 'PyFtpGui.pyw'))[0]

# PP4E
from Tom1.ch06.find import findlist
mydir = os.path.dirname(findlist('PyFtpGui.pyw', startdir=os.curdir)[0])

if sys.platform[:3] == 'win':
	os.system('start %s\getfilegui.py' % mydir)
	os.system('start %s\putfilegui.py' % mydir)
else:
	os.system('python3 %s/getfilegui.py' % mydir)
	os.system('python3 %s/putfilegui.py' % mydir)