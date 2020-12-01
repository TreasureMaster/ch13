#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Передача файлов с помощью ftplib.
# Использование пакета urllib для загрузки файлов.
# Пример 13.2 (Лутц Т2 стр.126)
"""
# ---------------------------------------------------------------------------- #
Сценарий на языке Python для загрузки файла по строке адреса URL;
вместо ftplib использует более высокоуровневый модуль urllib;
urllib поддреживает протоколы FTP, HTTP, HTTPS на стороне клиента,
локальные файлы, может работать с прокси-серверами, выполнять инструкции
перенаправления, принимать cookies и многое другое; urllib таже
позволяет загружать страницы html, изображения, текст и так далее;
смотрите также парсеры Python разметки html/xml веб-страниц,
получаемых с помощью urllib, в главе 19;
# ---------------------------------------------------------------------------- #
"""

import os, getpass
from urllib.request import urlopen						# веб-инструменты на основе сокетов

filename = 'spain08.jpg'								# имя удаленного/локального файла
password = getpass.getpass('Pswd?')

remoteaddr = 'ftp://combo:%s@GMP/%s;type=i' % (password, filename)
print('Downloading', remoteaddr)

# такой способ тоже работает (вместо 5 нижних строк)
# import urllib
# urllib.request.urlretrieve(remoteaddr, filename)

remotefile = urlopen(remoteaddr)						# возвращает объект типа файла для ввода
localfile = open(filename, 'wb')						# локальный фал для сохранения данных
localfile.write(remotefile.read())
localfile.close()
remotefile.close()