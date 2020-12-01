#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# HTTP: доступ к веб-сайтам.
# Пример 13.29 (Лутц Т2 стр.296)
"""
# ---------------------------------------------------------------------------- #
получает файл с сервера HTTP (web) через сокеты с помощью модуля http.client;
параметр с именем файла может содержать полный путь к каталогу и быть именем
любого сценария CGI с параметрами запроса в конце,
отделяемыми символом ?, для вызова удаленной программы; содержимое
полученного файла или вывод удаленной программы можно сохранить
в локальном файле, имитируя поведение FTP, или анализировать
с помощью модуля str.find или html.parser; смотрите также описание
метода http.client request(method, url, body=None, hdrs={});
# ---------------------------------------------------------------------------- #
"""

import sys, http.client

showlines = 6

try:
	servername, filename = sys.argv[1:]
except:
	servername, filename = 'learning-python.com', '/index.html'

print(servername, filename)
server = http.client.HTTPSConnection(servername)				# соединиться с HTTP-сервером
server.putrequest('GET', filename)								# отправить запрос и заголовки
server.putheader('Accept', 'text/html')							# можно также отправить запрос POST
server.endheaders()												# как и имена файлов сценариев CGI

reply = server.getresponse()									# прочитать заголовки + данные ответа
if reply.status != 200:											# код 200 означает успех
	print('Error sending request', reply.status, reply.reason)
else:
	data = reply.readlines()									# объект файла для получаемых данных
	reply.close()												# вывести строки с eoln в конце
	for line in data[:showlines]:								# чтобы сохранить, запишите в файл
		print(line)												# строки уже содержат \n, но являются строками bytes