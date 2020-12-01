#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Передача файлов с помощью ftplib.
# Утилиты FTP get и put.
# Пример 13.3 (Лутц Т2 стр.128)
"""
# ---------------------------------------------------------------------------- #
Сценарий на языке Python для загрузки медиафайла по FTP и его проигрывания.
Использует getfile.py, вспомогательный модуль, инкапсулирующий
этап загрузки по FTP.
# ---------------------------------------------------------------------------- #
"""

import getfile as getfile
from getpass import getpass

filename = 'spain08.jpg'

# получить файл с помощью вспомогательного модуля
getfile.getfile(file=filename,
				site='GMP',
				dir='.',
				user=('combo', getpass('Pswd?')),
				refetch=True)

# остальная часть сценария осталась без изменений
if input('Open file?') in ['Y', 'y']:
	from Tom1.ch06.playfile import playfile
	playfile(filename)