#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Передача файлов с помощью ftplib.
# Утилиты FTP get и put.
# Утилита загрузки.
# Пример 13.4 (Лутц Т2 стр.130)
"""
# ---------------------------------------------------------------------------- #
Загружает произвольный файл по FTP. Используется анонимный доступ к FTP,
если не указан кортеж user=(имя, пароль). В разделе самопроверки
используются тестовый FTP-сайт и файл.
# ---------------------------------------------------------------------------- #
"""

from ftplib import FTP							# инструменты FTP на основе сокета
from os.path import exists						# проверка наличия файла

def getfile(file, site, dir, user=(), *, verbose=True, refetch=False):
	"""
	загружает файл по FTP с сайта/каталога, используя анонимный доступ
	или действительную учетную запись, двоичный режим передачи
	"""
	if exists(file) and not refetch:
		if verbose: print(file, 'already fetched')
	else:
		if verbose: print('Downloading', file)
		local = open(file, 'wb')						# локальный файл с тем же именем
		try:
			remote = FTP(site)							# соединиться с FTP-сайтом
			remote.login(*user)							# для анонимного = () или исп-ся (имя, пароль)
			remote.cwd(dir)
			remote.retrbinary('RETR ' + file, local.write, 1024)
			remote.quit()
		finally:
			local.close()								# закрыть файл в любом случае
		if verbose: print('Downloading done.')			# исключения обрабатывает вызывающая программа


if __name__ == '__main__':
	from getpass import getpass
	file = 'spain08.jpg'
	dir = '.'
	site = 'GMP'
	user = ('combo', getpass('Pswd?'))
	getfile(file, site, dir, user)