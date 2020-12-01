#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Передача файлов с помощью ftplib.
# Пример 13.1 (Лутц Т2 стр.121)
"""
# ---------------------------------------------------------------------------- #
Сценарий на языке Python для загрузки медиафайла по FTP и его проигрывания.
Использует модуль ftplib, реализующий поддержку протокола FTP на основе
сокетов. Протокол FTP использует 2 сокета (один для данных и один
для управления - на портах 20 и 21) и определяет форматы текстовых
сообщений, однако модуль ftplib скрывает большую часть деталей этого
протокола. Измените настройки в соответствии со своим сайтом/файлом.
# ---------------------------------------------------------------------------- #
"""

import os, sys
from getpass import getpass								# инструмент скрытого ввода пароля
from ftplib import FTP									# инструменты FTP на основе сокетов

nonpassive = False										# использовать активный режим FTP?
filename = 'spain08.jpg'								# загружаемый файл
dirname = '.'											# удаленный каталог, откуда загружается файл
sitename = 'GMP'										# FTP-сайт, к которому выполняется подключение
userinfo = ('combo', getpass('Pswd?'))					# () - для анонимного доступа
if len(sys.argv) > 1: filename = sys.argv[1]			# имя файла из командной строки?

print('Connecting...')
connection = FTP(sitename)								# соединиться с FTP-сайтом
connection.login(*userinfo)								# по умолчанию анонимный доступ
connection.cwd(dirname)									# передача порциями по 1 Кбайту
if nonpassive:											# использовать активный режим FTP, если этого требует сервер
	connection.set_pasv(False)

print('Downloading...')
localfile = open(filename, 'wb')						# локальный файл, куда сохраняются данные
connection.retrbinary('RETR ' + filename, localfile.write, 1024)
connection.quit()
localfile.close()

if input('Open file?') in ['Y', 'y']:
	from Tom1.ch06.playfile import playfile
	playfile(filename)