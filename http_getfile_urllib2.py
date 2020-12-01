#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Еще раз о пакете urllib.
# Другие интерфейсы urllib.
# Пример 13.31 (Лутц Т2 стр.302)
"""
# ---------------------------------------------------------------------------- #
получает файл с сервера HTTP (web) через сокеты с помощью модуля urllib;
в этой версии использует интерфейс, сохраняющий полученные данные
в локальном файлы в двоичном режиме; имя локального файла передается
в аргументе командной строки или выделяется из URL посредством
модуля urllib.parse: аргмент с именем файла может содержить путь
к каталогу в начале и параметры запроса в конце, поэтому функции os.path.split
будет недостаточно (отделяет только путь к каталогу);
предостережение: имя файла следует обрабатывать функцией urllib.parse.quote,
если заранее неизвестно, что оно не содержит недопустимых символов -
смотрите следующие главы;
# ---------------------------------------------------------------------------- #
"""

import os, sys, urllib.request, urllib.parse

showlines = 6

try:
	servername, filename = sys.argv[1:3]					# первые 2 аргумента командной строки
except:
	servername, filename = 'learning-python.com', '/index.html'

remoteaddr = 'http://%s%s' % (servername, filename)			# любой адрес в сети

if len(sys.argv) == 4:										# получить имя файла
	localname = sys.argv[3]
else:
	(scheme, server, path, params, query, frag) = urllib.parse.urlparse(remoteaddr)
	localname = os.path.split(path)[1]

print(remoteaddr, localname)
urllib.request.urlretrieve(remoteaddr, localname)			# файл или сценарий
remotedata = open(localname, 'rb').readlines()				# сохранит в локальном файле
for line in remotedata[:showlines]:							# файл двоичный
	print(line)