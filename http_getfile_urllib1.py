#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Еще раз о пакете urllib.
# Пример 13.30 (Лутц Т2 стр.300)
"""
# ---------------------------------------------------------------------------- #
получает файл с сервера HTTP (web) через сокеты с помощью модуля urllib;
urllib поддерживает протоколы HTTP, FTP, HTTPS и обычные файлы в строках
адресов URL; для HTTP в строке URL можно указать имя файла или удаленного
сценария CGI; смотрите также пример использования urllib в разделе FTP
и вызов сценария CGI в последующей главе; Python позволяет получать файлы
из сети самыми разными способами, различающимися сложностью и требованиями
к серверам: через сокеты, FTP, HTTP, urllib и вывод CGI;
предостережение: имена файлов следует обрабатывать функцией
urllib.parse.quote, чтобы экранировать специальные символы,
если это не делается в программном коде, - смотрите следующие главы;
# ---------------------------------------------------------------------------- #
"""

import sys
from urllib.request import urlopen

showlines = 6

try:
	servername, filename = sys.argv[1:]
except:
	servername, filename = 'learning-python.com', '/index.html'

remoteaddr = 'http://%s%s' % (servername, filename)

print(remoteaddr)
remotefile = urlopen(remoteaddr)						# объект файла для ввода
remotedata = remotefile.readlines()						# чтение данных напрямую
remotefile.close()
for line in remotedata[:showlines]:						# строка bytes со встроенными символами \n
	print(line)